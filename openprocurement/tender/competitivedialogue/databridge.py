from gevent import monkey
monkey.patch_all()

from datetime import timedelta, datetime
try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

import logging
import logging.config
import os
import argparse

from retrying import retry
from uuid import uuid4

import gevent
from gevent.queue import Queue

from openprocurement_client.client import TendersClientSync, TendersClient
from openprocurement_client.client import ResourceNotFound
from yaml import load
from pytz import timezone
from lazydb import Db


TZ = timezone(os.environ['TZ'] if 'TZ' in os.environ else 'Europe/Kiev')


def get_now():
    return datetime.now(TZ)

logger = logging.getLogger("openprocurement.tender.competitivedialogue.databridge")
# logger = logging.getLogger(__name__)


db = Db('competitivedialogue_databridge_cache_db')


def generate_req_id():
    return b'competitivedialogue-data-bridge-req-' + str(uuid4()).encode('ascii')


class CompetitiveDialogueDataBridge(object):
    """ Competitive Dialogue Data Bridge """

    def __init__(self, config):
        super(CompetitiveDialogueDataBridge, self).__init__()
        self.config = config
        self.immortal_jobs = []
        self.jobs = []

        self.tenders_sync_client = TendersClientSync(
            '',
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'))

        self.client = TendersClient(
            self.config_get('api_token'),
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
        )

        self.initial_sync_point = {}
        self.tenders_queue = Queue(maxsize=500)
        self.handicap_second_setup_tender_queue = Queue(maxsize=500)
        self.new_tenders_put_queue = Queue(maxsize=500)
        self.new_tender_retry_put_queue = Queue(maxsize=500)

    def config_get(self, name):
        return self.config.get('main').get(name)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def get_tender_credentials(self, tender_id):
        """ Return credentials by tender id """
        self.client.headers.update({'X-Client-Request-ID': generate_req_id()})
        logger.info("Getting credentials for tender {}".format(tender_id), extra={"TENDER_ID": tender_id})
        data = self.client.extract_credentials(tender_id)
        logger.info("Got tender {} credentials".format(tender_id), extra={"TENDER_ID": tender_id})
        return data

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def initialize_sync(self, params=None, direction=None):
        # TODO use gevent.Event to wake up forward sync instead of checking
        # initial sync point
        if direction == "backward":
            assert params['descending']
            response = self.tenders_sync_client.sync_tenders(params,
                                                             extra_headers={'X-Client-Request-ID': generate_req_id()})
            # set values in reverse order due to 'descending' option
            self.initial_sync_point = {'forward_offset': response.prev_page.offset,
                                       'backward_offset': response.next_page.offset}
            logger.info("Initial sync point {}".format(self.initial_sync_point))
            return response
        elif not self.initial_sync_point:
            raise ValueError
        else:
            assert 'descending' not in params
            params['offset'] = self.initial_sync_point['forward_offset']
            logger.info("Starting forward sync from offset {}".format(params['offset']))
            return self.tenders_sync_client.sync_tenders(params,
                                                         extra_headers={'X-Client-Request-ID': generate_req_id()})

    def get_tenders(self, params=None, direction=""):
        """ Create never ended loop which monitoring tenders when status become complete return them """
        if params is None:
            params = {}
        response = self.initialize_sync(params=params, direction=direction)

        # While not last page and we have data
        while not (params.get('descending') and not
                   len(response.data) and
                   params.get('offset') == response.next_page.offset):
            tenders_list = response.data
            params['offset'] = response.next_page.offset

            delay = 101  # almost 2 minutes
            if tenders_list:  # if we have tender_list then next iteration should start after 15 seconds
                delay = 15
                logger.info("Client {} params: {}".format(direction, params))
            for tender in tenders_list:
                if tender['status'] in "complete" and \
                        tender['procurementMethodType'] in ["competitiveDialogue.aboveThresholdEU",
                                                            "competitiveDialogue.aboveThresholdUA"]:
                    logger.info('{} sync: Found tender in complete status {}'.format(direction.capitalize(),
                                                                                     tender['id']),
                                extra={"TENDER_ID": tender['id']})
                    yield tender
                else:
                    logger.debug('{} sync: Skipping tender {} in status {}'.format(direction.capitalize(),
                                                                                   tender['id'],
                                                                                   tender['status']),
                                 extra={"TENDER_ID": tender['id']})

            logger.info('Sleep {} sync...'.format(direction))
            gevent.sleep(delay)
            logger.info('Restore {} sync'.format(direction))
            logger.debug('{} {}'.format(direction, params))
            response = self.tenders_sync_client.sync_tenders(params,
                                                             extra_headers={'X-Client-Request-ID': generate_req_id()})

    def get_tender_data(self):
        """ Step 2 get small tender from tenders_queue, then get full tender, and copy to new dict """
        while True:
            try:
                tender_to_sync = self.tenders_queue.get()
                tender = self.tenders_sync_client.get_tender(
                    tender_to_sync['id'],
                    extra_headers={'X-Client-Request-ID': generate_req_id()})['data']
                db.put(tender_to_sync['id'], {'dateModified': tender_to_sync['dateModified']})
            except Exception, e:
                # If something happen put tender back to tenders_queue
                logger.exception(e)
                logger.info('Put dialog {0} back to tenders queue'.format(tender['id']),
                            extra={"DIALOG_ID": tender['id']})
                self.tenders_queue.put(tender_to_sync)
            else:
                if tender['status'] != 'complete':  # If tender which we get hasn't status complete
                    logger.warn('!!! dialog status not complete id {0}'.format(tender['id']),
                                extra={"DIALOG_ID": tender['id']})
                    continue
                try:
                    if not db.has(tender.get('TenderID')):  # check only for first time
                        self.client.get_tender(tender.get('TenderID'))
                    else:
                        logger.info('Tender from second step {0} exists in local db'.format(tender['id']),
                                    extra={"DIALOG_ID": tender['id']})
                        continue
                except ResourceNotFound:
                        logger.info('Sync dialog {0}'.format(tender['id']),
                                    extra={"DIALOG_ID": tender['id']})
                except Exception, e:
                    logger.exception(e)
                    logger.info('Put dialog {} back to tenders queue'.format(tender['id']), extra={"DIALOG_ID": tender['id']})
                    self.tenders_queue.put(tender)
                    break
                else:
                    # If we find tender form second stage, then, put him id to local base
                    db.put(tender['TenderID'], True)
                    logger.info('Tender from second step exists {}'.format(tender['TenderID']), extra={"DIALOG_ID": tender['id']})
                    continue

                # Create empty dict. and put information which we need for second stage
                new_tender = dict()
                new_tender['competitivedialogueID'] = tender['id']  # TODO: Here we must copy all that we need for new Tender
                new_tender['procurementMethodType'] = tender['procurementMethodType'].split('.')[-1]
                # required field for tender in draft status
                new_tender['items'] = tender['items']
                new_tender['title'] = tender['title']
                new_tender['minimalStep'] = tender['minimalStep']
                new_tender['value'] = tender['value']
                new_tender['procuringEntity'] = tender['procuringEntity']
                new_tender['items'] = tender['items']
                # new_tender['procurementMethod'] = ['selective'],
                if new_tender['procurementMethodType'] == 'aboveThresholdEU':
                    new_tender['title_en'] = tender['title_en']
                    new_tender['tenderPeriod'] = {'endDate': (get_now() + timedelta(days=31)).isoformat()}
                else:
                    new_tender['tenderPeriod'] = {'endDate': (get_now() + timedelta(days=16)).isoformat()}
                logger.info('Copying to new tender {}'.format(', '.join(['items', 'title', 'minimalStep',
                                                                         'value', 'procuringEntity', 'items'])),
                            extra={"TENDER_ID": tender['id']})

                self.handicap_second_setup_tender_queue.put(new_tender)

    def prepare_new_tender_data(self):
        """
          Step 3 get dict with params for our new tender, get extra information from dialog,
          And put updated tender dict to new_tenders_put_queue
        """
        while True:
            tender = self.handicap_second_setup_tender_queue.get()
            try:
                logger.info("Getting extra info from tender {}".format(tender['competitivedialogueID']),
                            extra={"DIALOG_ID": tender['competitivedialogueID']})
                tender_data = self.get_tender_credentials(tender['competitivedialogueID'])
            except Exception, e:  # If something happened put back to queue
                logger.exception(e)
                logger.info("Can't get tender credentials {}".format(tender['competitivedialogueID']),
                            extra={"DIALOG_ID": tender['competitivedialogueID']})
                self.handicap_second_setup_tender_queue.put(tender)
            else:
                logger.debug("Got extra info from tender {}".format(tender['competitivedialogueID']),
                             extra={"TENDER_ID": tender['competitivedialogueID']})
                data = tender_data.data
                if data.get('mode'):
                    tender['mode'] = data['mode']
                tender['owner'] = data['owner']
                tender['owner_token'] = data['tender_token']
                self.new_tenders_put_queue.put(tender)
            gevent.sleep(0)

    def put_new_tender(self):
        """
          Step 4 get dict with params for new tender and try create
        """
        while True:
            new_tender = self.new_tenders_put_queue.get()
            try:
                logger.info("Creating new tender for second step for dialog {0}".format(new_tender['competitivedialogueID']),
                            extra={"DIALOG_ID": new_tender['competitivedialogueID']})
                data = {"data": new_tender}
                res = self.client.create_tender(data)
                logger.info("Successfully created new tender for dialog tender {}".format(new_tender['competitivedialogueID']),
                            extra={"DIALOG_ID": new_tender['competitivedialogueID']})
                # self.client.patch_tender({'data': {'id': new_tender['competitivedialogueID'], 'TenderID': res['data']['id']}})
                db.put(res['data']['id'], True)
            except Exception, e:
                logger.exception(e)
                logger.info("Unsuccessful put new tender {0} for dialog ".format(new_tender['competitivedialogueID']),
                            extra={"DIALOG_ID": new_tender['competitivedialogueID']})
                logger.info("Schedule retry for dialog {0}".format(new_tender['competitivedialogueID']),
                            extra={"DIALOG_ID": new_tender['competitivedialogueID']})
                self.new_tender_retry_put_queue.put(new_tender)
            gevent.sleep(0)

    @retry(stop_max_attempt_number=15, wait_exponential_multiplier=1000 * 60)
    def _put_with_retry(self, tender):
        """
          Try create tender
        """
        try:
            data = {"data": tender}
            logger.info("Creating tender for dialog {}".format(tender['competitivedialogueID']),
                        extra={"DIALOG_ID": tender['competitivedialogueID']})
            self.client.create_tender(data)
        except Exception, e:
            logger.exception(e)
            raise

    def retry_put_tenders(self):
        """
          Step 5 If we didn't create new tender  from first time
        """
        while True:
            try:
                new_tender = self.new_tender_retry_put_queue.peek()
                self._put_with_retry(new_tender)
            except:
                new_tender = self.new_tender_retry_put_queue.get()
                logger.warn("Can't create tender for second stage {}".format(new_tender['competitivedialogueID']),
                            extra={"DIALOG_ID": new_tender['competitivedialogueID']})
            else:
                self.new_tender_retry_put_queue.get()
            gevent.sleep(0)

    def get_tenders_forward(self):
        """ From top list base get tenders which have status complete and put them to tenders_queue """
        logger.info('Start forward data sync worker...')
        params = {'opt_fields': 'status,lots,procurementMethodType', 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="forward"):
                logger.info('Forward sync: Put tender {} to process...'.format(tender_data['id']),
                            extra={"TENDER_ID": tender_data['id']})
                self.tenders_queue.put(tender_data)
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Forward worker died!')
            logger.exception(e)
        else:
            logger.warn('Forward data sync finished!')  # Should never happen!!!

    def get_tenders_backward(self):
        """
          Step 1 get tenders which in complete status and has right procurementMethodType,
          then push them to tenders_queue

        """
        logger.info('Start backward data sync worker...')
        params = {'opt_fields': 'status,lots,procurementMethodType', 'descending': 1, 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="backward"):
                # Check that tender was modified
                stored = db.get(tender_data['id'])
                if stored and stored['dateModified'] == tender_data['dateModified']:
                    logger.info('Tender {} not modified from last check. Skipping'.format(tender_data['id']), extra={"TENDER_ID": tender_data['id']})
                    continue
                logger.info('Backward sync: Put tender {} to process...'.format(tender_data['id']),
                            extra={"TENDER_ID": tender_data['id']})
                self.tenders_queue.put(tender_data)
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Backward worker died!')
            logger.exception(e)
        else:
            logger.info('Backward data sync finished.')

    def sync_single_tender(self, tender_id):
        """
          Get dialog by tender id and check if tender for second step exist, if not must create him
          :param tender_id: Id dialog model
        """
        try:
            logger.info("Getting dialog {}".format(tender_id))
            tender = self.tenders_sync_client.get_tender(tender_id)['data']
            logger.info("Got dialog {} in status {}".format(tender['id'], tender['status']))

            logger.info("Getting tender {} credentials".format(tender_id))
            tender_credentials = self.get_tender_credentials(tender_id)['data']
            logger.info("Got tender {} credentials".format(tender_id))

            if tender['status'] != 'complete':
                logger.info("Skip dialog {} in status {}".format(tender['id'], tender['status']))

            else:
                # TODO: model must have field TenderID
                logger.info("Checking if tender from second step {} already exists".format(tender['TenderID']))
                try:
                    self.tenders_sync_client.get_tender(tender['TenderID'])
                except ResourceNotFound:
                    new_tender = {}
                    logger.info('Tender from second step {} does not exists. Prepare for creation.'.format(tender['TenderID']))
                    logger.info('Extending dialog {} with extra data'.format(tender['id']))
                    if tender.get('mode'):
                        new_tender['mode'] = new_tender['mode']
                    # Here we must fill data for new tender
                    new_tender['dialog_id'] = tender['id']
                    new_tender['procuringEntity'] = tender['procuringEntity']
                    new_tender['owner'] = tender['owner']
                    new_tender['owner_token'] = tender_credentials['owner_token']
                    data = {"data": new_tender}
                    logger.info("Creating new tender")
                    response = self.client.create_tender(data)
                    assert 'data' in response
                    logger.info("tender {tender_id} created for dialog {dialog_id}".format(tender_id=response['data']['id'],
                                                                                           dialog_id=tender['id']))
                else:
                    logger.info('TenderID exists {}'.format(tender['TenderID']))

        except Exception, e:
            logger.exception(e)
            raise
        else:
            pass

    def run(self):
        logger.info('Start Competitive Dialogue Bridge')
        self.immortal_jobs = [
            gevent.spawn(self.get_tender_data),
            gevent.spawn(self.prepare_new_tender_data),
            gevent.spawn(self.put_new_tender),
            gevent.spawn(self.retry_put_tenders),
        ]
        while True:
            try:
                logger.info('Starting forward and backward sync workers')
                self.jobs = [
                    gevent.spawn(self.get_tenders_backward),   # Step 1 backward
                    gevent.spawn(self.get_tenders_forward),  # Step 1 forward
                ]
                gevent.joinall(self.jobs)
            except KeyboardInterrupt:
                logger.info('Exiting...')
                gevent.killall(self.jobs, timeout=5)
                break
            except Exception, e:
                logger.exception(e)

            logger.warn("Restarting synchronization")


def main():
    parser = argparse.ArgumentParser(description='Competitive Dialogue Data Bridge')
    parser.add_argument('config', type=str, help='Path to configuration file')
    parser.add_argument('--dialog', type=str, help='Dialog id to sync', dest="dialog_id")
    params = parser.parse_args()
    if os.path.isfile(params.config):
        with open(params.config) as config_file_obj:
            config = load(config_file_obj.read())
        logging.config.dictConfig(config)
        if params.dialog_id:
            CompetitiveDialogueDataBridge(config).sync_single_tender(params.dialog_id)
        else:
            CompetitiveDialogueDataBridge(config).run()
    else:
        logger.info('Invalid configuration file. Exiting...')


if __name__ == "__main__":
    main()
