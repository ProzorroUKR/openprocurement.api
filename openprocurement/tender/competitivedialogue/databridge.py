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
from functools import partial
from restkit.errors import ResourceError

from retrying import retry
from uuid import uuid4

import gevent
from gevent.queue import Queue

from openprocurement_client.client import TendersClientSync as BaseTendersClientSync
from yaml import load

from openprocurement.tender.competitivedialogue.models_constants import (
    CD_UA_TYPE, CD_EU_TYPE, STAGE_2_EU_TYPE, STAGE_2_UA_TYPE, STAGE2_STATUS
)
from openprocurement.tender.competitivedialogue.journal_msg_ids import (
    DATABRIDGE_RESTART, DATABRIDGE_GET_CREDENTIALS, DATABRIDGE_GOT_CREDENTIALS,
    DATABRIDGE_FOUND_NOLOT,
    DATABRIDGE_COPY_TENDER_ITEMS, DATABRIDGE_GET_EXTRA_INFO, DATABRIDGE_MISSING_CREDENTIALS,
    DATABRIDGE_GOT_EXTRA_INFO, DATABRIDGE_CREATE_NEW_TENDER, DATABRIDGE_TENDER_CREATED, DATABRIDGE_UNSUCCESSFUL_CREATE,
    DATABRIDGE_RETRY_CREATE, DATABRIDGE_CREATE_ERROR, DATABRIDGE_TENDER_PROCESS,
    DATABRIDGE_SYNC_SLEEP, DATABRIDGE_SYNC_RESUME, DATABRIDGE_PATCH_DIALOG, DATABRIDGE_CD_PATCH_STAGE2_ID,
    DATABRIDGE_CD_UNSUCCESSFUL_PATCH_STAGE2_ID, DATABRIDGE_CD_RETRY_PATCH_STAGE2_ID,
    DATABRIDGE_CD_PATCHED_STAGE2_ID, DATABRIDGE_PATCH_NEW_TENDER_STATUS, DATABRIDGE_SUCCESSFUL_PATCH_NEW_TENDER_STATUS,
    DATABRIDGE_UNSUCCESSFUL_PATCH_NEW_TENDER_STATUS, DATABRIDGE_PATCH_DIALOG_STATUS,
    DATABRIDGE_UNSUCCESSFUL_PATCH_DIALOG_STATUS, DATABRIDGE_SUCCESSFUL_PATCH_DIALOG_STATUS, DATABRIDGE_ONLY_PATCH,
    DATABRIDGE_TENDER_STAGE2_NOT_EXIST, DATABRIDGE_CREATE_NEW_STAGE2, DATABRIDGE_WORKER_DIED)


dialog_work = set()  # local storage for current competitive dialogue in main queue

logger = logging.getLogger("openprocurement.tender.competitivedialogue.databridge")


def generate_req_id():
    return b'competitive-dialogue-data-bridge-req-' + str(uuid4()).encode('ascii')


def journal_context(record=None, params=None):
    if record is None:
        record = {}
    if params is None:
        params = {}
    for k, v in params.items():
        record["JOURNAL_" + k] = v
    return record


def get_item_by_related_lot(items, lot_id):
    for item in items:
        try:
            if item['relatedLot'] == lot_id:
                yield item
        except KeyError:
            raise KeyError('Item should contain \'relatedLot\' field.')


def get_lot_by_id(tender, lot_id):
    for lot in tender['lots']:
        if lot['id'] == lot_id:
            return lot


def get_bid_by_id(bids, bid_id):
    for bid in bids:
        if bid['id'] == bid_id:
            return bid


def prepare_lot(orig_tender, lot_id, items):
    """
    Replace new id in lot and related items
    :param orig_tender: competitive dialogue tender
    :param lot_id: origin lot id
    :param items: list with related item for lot
    :return: lot with new id
    """
    lot = get_lot_by_id(orig_tender, lot_id)
    if lot['status'] != 'active':
        return False
    for item in get_item_by_related_lot(orig_tender['items'], lot_id):
        items.append(item)
    return lot


def check_status_response(func):
    def func_wrapper(obj, *args, **kwargs):
        try:
            response = func(obj, *args, **kwargs)
        except ResourceError as re:
            if re.status_int == 412:
                obj.headers['Cookie'] = re.response.headers['Set-Cookie']
                response = func(obj, *args, **kwargs)
            else:
                raise ResourceError(re)
        return response
    return func_wrapper


class TendersClientSync(BaseTendersClientSync):

    @check_status_response
    def get_tender(self, *args, **kwargs):
        return super(TendersClientSync, self).get_tender(*args, **kwargs)

    @check_status_response
    def extract_credentials(self, *args, **kwargs):
        return super(TendersClientSync, self).extract_credentials(*args, **kwargs)

    @check_status_response
    def create_tender(self, *args, **kwargs):
        return super(TendersClientSync, self).create_tender(*args, **kwargs)

    @check_status_response
    def patch_tender(self, *args, **kwargs):
        return super(TendersClientSync, self).patch_tender(*args, **kwargs)


class CompetitiveDialogueDataBridge(object):
    """ Competitive Dialogue Data Bridge """
    copy_name_fields = ('title_ru', 'mode', 'procurementMethodDetails', 'title_en', 'description', 'description_en',
                        'description_ru', 'title', 'minimalStep', 'value', 'procuringEntity', 'submissionMethodDetails')
    rewrite_statuses = ['draft']
    allowed_statuses = ['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still',
                        'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled',
                        'unsuccessful', STAGE2_STATUS]

    def __init__(self, config):
        super(CompetitiveDialogueDataBridge, self).__init__()
        self.config = config

        self.tenders_sync_client = TendersClientSync(
            '',
            host_url=self.config_get('public_tenders_api_server') or self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
        )

        self.client = TendersClientSync(
            self.config_get('api_token'),
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
        )

        self.initial_sync_point = {}
        self.initialization_event = gevent.event.Event()
        self.competitive_dialogues_queue = Queue(maxsize=500)  # Id tender which need to check
        self.handicap_competitive_dialogues_queue = Queue(maxsize=500)
        self.dialogs_stage2_put_queue = Queue(maxsize=500)  # queue with new tender data
        self.dialogs_stage2_retry_put_queue = Queue(maxsize=500)

        self.dialog_stage2_id_queue = Queue(maxsize=500)
        self.dialog_retry_stage2_id_queue = Queue(maxsize=500)

        self.dialogs_stage2_patch_queue = Queue(maxsize=500)
        self.dialogs_stage2_retry_patch_queue = Queue(maxsize=500)

        self.dialog_set_complete_queue = Queue(maxsize=500)
        self.dialog_retry_set_complete_queue = Queue(maxsize=500)
        self.jobs_watcher_delay = self.config_get('jobs_watcher_delay') or 15

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
            response = self.tenders_sync_client.sync_tenders(params, extra_headers={'X-Client-Request-ID': generate_req_id()})
            # set values in reverse order due to 'descending' option
            self.initial_sync_point = {'forward_offset': response.prev_page.offset,
                                       'backward_offset': response.next_page.offset}
            self.initialization_event.set()
            logger.info("Initial sync point {}".format(self.initial_sync_point))
            return response
        elif not self.initial_sync_point:
            raise ValueError
        else:
            assert 'descending' not in params
            gevent.wait([self.initialization_event])
            self.initialization_event.clear()
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
                # Check, if we already work with this tender
                if tender['id'] in dialog_work:
                    logger.info('WORK with tender {}'.format(tender['id']))
                    continue
                if tender['procurementMethodType'] in [CD_UA_TYPE, CD_EU_TYPE] and tender['status'] == 'active.stage2.waiting':
                    logger.info('{0} sync: Found competitive dialogue (stage1), id={1} with status {2}'.format(direction.capitalize(), tender['id'], tender['status']),
                                extra=journal_context({"MESSAGE_ID": DATABRIDGE_FOUND_NOLOT},
                                                      {"TENDER_ID": tender['id']}))
                    yield tender
                else:
                    logger.debug('{0} sync: Skipping tender {1} in status {2} with procurementMethodType {3}'.format(direction.capitalize(), tender['id'], tender['status'], tender['procurementMethodType']),
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
                tender_to_sync = self.competitive_dialogues_queue.peek()  # Get competitive dialogue which we want to sync
                tender = self.tenders_sync_client.get_tender(tender_to_sync['id'])['data']  # Try get data by tender id
            except Exception, e:
                # If we have something problems then put tender back to queue
                logger.exception(e)
                logger.info('Put tender {} back to tenders queue'.format(tender_to_sync['id']),
                            extra=journal_context(params={"TENDER_ID": tender_to_sync['id']}))
                self.competitive_dialogues_queue.put(tender_to_sync)
            else:
                if 'stage2TenderID' in tender:
                    try:
                        tender_stage2 = self.tenders_sync_client.get_tender(tender['stage2TenderID'])['data']
                    except:
                        logger.info('Tender stage 2 id={0} didn\'t exist, need create new'.format(tender['id']),
                                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_STAGE2_NOT_EXIST},
                                                          {"TENDER_ID": tender['id']}))
                    else:
                        if tender_stage2.get('status') in self.allowed_statuses:
                            logger.info('For dialog {0} tender stage 2 already exists, need only patch'.format(tender['id']),
                                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_ONLY_PATCH},
                                                              {"TENDER_ID": tender['id']}))
                            patch_data = {"id": tender['id'],
                                          "status": "complete"}
                            self.dialog_set_complete_queue.put(patch_data)
                            continue
                        elif tender_stage2.get('status') in self.rewrite_statuses:
                            logger.info('Tender stage 2 id={0} has bad status need to create new '.format(tender['id']),
                                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_NEW_STAGE2},
                                                              {"TENDER_ID": tender['id']}))

                logger.info('Copy competitive dialogue data, id={} '.format(tender['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_COPY_TENDER_ITEMS},
                                                  {"TENDER_ID": tender['id']}))
                new_tender = dict(title=tender['title'], procurementMethod='selective',
                                  status='draft', dialogueID=tender['id'])

                for field_name in self.copy_name_fields:  # Copy fields from stage 1 competitive dialog
                    if field_name in tender:
                        new_tender[field_name] = tender[field_name]
                if tender['procurementMethodType'].endswith('EU'):
                    new_tender['procurementMethodType'] = STAGE_2_EU_TYPE
                else:
                    new_tender['procurementMethodType'] = STAGE_2_UA_TYPE
                new_tender['tenderID'] = '{}.2'.format(tender['tenderID']) # set tenderID as in stage1 + '.2'
                old_lots, items, short_listed_firms = dict(), list(), dict()
                for qualification in tender['qualifications']:
                    if qualification['status'] == 'active':  # check if qualification has status active
                        if qualification.get('lotID'):
                            if qualification['lotID'] not in old_lots:  # check if lot id in local dict with new lots
                                lot = prepare_lot(tender, qualification['lotID'], items)  # update lot with new id
                                if not lot:  # Go next iter if not lot
                                    continue
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
                if 'features' in tender:
                    new_tender['features'] = []
                    for feature in tender.get('features'):
                        if feature['featureOf'] == 'tenderer':  # If feature related to tender, than just copy
                            new_tender['features'].append(feature)
                        elif feature['featureOf'] == 'item':  # If feature related to item need check if it's actual
                            if feature['relatedItem'] in (item['id'] for item in new_tender['items']):
                                new_tender['features'].append(feature)
                        elif feature['featureOf'] == 'lot':  # If feature related to lot need check if it's actual
                            if feature['relatedItem'] in old_lots.keys():
                                new_tender['features'].append(feature)
                new_tender['shortlistedFirms'] = short_listed_firms.values()
                self.competitive_dialogues_queue.get()
                self.handicap_competitive_dialogues_queue.put(new_tender)

    def prepare_new_tender_data(self):
        while True:
            new_tender = self.handicap_competitive_dialogues_queue.get()
            try:
                logger.info("Getting extra info for competitive dialogue, id={0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_GET_EXTRA_INFO},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                tender_data = self.get_tender_credentials(new_tender['dialogueID'])
            except Exception, e:
                logger.exception(e)
                logger.info("Can't get competitive dialogue credentials, id={0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_MISSING_CREDENTIALS},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                self.handicap_competitive_dialogues_queue.put(new_tender)
            else:
                logger.debug("Got extra info for competitive dialogue, id={}".format(new_tender['dialogueID']),
                             extra=journal_context({"MESSAGE_ID": DATABRIDGE_GOT_EXTRA_INFO},
                                                   {"TENDER_ID": new_tender['dialogueID']}))
                data = tender_data.data
                new_tender['owner'] = data['owner']
                new_tender['dialogue_token'] = data['tender_token']
                self.dialogs_stage2_put_queue.put(new_tender)
            gevent.sleep(0)

    def put_tender_stage2(self):
        """
        Create tender for stage 2
        """
        while True:
            new_tender = self.dialogs_stage2_put_queue.get()
            logger.info("Creating tender stage2 from competitive dialogue id={}".format(new_tender['dialogueID']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_NEW_TENDER},
                                              {"TENDER_ID": new_tender['dialogueID']}))
            data = {"data": new_tender}
            try:
                res = self.client.create_tender(data)
            except ResourceError as re:
                if re.status_int == 412:  # Update Cookie, and retry
                    self.client.headers['Cookie'] = re.response.headers['Set-Cookie']
                elif re.status_int == 422:  # WARNING and don't retry
                    logger.warn("Catch 422 status, stop create tender stage2",
                                extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                                      {"TENDER_ID": new_tender['dialogueID']}))
                    logger.warn("Error response {}".format(re.message),
                                extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                                      {"TENDER_ID": new_tender['dialogueID']}))
                    continue
                elif re.status_int == 404:  # WARNING and don't retry
                    logger.warn("Catch 404 status, stop create tender stage2",
                                extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                                      {"TENDER_ID": new_tender['dialogueID']}))
                    continue
                logger.info("Unsuccessful put for tender stage2 of competitive dialogue id={0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                logger.info("Schedule retry for competitive dialogue id={0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_RETRY_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                self.dialogs_stage2_retry_put_queue.put(new_tender)
            except Exception, e:
                logger.info("Exception, schedule retry for competitive dialogue id={0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_RETRY_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                self.dialogs_stage2_retry_put_queue.put(new_tender)
                logger.exception(e)
            else:
                logger.info("Successfully created tender stage2 id={} from competitive dialogue id={}".format(res['data']['id'], res['data']['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_CREATED},
                                                  {"DIALOGUE_ID": res['data']['dialogueID'],
                                                   "TENDER_ID": res['data']['id']}))
                # Put data in queue for patch dialog
                dialog = {"id": res['data']['dialogueID'],
                          "stage2TenderID": res['data']['id']}
                self.dialog_stage2_id_queue.put(dialog)
            gevent.sleep(0)

    def patch_dialog_add_stage2_id(self):
        """
        Patch origin competitive dialogue - set tender id for stage 2 (field stage2TenderID)
        """
        while True:
            dialog = self.dialog_stage2_id_queue.get()
            dialog_work.add(dialog['id'])
            logger.info("Patch competitive dialogue id={} with stage2 tender id".format(dialog['id']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_CD_PATCH_STAGE2_ID},
                                              {"TENDER_ID": dialog['id']}))

            patch_data = {"data": dialog}
            try:
                res_patch = self.client.patch_tender(patch_data)
            except Exception, e:
                logger.exception(e)
                logger.info("Unsuccessful patch competitive dialogue id={0} with stage2 tender id".format(dialog['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CD_UNSUCCESSFUL_PATCH_STAGE2_ID},
                                                  {"TENDER_ID": dialog['id']}))
                logger.info("Schedule retry for competitive dialogue id={0}".format(dialog['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CD_RETRY_PATCH_STAGE2_ID},
                                                  {"TENDER_ID": dialog['id']}))
                self.dialog_retry_stage2_id_queue.put(dialog)
            else:
                logger.info("Successful patch competitive dialogue id={0} with stage2 tender id".format(res_patch['data']['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CD_PATCHED_STAGE2_ID},
                                                  {"DIALOGUE_ID": res_patch['data']['id'],
                                                   "TENDER_ID": res_patch['data']['stage2TenderID']}))
                data = {"id": dialog['stage2TenderID'],
                        "status": STAGE2_STATUS,
                        "dialogueID": dialog['id']}
                self.dialogs_stage2_patch_queue.put(data)
            gevent.sleep(0)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def _patch_dialog_add_stage2_id_with_retry(self, dialog):
        try:
            data = {"data": dialog}
            logger.info("Patch competitive dialogue id={0}".format(dialog['id']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_PATCH_DIALOG},
                                              {"TENDER_ID": dialog['id']}))
            self.client.patch_tender(data)
        except Exception, e:
            logger.exception(e)
            raise

    def retry_patch_dialog_add_stage2_id(self):
        while True:
            try:
                dialog = self.dialog_retry_stage2_id_queue.get()
                self._patch_dialog_add_stage2_id_with_retry(dialog)
            except:
                logger.warn("Can't patch competitive dialogue id={0}".format(dialog['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CD_UNSUCCESSFUL_PATCH_STAGE2_ID},
                                                  {"TENDER_ID": dialog['id']}))
                self.competitive_dialogues_queue.put({"id": dialog['id']})
            else:
                data = {"id": dialog['stage2TenderID'],
                        "status": STAGE2_STATUS,
                        "dialogueID": dialog['id']}
                self.dialogs_stage2_patch_queue.put(data)
            gevent.sleep(0)

    def patch_new_tender_status(self):
        while True:
            patch_data = self.dialogs_stage2_patch_queue.get()
            logger.info("Patch tender stage2 id={0} with status {1}".format(patch_data['id'], patch_data['status']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_PATCH_NEW_TENDER_STATUS},
                                              {"TENDER_ID": patch_data["id"]}))
            try:
                res = self.client.patch_tender({"data": patch_data})
            except Exception, e:
                logger.exception(e)
                logger.info("Unsuccessful path tender stage2 id={0} with status {1}".format(patch_data['id'], patch_data['status']))
                logger.info("Schedule retry patch for tender stage2 {0}".format(patch_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_PATCH_NEW_TENDER_STATUS},
                                                  {"TENDER_ID": patch_data['id']}))
                self.dialogs_stage2_retry_patch_queue.put(patch_data)
            else:
                logger.info("Successful patch tender stage2 id={0} with status {1}".format(patch_data['id'], patch_data['status']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_SUCCESSFUL_PATCH_NEW_TENDER_STATUS}))
                patch_data = {"id": res['data']['dialogueID'],
                              "status": "complete"}
                self.dialog_set_complete_queue.put(patch_data)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def _patch_new_tender_status_with_retry(self, new_tender):
        try:
            data = {"data": new_tender}
            logger.info("Patch new tender stage2 id={0} status".format(new_tender['id']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_PATCH_NEW_TENDER_STATUS},
                                              {"TENDER_ID": new_tender['id']}))
            self.client.patch_tender(data)
        except Exception, e:
            logger.exception(e)
            raise

    def path_dialog_status(self):
        while True:
            patch_data = self.dialog_set_complete_queue.get()
            logger.info("Patch competitive dialogue id={0} with status {1}".format(patch_data['id'], patch_data['status']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_PATCH_DIALOG_STATUS},
                                              {"TENDER_ID": patch_data["id"]}))
            try:
                self.client.patch_tender({"data": patch_data})
            except Exception, e:
                logger.exception(e)
                logger.info("Unsuccessful path competitive dialogue id={0} with status {1}".format(patch_data['id'], patch_data['status']))
                logger.info("Schedule retry patch for competitive dialogue id={0}".format(patch_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_PATCH_DIALOG_STATUS},
                                                  {"TENDER_ID": patch_data['id']}))
                self.dialog_retry_set_complete_queue.put(patch_data)
            else:
                logger.info("Successful patch competitive dialogue id={0} with status {1}".format(patch_data['id'], patch_data['status']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_SUCCESSFUL_PATCH_DIALOG_STATUS}))
                try:
                    dialog_work.remove(patch_data['id'])
                except KeyError:
                    pass

    def retry_patch_dialog_status(self):
        while True:
            patch_data = self.dialog_retry_set_complete_queue.get()
            try:
                self._patch_dialog_status_with_retry(patch_data)
            except:
                logger.warn("Can't patch competitive dialogue id={0} with status {1}".format(patch_data['id'], patch_data['status']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_PATCH_DIALOG_STATUS,
                                                   "TENDER_ID": patch_data['id']}))
                self.competitive_dialogues_queue.put({"id": patch_data['id']})
            gevent.sleep(0)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def _patch_dialog_status_with_retry(self, patch_data):
        try:
            data = {"data": patch_data}
            logger.info("Patch competitive dialogue id={0} with status {1}".format(patch_data['id'], patch_data['status']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_PATCH_DIALOG_STATUS},
                                              {"TENDER_ID": patch_data['id']}))
            self.client.patch_tender(data)
        except Exception, e:
            logger.exception(e)
            raise

    def retry_patch_new_tender_status(self):
        while True:
            patch_data = self.dialogs_stage2_retry_patch_queue.get()
            try:
                self._patch_new_tender_status_with_retry(patch_data)
            except:
                logger.warn("Can't patch tender stage2 id={0} with status {1}".format(patch_data['id'], patch_data['status']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_PATCH_NEW_TENDER_STATUS,
                                                   "TENDER_ID": patch_data['id']}))
                self.competitive_dialogues_queue.put({"id": patch_data['dialogueID']})
            gevent.sleep(0)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=10000)
    def _put_with_retry(self, new_tender):
        data = {"data": new_tender}
        logger.info("Creating tender stage2 from competitive dialogue id={0}".format(new_tender['dialogueID']),
                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_NEW_TENDER},
                                          {"TENDER_ID": new_tender['dialogueID']}))
        try:
            res = self.client.create_tender(data)
        except ResourceError as re:
            if re.status_int == 412:  # Update Cookie, and retry
                self.client.headers['Cookie'] = re.response.headers['Set-Cookie']
            elif re.status_int == 422:  # WARNING and don't retry
                logger.warn("Catch 422 status, stop create tender stage2",
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
                logger.warn("Error response {}".format(re.message),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
            elif re.status_int == 404:  # WARNING and don't retry
                logger.warn("Catch 404 status, stop create tender stage2",
                            extra=journal_context(
                                {"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                {"TENDER_ID": new_tender['dialogueID']}))
            else:
                logger.info("Unsuccessful put for tender stage2 of competitive dialogue id={0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE},
                                                  {"TENDER_ID": new_tender['dialogueID']}))
            raise re
        except Exception, e:
            logger.exception(e)
            raise
        else:
            # Put data in queue for patch dialog
            dialog = {"id": res['data']['dialogueID'],
                      "stage2TenderID": res['data']['id']}
            self.dialog_stage2_id_queue.put(dialog)

    def retry_put_tender_stage2(self):
        while True:
            try:
                new_tender = self.dialogs_stage2_retry_put_queue.get()
                self._put_with_retry(new_tender)
            except:
                del new_tender['dialogue_token']  # do not reveal tender credentials in logs
                logger.warn("Can't create tender stage2 from competitive dialogue id={0}".format(new_tender['dialogueID']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_ERROR,
                                                   "TENDER_ID": new_tender['dialogueID']}))
                self.competitive_dialogues_queue.put({"id": new_tender['dialogueID']})
            else:
                dialog = {"id": new_tender['dialogueID'],
                          "stage2TenderID": new_tender['id']}
                self.dialog_stage2_id_queue.put(dialog)
            gevent.sleep(0)

    def get_competitive_dialogue_forward(self):
        logger.info('Start forward data sync worker...')
        params = {'opt_fields': 'status,procurementMethodType', 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="forward"):
                logger.info('Forward sync: Put competitive dialogue id={} to process...'.format(tender_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_PROCESS},
                                                  {"TENDER_ID": tender_data['id']}))
                self.competitive_dialogues_queue.put(tender_data)
        except ResourceError as re:
            logger.warn('Forward worker died!', extra=journal_context({"MESSAGE_ID": DATABRIDGE_WORKER_DIED}, {}))
            logger.error("Error response {}".format(re.message))
            raise re
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Forward worker died!', extra=journal_context({"MESSAGE_ID": DATABRIDGE_WORKER_DIED}, {}))
            logger.exception(e)
            raise e
        else:
            logger.warn('Forward data sync finished!')  # Should never happen!!!

    def get_competitive_dialogue_backward(self):
        logger.info('Start backward data sync worker...')
        params = {'opt_fields': 'status,procurementMethodType', 'descending': 1, 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="backward"):
                logger.info('Backward sync: Put competitive dialogue id={} to process...'.format(tender_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_PROCESS},
                                                  {"TENDER_ID": tender_data['id']}))
                self.competitive_dialogues_queue.put(tender_data)
        except ResourceError as re:
            logger.warn('Backward worker died!', extra=journal_context({"MESSAGE_ID": DATABRIDGE_WORKER_DIED}, {}))
            logger.error("Error response {}".format(re.message))
            raise re
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Backward worker died!', extra=journal_context({"MESSAGE_ID": DATABRIDGE_WORKER_DIED}, {}))
            logger.exception(e)
            raise e
        else:
            logger.info('Backward data sync finished.')

    def catch_exception(self, exc, name):
        """Restarting job"""
        logger.warning('Worker died! Restarting {}.'.format(name), extra=journal_context({"MESSAGE_ID": DATABRIDGE_WORKER_DIED}, {}))
        if name == 'get_competitive_dialogue_data':
            tender = self.competitive_dialogues_queue.get()  # delete invalid tender from queue
            logger.info('Remove invalid tender {}'.format(tender.id))
        self.immortal_jobs[name] = gevent.spawn(getattr(self, name))
        self.immortal_jobs[name].link_exception(partial(self.catch_exception, name=name))

    def _start_competitive_sculptors(self):
        logger.info('Start Competitive Dialogue Data Bridge')
        self.immortal_jobs = {
            'get_competitive_dialogue_data': gevent.spawn(self.get_competitive_dialogue_data),
            'prepare_new_tender_data': gevent.spawn(self.prepare_new_tender_data),
            'put_tender_stage2': gevent.spawn(self.put_tender_stage2),
            'retry_put_tender_stage2': gevent.spawn(self.retry_put_tender_stage2),
            'patch_dialog_add_stage2_id': gevent.spawn(self.patch_dialog_add_stage2_id),
            'retry_patch_dialog_add_stage2_id': gevent.spawn(self.retry_patch_dialog_add_stage2_id),
            'patch_new_tender_status': gevent.spawn(self.patch_new_tender_status),
            'retry_patch_new_tender_status': gevent.spawn(self.retry_patch_new_tender_status),
            'path_dialog_status': gevent.spawn(self.path_dialog_status),
            'retry_patch_dialog_status': gevent.spawn(self.retry_patch_dialog_status)
        }
        for name, job in self.immortal_jobs.items():
            job.link_exception(partial(self.catch_exception, name=name))

    def _start_competitive_wokers(self):
        self.jobs = [
            gevent.spawn(self.get_competitive_dialogue_backward),
            gevent.spawn(self.get_competitive_dialogue_forward),
        ]

    def _restart_synchronization_workers(self):
        logger.warn("Restarting synchronization", extra=journal_context({"MESSAGE_ID": DATABRIDGE_RESTART}, {}))
        for j in self.jobs:
            j.kill()
        self._start_competitive_wokers()

    def run(self):
        self._start_competitive_sculptors()
        self._start_competitive_wokers()
        backward_worker, forward_worker = self.jobs

        try:
            while True:
                gevent.sleep(self.jobs_watcher_delay)
                if forward_worker.dead or (backward_worker.dead and not backward_worker.successful()):
                    self._restart_synchronization_workers()
                    backward_worker, forward_worker = self.jobs
            logger.info('Starting forward and backward sync workers')
        except KeyboardInterrupt:
            logger.info('Exiting...')
            gevent.killall(self.jobs, timeout=5)
            gevent.killall(self.immortal_jobs, timeout=5)
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