from gevent import monkey

monkey.patch_all()

try:
    import urllib3.contrib.pyopenssl

    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

import logging
import logging.config
import os
import argparse
import copy

from datetime import timedelta, datetime
from retrying import retry
from uuid import uuid4

import gevent
from gevent.queue import Queue

from openprocurement_client.client import TendersClientSync, TendersClient
from yaml import load
from pytz import timezone
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.journal_msg_ids import (
    DATABRIDGE_RESTART, DATABRIDGE_GET_CREDENTIALS, DATABRIDGE_GOT_CREDENTIALS,
    DATABRIDGE_FOUND_MULTILOT_COMPLETE, DATABRIDGE_FOUND_NOLOT,
    DATABRIDGE_COPY_TENDER_ITEMS, DATABRIDGE_CD_PATCHED,
    DATABRIDGE_GET_EXTRA_INFO, DATABRIDGE_MISSING_CREDENTIALS,
    DATABRIDGE_GOT_EXTRA_INFO, DATABRIDGE_CREATE_NEW_TENDER,
    DATABRIDGE_TENDER_CREATED, DATABRIDGE_UNSUCCESSFUL_CREATE,
    DATABRIDGE_RETRY_CREATE, DATABRIDGE_CREATE_ERROR, DATABRIDGE_TENDER_PROCESS,
    DATABRIDGE_SKIP_NOT_MODIFIED, DATABRIDGE_SYNC_SLEEP, DATABRIDGE_SYNC_RESUME)

TZ = timezone(os.environ['TZ'] if 'TZ' in os.environ else 'Europe/Kiev')


def get_now():
    return datetime.now(TZ)


logger = logging.getLogger("openprocurement.tender.competitivedialogue.databridge")

from lazydb import Db

db = Db('competitivedialogue_databridge_cache_db')


def generate_req_id():
    return b'competitive-dialogue-data-bridge-req-' + str(uuid4()).encode('ascii')


def generate_id():
    return uuid4().hex


def journal_context(record={}, params={}):
    for k, v in params.items():
        record["JOURNAL_" + k] = v
    return record


def get_item_by_related_lot(items, lot_id):
    for item in items:
        if item['relatedLot'] == lot_id:
            return item


def get_lot_by_id(tender, lot_id):
    for lot in tender['lots']:
        if lot['id'] == lot_id:
            return lot


def get_bid_by_id(bids, bid_id):
    for bid in bids:
        if bid['id'] == bid_id:
            return bid


def generate_new_id_for_items(orig_tender):
    """
    Generate new item id for every item in tender
    :param orig_tender: competitive dialogue tender
    :return: None
    """
    for item in orig_tender['items']:
        item['id'] = generate_id()


def prepare_lot(orig_tender, lot_id, items):
    """
    Replace new id in lot and related items
    :param orig_tender: competitive dialogue tender
    :param lot_id: origin lot id
    :param items: list with related item for lot
    :return: lot with new id
    """
    item = get_item_by_related_lot(orig_tender['items'], lot_id)
    item['id'] = generate_id()
    item['relatedLot'] = generate_id()
    items.append(item)
    lot = get_lot_by_id(orig_tender, lot_id)
    lot['id'] = item['relatedLot']
    return lot


class CompetitiveDialogueDataBridge(object):
    """ Competitive Dialogue Data Bridge """

    def __init__(self, config):
        super(CompetitiveDialogueDataBridge, self).__init__()
        self.config = config

        self.tenders_sync_client = TendersClientSync(
            '',
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
        )

        self.client = TendersClient(
            self.config_get('api_token'),
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
        )

        self.initial_sync_point = {}
        self.tenders_queue = Queue(maxsize=500)
        self.handicap_tenders_queue = Queue(maxsize=500)
        self.new_tenders_put_queue = Queue(maxsize=500)
        self.new_tender_retry_put_queue = Queue(maxsize=500)

    def config_get(self, name):
        return self.config.get('main').get(name)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def get_tender_credentials(self, tender_id):
        self.client.headers.update({'X-Client-Request-ID': generate_req_id()})
        logger.info("Getting credentials for tender {}".format(tender_id),
                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_GET_CREDENTIALS},
                                          {"TENDER_ID": tender_id}))

        data = self.client.extract_credentials(tender_id)
        logger.info("Got tender {} credentials".format(tender_id),
                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_GOT_CREDENTIALS},
                                          {"TENDER_ID": tender_id}))
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

    def get_tenders(self, params, direction=""):
        response = self.initialize_sync(params=params, direction=direction)

        while not (params.get('descending') and not len(response.data) and params.get(
                'offset') == response.next_page.offset):
            tenders_list = response.data
            params['offset'] = response.next_page.offset

            delay = 101
            if tenders_list:
                delay = 15
                logger.info("Client {} params: {}".format(direction, params))
            for tender in tenders_list:
                if tender['status'] == 'active.stage2.waiting':
                    if hasattr(tender, "lots"):
                        if any([1 for lot in tender['lots'] if lot['status'] == "active"]):
                            logger.info('{} sync: Found multilot tender {} in status {}'.format(direction.capitalize(),
                                                                                                tender['id'],
                                                                                                tender['status']),
                                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_FOUND_MULTILOT_COMPLETE},
                                                              {"TENDER_ID": tender['id']}))
                            yield tender
                    else:
                        logger.info('{} sync: Found tender {}'.format(direction.capitalize(), tender['id']),
                                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_FOUND_NOLOT},
                                                          {"TENDER_ID": tender['id']}))
                        yield tender
                else:
                    logger.debug('{} sync: Skipping tender {} in status {}'.format(direction.capitalize(), tender['id'],
                                                                                   tender['status']),
                                 extra=journal_context(params={"TENDER_ID": tender['id']}))

            logger.info('Sleep {} sync...'.format(direction),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_SYNC_SLEEP}))
            gevent.sleep(delay)
            logger.info('Restore {} sync'.format(direction),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_SYNC_RESUME}))
            logger.debug('{} {}'.format(direction, params))
            response = self.tenders_sync_client.sync_tenders(params,
                                                             extra_headers={'X-Client-Request-ID': generate_req_id()})

    def get_competitive_dialogue_data(self):
        while True:
            try:
                tender_to_sync = self.tenders_queue.get()  # Get competitive dialogue which we want to sync
                tender = self.tenders_sync_client.get_tender(tender_to_sync['id'],
                                                             extra_headers={'X-Client-Request-ID': generate_req_id()})[
                    'data']  # Try get data by tender id
            except Exception, e:
                # If we have something problems then put tender back to queue
                logger.exception(e)
                logger.info('Put tender {} back to tenders queue'.format(tender_to_sync['id']),
                            logger.info('Put tender {} back to tenders queue'.format(tender_to_sync['id']),
                                        extra=journal_context(params={"TENDER_ID": tender_to_sync['id']})))
                self.tenders_queue.put(tender_to_sync)
            else:
                if db.has(tender['id']):
                    logger.info('Tender {} exists in local db'.format(tender['id']),
                                extra=journal_context(params={"TENDER_ID": tender['id']}))
                    continue
                logger.info('Copy tender data {} '.format(tender['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_COPY_TENDER_ITEMS},
                                                  {"TENDER_ID": tender['id']}))
                new_tender = dict(title_ru=tender['title_ru'], procurementMethod='selective')
                if tender['procurementMethodType'].endswith('EU'):
                    new_tender['procurementMethodType'] = STAGE_2_EU_TYPE
                    new_tender['title_en'] = tender['title_en']
                    new_tender['tenderPeriod'] = {'endDate': (get_now() + timedelta(days=31)).isoformat()}
                else:
                    new_tender['procurementMethodType'] = STAGE_2_UA_TYPE
                    new_tender['tenderPeriod'] = {'endDate': (get_now() + timedelta(days=16)).isoformat()}
                old_lots, items, short_listed_firms = dict(), list(), dict()
                for qualification in tender['qualifications']:
                    if qualification['status'] == 'active':  # check if qualification has status active
                        if qualification.get('lotID'):
                            if qualification['lotID'] not in old_lots:  # check if lot id in local dict with new lots
                                lot = prepare_lot(tender, qualification['lotID'], items)  # update lot with new id
                                old_lots[qualification['lotID']] = lot  # set new lot in local dict
                            bid = get_bid_by_id(tender['bids'], qualification['bidID'])
                            for bid_tender in bid['tenderers']:
                                if bid_tender['identifier']['id'] not in short_listed_firms:
                                    short_listed_firms[bid_tender['identifier']['id']] = {"name": bid_tender['name'],
                                                                                          "identifier": bid_tender['identifier'],
                                                                                          "lots": [{"id": old_lots[qualification['lotID']]['id']}]}
                                else:
                                    short_listed_firms[bid_tender['identifier']['id']]['lots'].append(
                                        {"id": old_lots[qualification['lotID']]['id']})
                        else:
                            generate_new_id_for_items(tender)
                            new_tender['items'] = copy.deepcopy(tender['items'])  # add all items, with new id
                            bid = get_bid_by_id(tender['bids'], qualification['bidID'])
                            for bid_tender in bid['tenderers']:
                                if bid_tender['identifier']['id'] not in short_listed_firms:
                                    short_listed_firms[bid_tender['identifier']['id']] = {"name": bid_tender['name'],
                                                                                          "identifier": bid_tender['identifier'],
                                                                                          "lots": []}
                if items:  # If we have lots, then add only related items
                    new_tender['items'] = items
                new_tender['lots'] = old_lots.values()
                new_tender['shortlistedFirms'] = short_listed_firms.values()

                new_tender['status'] = 'draft'
                new_tender['dialogueID'] = tender['id']
                new_tender['title'] = tender['title']
                new_tender['minimalStep'] = tender['minimalStep']
                new_tender['value'] = tender['value']
                new_tender['procuringEntity'] = tender['procuringEntity']
                self.handicap_tenders_queue.put(new_tender)

    def prepare_new_tender_data(self):
        while True:
            new_tender = self.handicap_tenders_queue.get()
            try:
                logger.info("Getting extra info for tender {0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_GET_EXTRA_INFO},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                tender_data = self.get_tender_credentials(new_tender['dialogueID'])
            except Exception, e:
                logger.exception(e)
                logger.info("Can't get tender credentials {0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_MISSING_CREDENTIALS},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                self.handicap_tenders_queue.put(new_tender)
            else:
                logger.debug("Got extra info for tender {}".format(new_tender['dialogueID']),
                             extra=journal_context({"MESSAGE_ID": DATABRIDGE_GOT_EXTRA_INFO},
                                                   {"TENDER_ID": new_tender['dialogueID']}))
                data = tender_data.data
                if data.get('mode'):
                    new_tender['mode'] = data['mode']
                new_tender['owner'] = data['owner']
                new_tender['dialogue_token'] = data['tender_token']
                self.new_tenders_put_queue.put(new_tender)
            gevent.sleep(0)

    def put_tender_stage2(self):
        """
        Create tender for stage 2
        """
        while True:
            new_tender = self.new_tenders_put_queue.get()
            try:
                logger.info("Creating new tender from dialog {}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_NEW_TENDER},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                data = {"data": new_tender}
                res = self.client.create_tender(data)

                logger.info("Successfully created tender second stage {} from dialogue {}".format(
                    res['data']['id'], res['data']['dialogueID']),
                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_CREATED},
                                          {"DIALOGUE_ID": res['data']['dialogueID'],
                                           "TENDER_ID": res['data']['id']}))
                # patch origin competitive dialogue - set tender id for stage 2 (field stage2TenderID) and set status to complete
                patch_data = {"data": {"id": res['data']['dialogueID'],
                                       "status": "complete",
                                       "stage2TenderID": res['data']['id']}}
                res_patch = self.client.patch_tender(patch_data)

                logger.info("Successfully patch competitive dialogue {}".format(
                    res['data']['dialogueID']),
                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_CD_PATCHED},
                                          {"DIALOGUE_ID": res['data']['dialogueID'],
                                           "TENDER_ID": res['data']['id']}))

                db.put(res['data']['dialogueID'], True)
            except Exception, e:
                logger.exception(e)
                logger.info("Unsuccessful put for new tender of tender {0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                logger.info("Schedule retry for tender {0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_RETRY_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                self.new_tender_retry_put_queue.put(new_tender)
            gevent.sleep(0)

    @retry(stop_max_attempt_number=15, wait_exponential_multiplier=1000 * 60)
    def _put_with_retry(self, new_tender):
        try:
            data = {"data": new_tender}
            logger.info("Creating new tender of tender {0}".format(new_tender['dialogueID']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_NEW_TENDER},
                                              {"TENDER_ID": new_tender['dialogueID']}))
            self.client.create_tender(data)
        except Exception, e:
            logger.exception(e)
            raise

    def retry_put_tender_stage2(self):
        while True:
            try:
                new_tender = self.new_tender_retry_put_queue.peek()
                self._put_with_retry(new_tender)
            except:
                tender = self.new_tender_retry_put_queue.get()
                del tender['tender_token']  # do not reveal tender credentials in logs
                logger.warn("Can't create new tender from tender {0}".format(tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_ERROR,
                                                   "TENDER_ID": tender['dialogueID']}))
            else:
                self.new_tender_retry_put_queue.get()
            gevent.sleep(0)

    def get_tender_forward(self):
        logger.info('Start forward data sync worker...')
        params = {'opt_fields': 'status,lots', 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="forward"):
                logger.info('Forward sync: Put tender {} to process...'.format(tender_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_PROCESS},
                                                  {"TENDER_ID": tender_data['id']}))
                self.tenders_queue.put(tender_data)
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Forward worker died!')
            logger.exception(e)
        else:
            logger.warn('Forward data sync finished!')  # Should never happen!!!

    def get_tender_backward(self):
        logger.info('Start backward data sync worker...')
        params = {'opt_fields': 'status,lots', 'descending': 1, 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="backward"):
                stored = db.get(tender_data['id'])
                if stored:
                    logger.info('Tender {} in local db. Skipping'.format(tender_data['id']),
                                extra=journal_context({"MESSAGE_ID": DATABRIDGE_SKIP_NOT_MODIFIED},
                                                      {"TENDER_ID": tender_data['id']}))
                    continue
                logger.info('Backward sync: Put tender {} to process...'.format(tender_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_PROCESS},
                                                  {"TENDER_ID": tender_data['id']}))
                self.tenders_queue.put(tender_data)
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Backward worker died!')
            logger.exception(e)
        else:
            logger.info('Backward data sync finished.')

    def run(self):
        logger.info('Start Competitive Dialogue Data Bridge')
        self.immortal_jobs = [
            gevent.spawn(self.get_competitive_dialogue_data),
            gevent.spawn(self.prepare_new_tender_data),
            gevent.spawn(self.put_tender_stage2),
            gevent.spawn(self.retry_put_tender_stage2),
        ]
        while True:
            try:
                logger.info('Starting forward and backward sync workers')
                self.jobs = [
                    gevent.spawn(self.get_tender_backward),
                    gevent.spawn(self.get_tender_forward),
                ]
                gevent.joinall(self.jobs)
            except KeyboardInterrupt:
                logger.info('Exiting...')
                gevent.killall(self.jobs, timeout=5)
                break
            except Exception, e:
                logger.exception(e)

            logger.warn("Restarting synchronization", extra=journal_context({"MESSAGE_ID": DATABRIDGE_RESTART}))


def main():
    """ Parse config and create bridge """
    parser = argparse.ArgumentParser(description='Competitive Dialogue Data Bridge')
    parser.add_argument('config', type=str, help='Path to configuration file')
    params = parser.parse_args()
    if os.path.isfile(params.config):
        with open(params.config) as config_file_obj:
            config = load(config_file_obj.read())
        logging.config.dictConfig(config)
        CompetitiveDialogueDataBridge(config).run()
    else:
        logger.info('Invalid configuration file. Exiting...')


if __name__ == "__main__":
    main()
