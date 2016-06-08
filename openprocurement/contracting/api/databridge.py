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

from copy import deepcopy
from retrying import retry
from uuid import uuid4

import gevent
from gevent.queue import Queue

from openprocurement_client.client import TendersClientSync, TendersClient
from openprocurement_client.contract import ContractingClient
from openprocurement_client.client import ResourceNotFound
from yaml import load
from openprocurement.contracting.api.journal_msg_ids import (
    DATABRIDGE_RESTART, DATABRIDGE_GET_CREDENTIALS, DATABRIDGE_GOT_CREDENTIALS,
    DATABRIDGE_FOUND_MULTILOT_COMPLETE, DATABRIDGE_FOUND_NOLOT_COMPLETE,
    DATABRIDGE_CONTRACT_TO_SYNC, DATABRIDGE_CONTRACT_EXISTS,
    DATABRIDGE_COPY_CONTRACT_ITEMS, DATABRIDGE_MISSING_CONTRACT_ITEMS,
    DATABRIDGE_GET_EXTRA_INFO, DATABRIDGE_MISSING_CREDENTIALS,
    DATABRIDGE_GOT_EXTRA_INFO, DATABRIDGE_CREATE_CONTRACT,
    DATABRIDGE_CONTRACT_CREATED, DATABRIDGE_UNSUCCESSFUL_CREATE,
    DATABRIDGE_RETRY_CREATE, DATABRIDGE_CREATE_ERROR, DATABRIDGE_TENDER_PROCESS,
    DATABRIDGE_SKIP_NOT_MODIFIED, DATABRIDGE_SYNC_SLEEP, DATABRIDGE_SYNC_RESUME)


logger = logging.getLogger("openprocurement.contracting.api.databridge")
# logger = logging.getLogger(__name__)

from lazydb import Db

db = Db('databridge_cache_db')


def generate_req_id():
    return b'contracting-data-bridge-req-' + str(uuid4()).encode('ascii')


def journal_context(extra):
    return dict([("JOURNAL_" + k, v) for k, v in extra.items()])


class ContractingDataBridge(object):
    """ Contracting Data Bridge """

    def __init__(self, config):
        super(ContractingDataBridge, self).__init__()
        self.config = config

        self.tenders_sync_client = TendersClientSync('',
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
        )

        self.client = TendersClient(
            self.config_get('api_token'),
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
        )

        self.contracting_client = ContractingClient(
            self.config_get('api_token'),
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version')
        )

        self.initial_sync_point = {}
        self.tenders_queue = Queue(maxsize=500)
        self.handicap_contracts_queue = Queue(maxsize=500)
        self.contracts_put_queue = Queue(maxsize=500)
        self.contracts_retry_put_queue = Queue(maxsize=500)

    def config_get(self, name):
        return self.config.get('main').get(name)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def get_tender_credentials(self, tender_id):
        self.client.headers.update({'X-Client-Request-ID': generate_req_id()})
        logger.info("Getting credentials for tender {}".format(tender_id), extra=journal_context({"MESSAGE_ID": DATABRIDGE_GET_CREDENTIALS,
                                                                                                  "TENDER_ID": tender_id}))
        data = self.client.extract_credentials(tender_id)
        logger.info("Got tender {} credentials".format(tender_id), extra=journal_context({"MESSAGE_ID": DATABRIDGE_GOT_CREDENTIALS,
                                                                                          "TENDER_ID": tender_id}))
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
            logger.info("Initial sync point {}".format(self.initial_sync_point))
            return response
        elif not self.initial_sync_point:
            raise ValueError
        else:
            assert 'descending' not in params
            params['offset'] = self.initial_sync_point['forward_offset']
            logger.info("Starting forward sync from offset {}".format(params['offset']))
            return self.tenders_sync_client.sync_tenders(params, extra_headers={'X-Client-Request-ID': generate_req_id()})

    def get_tenders(self, params={}, direction=""):
        response = self.initialize_sync(params=params, direction=direction)

        while not (params.get('descending') and not len(response.data) and params.get('offset') == response.next_page.offset):
            tenders_list = response.data
            params['offset'] = response.next_page.offset

            delay = 101
            if tenders_list:
                delay = 15
                logger.info("Client {} params: {}".format(direction, params))
            for tender in tenders_list:
                if tender['status'] in ("active.qualification",
                                        "active.awarded", "complete"):
                    if hasattr(tender, "lots"):
                        if any([1 for lot in tender['lots'] if lot['status'] == "complete"]):
                            logger.info('{} sync: Found multilot tender {} in status {}'.format(direction.capitalize(), tender['id'], tender['status']),
                                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_FOUND_MULTILOT_COMPLETE, "TENDER_ID": tender['id']}))
                            yield tender
                    elif tender['status'] == "complete":
                        logger.info('{} sync: Found tender in complete status {}'.format(direction.capitalize(), tender['id']),
                                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_FOUND_NOLOT_COMPLETE, "TENDER_ID": tender['id']}))
                        yield tender
                else:
                    logger.debug('{} sync: Skipping tender {} in status {}'.format(direction.capitalize(), tender['id'], tender['status']),
                                 extra=journal_context({"TENDER_ID": tender['id']}))

            logger.info('Sleep {} sync...'.format(direction), extra=journal_context({"MESSAGE_ID": DATABRIDGE_SYNC_SLEEP}))
            gevent.sleep(delay)
            logger.info('Restore {} sync'.format(direction), extra=journal_context({"MESSAGE_ID": DATABRIDGE_SYNC_RESUME}))
            logger.debug('{} {}'.format(direction, params))
            response = self.tenders_sync_client.sync_tenders(params, extra_headers={'X-Client-Request-ID': generate_req_id()})

    def get_tender_contracts(self):
        while True:
            try:
                tender_to_sync = self.tenders_queue.get()
                tender = self.tenders_sync_client.get_tender(tender_to_sync['id'],
                                                             extra_headers={'X-Client-Request-ID': generate_req_id()})['data']
                db.put(tender_to_sync['id'], {'dateModified': tender_to_sync['dateModified']})
            except Exception, e:
                logger.exception(e)
                logger.info('Put tender {} back to tenders queue'.format(tender_to_sync['id']), extra=journal_context({"TENDER_ID": tender_to_sync['id']}))
                self.tenders_queue.put(tender_to_sync)
            else:
                if 'contracts' not in tender:
                    logger.warn('!!!No contracts found in tender {}'.format(tender['id']), extra=journal_context({"TENDER_ID": tender['id']}))
                    continue
                for contract in tender['contracts']:
                    if contract["status"] == "active":

                        try:
                            if not db.has(contract['id']):
                                self.contracting_client.get_contract(contract['id'])
                            else:
                                logger.info('Contract {} exists in local db'.format(contract['id']), extra=journal_context({"CONTRACT_ID": contract['id']}))
                                continue
                        except ResourceNotFound:
                            logger.info('Sync contract {} of tender {}'.format(contract['id'], tender['id']), extra=journal_context(
                                {"CONTRACT_ID": contract['id'], "TENDER_ID": tender['id'], "MESSAGE_ID": DATABRIDGE_CONTRACT_TO_SYNC}))
                        except Exception, e:
                            logger.exception(e)
                            logger.info('Put tender {} back to tenders queue'.format(tender_to_sync['id']), extra=journal_context({"TENDER_ID": tender_to_sync['id']}))
                            self.tenders_queue.put(tender_to_sync)
                            break
                        else:
                            db.put(contract['id'], True)
                            logger.info('Contract exists {}'.format(contract['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_CONTRACT_EXISTS,
                                                                                                            "CONTRACT_ID": contract['id']}))
                            continue

                            contract['tender_id'] = tender['id']
                        contract['procuringEntity'] = tender['procuringEntity']

                        if not contract.get('items'):
                            logger.info('Copying contract {} items'.format(contract['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_COPY_CONTRACT_ITEMS,
                                                                                                                   "CONTRACT_ID": contract['id']}))
                            if tender.get('lots'):
                                related_awards = [aw for aw in tender['awards'] if aw['id'] == contract['awardID']]
                                if related_awards:
                                    award = related_awards[0]
                                    if award.get("items"):
                                        logger.debug('Copying items from related award {}'.format(award['id']))
                                        contract['items'] = award['items']
                                    else:
                                        logger.debug('Copying items matching related lot {}'.format(award['relatedLot']))
                                        contract['items'] = [item for item in tender['items'] if item['relatedLot'] == award['lotID']]
                                else:
                                    logger.warn('Not found related award for contact {} of tender {}'.format(contract['id'], tender['id']),
                                                extra=journal_context({"CONTRACT_ID": contract['id'], "TENDER_ID": tender['id']}))
                            else:
                                logger.debug('Copying all tender {} items into contract {}'.format(tender['id'], contract['id']),
                                             extra=journal_context({"CONTRACT_ID": contract['id'], "TENDER_ID": tender['id']}))
                                contract['items'] = tender['items']

                        if not contract.get('items'):
                            logger.warn('Contact {} of tender {} does not contain items info'.format(contract['id'], tender['id']),
                                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_MISSING_CONTRACT_ITEMS,
                                                               "CONTRACT_ID": contract['id'], "TENDER_ID": tender['id']}))

                        self.handicap_contracts_queue.put(contract)

    def prepare_contract_data(self):
        while True:
            contract = self.handicap_contracts_queue.get()
            try:
                logger.info("Getting extra info for tender {}".format(contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_GET_EXTRA_INFO, "TENDER_ID": contract['tender_id']}))
                tender_data = self.get_tender_credentials(contract['tender_id'])
            except Exception, e:
                logger.exception(e)
                logger.info("Can't get tender credentials {}".format(contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_MISSING_CREDENTIALS, "TENDER_ID": contract['tender_id']}))
                self.handicap_contracts_queue.put(contract)
            else:
                logger.debug("Got extra info for tender {}".format(contract['tender_id']),
                             extra=journal_context({"MESSAGE_ID": DATABRIDGE_GOT_EXTRA_INFO, "TENDER_ID": contract['tender_id']}))
                data = tender_data.data
                if data.get('mode'):
                    contract['mode'] = data['mode']
                contract['owner'] = data['owner']
                contract['tender_token'] = data['tender_token']
                self.contracts_put_queue.put(contract)
            gevent.sleep(0)

    def put_contracts(self):
        while True:
            contract = self.contracts_put_queue.get()
            try:
                logger.info("Creating contract {} of tender {}".format(contract['id'], contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_CONTRACT, "CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
                data = {"data": contract.toDict()}
                self.contracting_client.create_contract(data)
                logger.info("Successfully created contract {} of tender {}".format(contract['id'], contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CONTRACT_CREATED, "CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
                db.put(contract['id'], True)
            except Exception, e:
                logger.exception(e)
                logger.info("Unsuccessful put for contract {0} of tender {1}".format(contract['id'], contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_UNSUCCESSFUL_CREATE, "CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
                logger.info("Schedule retry for contract {0}".format(contract['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_RETRY_CREATE, "CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
                self.contracts_retry_put_queue.put(contract)
            gevent.sleep(0)

    @retry(stop_max_attempt_number=15, wait_exponential_multiplier=1000 * 60)
    def _put_with_retry(self, contract):
        try:
            data = {"data": contract.toDict()}
            logger.info("Creating contract {} of tender {}".format(contract['id'], contract['tender_id']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_CONTRACT, "CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
            self.contracting_client.create_contract(data)
        except Exception, e:
            logger.exception(e)
            raise

    def retry_put_contracts(self):
        while True:
            try:
                contract = self.contracts_retry_put_queue.peek()
                self._put_with_retry(contract)
            except:
                contract = self.contracts_retry_put_queue.get()
                del contract['tender_token']  # do not reveal tender credentials in logs
                logger.warn("Can't create contract {}".format(contract),  extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_ERROR, "CONTRACT_ID": contract['id']}))
            else:
                self.contracts_retry_put_queue.get()
            gevent.sleep(0)

    def get_tender_contracts_forward(self):
        logger.info('Start forward data sync worker...')
        params = {'opt_fields': 'status,lots', 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="forward"):
                logger.info('Forward sync: Put tender {} to process...'.format(tender_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_PROCESS, "TENDER_ID": tender_data['id']}))
                self.tenders_queue.put(tender_data)
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Forward worker died!')
            logger.exception(e)
        else:
            logger.warn('Forward data sync finished!')  # Should never happen!!!

    def get_tender_contracts_backward(self):
        logger.info('Start backward data sync worker...')
        params = {'opt_fields': 'status,lots', 'descending': 1, 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="backward"):
                stored = db.get(tender_data['id'])
                if stored and stored['dateModified'] == tender_data['dateModified']:
                    logger.info('Tender {} not modified from last check. Skipping'.format(tender_data['id']), extra=journal_context(
                        {"MESSAGE_ID": DATABRIDGE_SKIP_NOT_MODIFIED, "TENDER_ID": tender_data['id']}))
                    continue
                logger.info('Backward sync: Put tender {} to process...'.format(tender_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_PROCESS, "TENDER_ID": tender_data['id']}))
                self.tenders_queue.put(tender_data)
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Backward worker died!')
            logger.exception(e)
        else:
            logger.info('Backward data sync finished.')

    def sync_single_tender(self, tender_id):
        transfered_contracts = []
        try:
            logger.info("Getting tender {}".format(tender_id))
            tender = self.tenders_sync_client.get_tender(tender_id)['data']
            logger.info("Got tender {} in status {}".format(tender['id'], tender['status']))

            logger.info("Getting tender {} credentials".format(tender_id))
            tender_credentials = self.get_tender_credentials(tender_id)['data']
            logger.info("Got tender {} credentials".format(tender_id))

            for contract in tender.get('contracts', []):
                if contract['status'] != 'active':
                    logger.info("Skip contract {} in status {}".format(contract['id'], contract['status']))
                    continue

                logger.info("Checking if contract {} already exists".format(contract['id']))
                try:
                    self.contracting_client.get_contract(contract['id'])
                except ResourceNotFound:
                    logger.info('Contract {} does not exists. Prepare contract for creation.'.format(contract['id']))
                else:
                    logger.info('Contract exists {}'.format(contract['id']))
                    continue

                logger.info("Extending contract {} with extra data".format(contract['id']))
                if tender.get('mode'):
                    contract['mode'] = tender['mode']
                contract['tender_id'] = tender['id']
                contract['procuringEntity'] = tender['procuringEntity']
                contract['owner'] = tender['owner']
                contract['tender_token'] = tender_credentials['tender_token']
                data = {"data": contract.toDict()}
                logger.info("Creating contract {}".format(contract['id']))
                response = self.contracting_client.create_contract(data)
                assert 'data' in response
                logger.info("Contract {} created".format(contract['id']))
                transfered_contracts.append(contract['id'])
        except Exception, e:
            logger.exception(e)
            raise
        else:
            if transfered_contracts:
                logger.info("Successfully transfered contracts: {}".format(transfered_contracts))
            else:
                logger.info("Tender {} does not contain contracts to transfer".format(tender_id))


    def run(self):
        logger.info('Start Contracting Data Bridge')
        self.immortal_jobs = [
            gevent.spawn(self.get_tender_contracts),
            gevent.spawn(self.prepare_contract_data),
            gevent.spawn(self.put_contracts),
            gevent.spawn(self.retry_put_contracts),
        ]
        while True:
            try:
                logger.info('Starting forward and backward sync workers')
                self.jobs = [
                    gevent.spawn(self.get_tender_contracts_backward),
                    gevent.spawn(self.get_tender_contracts_forward),
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
    parser = argparse.ArgumentParser(description='Contracting Data Bridge')
    parser.add_argument('config', type=str, help='Path to configuration file')
    parser.add_argument('--tender', type=str, help='Tender id to sync', dest="tender_id")
    params = parser.parse_args()
    if os.path.isfile(params.config):
        with open(params.config) as config_file_obj:
            config = load(config_file_obj.read())
        logging.config.dictConfig(config)
        if params.tender_id:
            ContractingDataBridge(config).sync_single_tender(params.tender_id)
        else:
            ContractingDataBridge(config).run()
    else:
        logger.info('Invalid configuration file. Exiting...')


if __name__ == "__main__":
    main()
