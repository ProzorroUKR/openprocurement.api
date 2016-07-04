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
from openprocurement.api.utils import generate_id
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.journal_msg_ids import (
    DATABRIDGE_RESTART, DATABRIDGE_GET_CREDENTIALS, DATABRIDGE_GOT_CREDENTIALS,
    DATABRIDGE_FOUND_NOLOT,
    DATABRIDGE_COPY_TENDER_ITEMS, DATABRIDGE_CD_PATCHED,
    DATABRIDGE_GET_EXTRA_INFO, DATABRIDGE_MISSING_CREDENTIALS,
    DATABRIDGE_GOT_EXTRA_INFO, DATABRIDGE_CREATE_NEW_TENDER,
    DATABRIDGE_TENDER_CREATED, DATABRIDGE_UNSUCCESSFUL_CREATE,
    DATABRIDGE_RETRY_CREATE, DATABRIDGE_CREATE_ERROR, DATABRIDGE_TENDER_PROCESS,
    DATABRIDGE_SKIP_NOT_MODIFIED, DATABRIDGE_SYNC_SLEEP, DATABRIDGE_SYNC_RESUME, DATABRIDGE_PATH_DIALOG,
    DATABRIDGE_UNSUCCESSFUL_PATH, DATABRIDGE_RETRY_PATH)

TZ = timezone(os.environ['TZ'] if 'TZ' in os.environ else 'Europe/Kiev')


logger = logging.getLogger("openprocurement.tender.competitivedialogue.databridge")

from lazydb import Db

db = Db('competitivedialogue_databridge_cache_db')


def generate_req_id():
    return b'competitive-dialogue-data-bridge-req-' + str(uuid4()).encode('ascii')


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
        self.dialog_path_queue = Queue(maxsize=500)
        self.dialog_retry_path_queue = Queue(maxsize=500)

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

        while not (params.get('descending') and not len(response.data) and params.get('offset') == response.next_page.offset):
            tenders_list = response.data
            params['offset'] = response.next_page.offset

            delay = 101
            if tenders_list:
                delay = 15
                logger.info("Client {} params: {}".format(direction, params))
            for tender in tenders_list:
                if tender['status'] == 'active.stage2.waiting':
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
                tender = self.tenders_sync_client.get_tender(
                    tender_to_sync['id'],
                    extra_headers={'X-Client-Request-ID': generate_req_id()})['data']  # Try get data by tender id
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
                if db.has('path_{dialog_id}'.format(dialog_id=tender['id'])):
                    logger.info('New stage for dialog {} exists. Need only path'.format(tender['id']),
                                extra=journal_context(params={"TENDER_ID": tender['id']}))
                    continue
                logger.info('Copy tender data {} '.format(tender['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_COPY_TENDER_ITEMS},
                                                  {"TENDER_ID": tender['id']}))
                new_tender = dict(title=tender['title'], procurementMethod='selective')
                if 'title_ru' in tender:
                    new_tender['title_ru'] = tender['title_ru']
                if tender.get('mode'):
                    new_tender['mode'] = tender['mode']
                if tender.get('procurementMethodDetails'):
                    new_tender['procurementMethodDetails'] = tender['procurementMethodDetails']
                if tender['procurementMethodType'].endswith('EU'):
                    new_tender['procurementMethodType'] = STAGE_2_EU_TYPE
                    new_tender['title_en'] = tender['title_en']
                else:
                    new_tender['procurementMethodType'] = STAGE_2_UA_TYPE

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
            logger.info("Creating new tender from dialog {}".format(new_tender['dialogueID']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_NEW_TENDER},
                                              {"TENDER_ID": new_tender['dialogueID']}))
            data = {"data": new_tender}
            try:
                res = self.client.create_tender(data)
            except Exception, e:
                logger.exception(e)
                logger.info("Unsuccessful put for new tender of tender {0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                logger.info("Schedule retry for tender {0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_RETRY_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                self.new_tender_retry_put_queue.put(new_tender)
            else:
                logger.info("Successfully created tender second stage {} from dialogue {}".format(
                    res['data']['id'], res['data']['dialogueID']),
                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_CREATED},
                                          {"DIALOGUE_ID": res['data']['dialogueID'],
                                           "TENDER_ID": res['data']['id']}))
                # Put data in queue for path dialog
                dialog = {"id": res['data']['dialogueID'],
                          "status": "complete",
                          "stage2TenderID": res['data']['id']}
                self.dialog_path_queue.put(dialog)
                # save dialog to local db
                db.put('path_{dialog_id}'.format(dialog_id=res['data']['dialogueID']), dialog)
                db.put(res['data']['dialogueID'], True)
            gevent.sleep(0)

    def path_dialog(self):
        """
        Patch origin competitive dialogue - set tender id for stage 2 (field stage2TenderID) and set status to complete
        """
        while True:
            dialog = self.dialog_path_queue.get()
            logger.info("Path dialog {}".format(dialog['id']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_PATH_DIALOG},
                                              {"TENDER_ID": dialog['id']}))

            patch_data = {"data": dialog}
            try:
                res_patch = self.client.patch_tender(patch_data)
            except Exception, e:
                logger.exception(e)
                logger.info("Unsuccessful path dialog {0}".format(dialog['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_PATH},
                                                  {"TENDER_ID": dialog['id']}))
                logger.info("Schedule retry for tender {0}".format(dialog['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_RETRY_PATH},
                                                  {"TENDER_ID": dialog['id']}))
                self.dialog_retry_path_queue.put(dialog)
            else:
                logger.info("Successfully patch competitive dialogue {}".format(res_patch['data']['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CD_PATCHED},
                                                  {"DIALOGUE_ID": res_patch['data']['id'],
                                                   "TENDER_ID": res_patch['data']['stage2TenderID']}))
                db.delete('path_{dialog_id}'.format(dialog_id=res_patch['data']['id']))
                db._write()  # see https://github.com/mekarpeles/lazydb/blob/master/lazydb/lazydb.py#L64
            gevent.sleep(0)

    @retry(stop_max_attempt_number=15, wait_exponential_multiplier=1000 * 60)
    def _path_with_retry(self, dialog):
        try:
            data = {"data": dialog}
            logger.info("Path dialog {0}".format(dialog['id']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_CD_PATCHED},
                                              {"TENDER_ID": dialog['id']}))
            self.client.patch_tender(data)
        except Exception, e:
            logger.exception(e)
            raise

    def retry_path_dialog(self):
        while True:
            try:
                dialog = self.dialog_retry_path_queue.peek()
                self._path_with_retry(dialog)
            except:
                dialog = self.dialog_retry_path_queue.get()
                logger.warn("Can't path dialog {0}".format(dialog['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_PATH,
                                                   "TENDER_ID": dialog['id']}))
            else:
                # we patched dialog
                self.dialog_retry_path_queue.get()
                db.delete('path_{dialog_id}'.format(dialog_id=dialog['id']))
                db._write()  # see https://github.com/mekarpeles/lazydb/blob/master/lazydb/lazydb.py#L64
            gevent.sleep(0)

    @retry(stop_max_attempt_number=15, wait_exponential_multiplier=1000 * 60)
    def _put_with_retry(self, new_tender):
        data = {"data": new_tender}
        logger.info("Creating new tender of tender {0}".format(new_tender['dialogueID']),
                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_NEW_TENDER},
                                          {"TENDER_ID": new_tender['dialogueID']}))
        try:
            res = self.client.create_tender(data)
        except Exception, e:
            logger.exception(e)
            raise
        else:
            # Put data in queue for path dialog
            dialog = {"id": res['data']['dialogueID'],
                      "status": "complete",
                      "stage2TenderID": res['data']['id']}
            self.dialog_path_queue.put(dialog)
            # save dialog to local db
            db.put('path_{dialog_id}'.format(dialog_id=res['data']['dialogueID']), dialog)
            db.put(res['data']['dialogueID'], True)

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
        params = {'opt_fields': 'status', 'mode': '_all_'}
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
        params = {'opt_fields': 'status', 'descending': 1, 'mode': '_all_'}
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

    def init_path_tender(self):
        """
        Get all dialogs which we need to path and add them to queue
        """
        for key, value in db.items():
            if key.startswith('path'):

                self.dialog_path_queue.put(value)

    def run(self):
        logger.info('Start Competitive Dialogue Data Bridge')
        self.immortal_jobs = [
            gevent.spawn(self.get_competitive_dialogue_data),
            gevent.spawn(self.prepare_new_tender_data),
            gevent.spawn(self.put_tender_stage2),
            gevent.spawn(self.retry_put_tender_stage2),
            gevent.spawn(self.path_dialog),
            gevent.spawn(self.retry_path_dialog)
        ]
        self.init_path_tender()
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
