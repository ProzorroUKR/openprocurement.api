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
    DATABRIDGE_GET_EXTRA_INFO, DATABRIDGE_WORKER_DIED, DATABRIDGE_START,
    DATABRIDGE_GOT_EXTRA_INFO, DATABRIDGE_CREATE_CONTRACT, DATABRIDGE_EXCEPTION,
    DATABRIDGE_CONTRACT_CREATED, DATABRIDGE_RETRY_CREATE, DATABRIDGE_INFO,
    DATABRIDGE_TENDER_PROCESS, DATABRIDGE_SKIP_NOT_MODIFIED,
    DATABRIDGE_SYNC_SLEEP, DATABRIDGE_SYNC_RESUME, DATABRIDGE_CACHED)


logger = logging.getLogger("openprocurement.contracting.api.databridge")
# logger = logging.getLogger(__name__)


class Db(object):
    """ Database proxy """

    def __init__(self, config):
        self.config = config

        self._backend = None
        self._db_name = None
        self._port = None
        self._host = None

        if 'cache_host' in self.config:
            import redis
            self._backend = "redis"
            self._host = self.config.get('cache_host')
            self._port = self.config.get('cache_port') or 6379
            self._db_name = self.config.get('cache_db_name') or 0
            self.db = redis.StrictRedis(host=self._host, port=self._port,
                                        db=self._db_name)
            self.set_value = self.db.set
            self.has_value = self.db.exists
        else:
            from lazydb import Db
            self._backend = "lazydb"
            self._db_name = self.config.get('cache_db_name') or 'databridge_cache_db'
            self.db = Db(self._db_name)
            self.set_value = self.db.put
            self.has_value = self.db.has


    def get(self, key):
        return self.db.get(key)

    def put(self, key, value):
        self.set_value(key, value)

    def has(self, key):
        return self.has_value(key)


def generate_req_id():
    return b'contracting-data-bridge-req-' + str(uuid4()).encode('ascii')


def journal_context(record={}, params={}):
    for k, v in params.items():
        record["JOURNAL_" + k] = v
    return record


class ContractingDataBridge(object):
    """ Contracting Data Bridge """

    def __init__(self, config):
        super(ContractingDataBridge, self).__init__()
        self.config = config

        self.cache_db = Db(self.config.get('main'))

        self._backend = "redis"
        self._host = self.config.get('cache_host')
        self._port = self.config.get('cache_port') or 6379
        self._db_name = self.config.get('cache_db_name') or 0

        logger.info("Caching backend: '{}', db name: '{}', host: '{}', port: '{}'".format(self.cache_db._backend,
                                                                                          self.cache_db._db_name,
                                                                                          self.cache_db._host,
                                                                                          self.cache_db._port),
                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_INFO}, {}))


        self.on_error_delay = self.config_get('on_error_sleep_delay') or 5
        self.jobs_watcher_delay = self.config_get('jobs_watcher_delay') or 15
        queue_size = self.config_get('buffers_size') or 500
        self.full_stack_sync_delay = self.config_get('full_stack_sync_delay') or 15
        self.empty_stack_sync_delay = self.config_get('empty_stack_sync_delay') or 101

        api_server = self.config_get('tenders_api_server')
        api_version = self.config_get('tenders_api_version')
        ro_api_server = self.config_get('public_tenders_api_server') or api_server

        contracting_api_server = self.config_get('contracting_api_server')
        contracting_api_version = self.config_get('contracting_api_version')

        self.tenders_sync_client = TendersClientSync('',
            host_url=ro_api_server, api_version=api_version,
        )

        self.client = TendersClient(
            self.config_get('api_token'),
            host_url=api_server, api_version=api_version,
        )

        self.contracting_client = ContractingClient(
            self.config_get('api_token'),
            host_url=contracting_api_server, api_version=contracting_api_version
        )

        self.contracting_client_ro = self.contracting_client
        if self.config_get('public_tenders_api_server'):
            if api_server == contracting_api_server and api_version == contracting_api_version:
                self.contracting_client_ro = ContractingClient(
                    self.config_get('api_token'),
                    host_url=ro_api_server, api_version=api_version
                )

        self.initial_sync_point = {}
        self.initialization_event = gevent.event.Event()
        self.tenders_queue = Queue(maxsize=queue_size)
        self.handicap_contracts_queue = Queue(maxsize=queue_size)
        self.contracts_put_queue = Queue(maxsize=queue_size)
        self.contracts_retry_put_queue = Queue(maxsize=queue_size)
        self.basket = {}

    def config_get(self, name):
        return self.config.get('main').get(name)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def get_tender_credentials(self, tender_id):
        self.client.headers.update({'X-Client-Request-ID': generate_req_id()})
        logger.info("Getting credentials for tender {}".format(tender_id), extra=journal_context({"MESSAGE_ID": DATABRIDGE_GET_CREDENTIALS},
                                                                                                 {"TENDER_ID": tender_id}))
        data = self.client.extract_credentials(tender_id)
        logger.info("Got tender {} credentials".format(tender_id), extra=journal_context({"MESSAGE_ID": DATABRIDGE_GOT_CREDENTIALS},
                                                                                         {"TENDER_ID": tender_id}))
        return data

    def initialize_sync(self, params=None, direction=None):
        if direction == "backward":
            assert params['descending']
            response = self.tenders_sync_client.sync_tenders(params, extra_headers={'X-Client-Request-ID': generate_req_id()})
            # set values in reverse order due to 'descending' option
            self.initial_sync_point = {'forward_offset': response.prev_page.offset,
                                       'backward_offset': response.next_page.offset}
            self.initialization_event.set()  # wake up forward worker
            logger.info("Initial sync point {}".format(self.initial_sync_point))
            return response
        else:
            assert 'descending' not in params
            gevent.wait([self.initialization_event])
            params['offset'] = self.initial_sync_point['forward_offset']
            logger.info("Starting forward sync from offset {}".format(params['offset']))
            return self.tenders_sync_client.sync_tenders(params, extra_headers={'X-Client-Request-ID': generate_req_id()})

    def get_tenders(self, params={}, direction=""):
        response = self.initialize_sync(params=params, direction=direction)

        while not (params.get('descending') and not len(response.data) and params.get('offset') == response.next_page.offset):
            tenders_list = response.data
            params['offset'] = response.next_page.offset

            delay = self.empty_stack_sync_delay
            if tenders_list:
                delay = self.full_stack_sync_delay
                logger.info("Client {} params: {}".format(direction, params))
            for tender in tenders_list:
                if tender['status'] in ("active.qualification",
                                        "active.awarded", "complete"):
                    if hasattr(tender, "lots"):
                        if any([1 for lot in tender['lots'] if lot['status'] == "complete"]):
                            logger.info('{} sync: Found multilot tender {} in status {}'.format(direction.capitalize(), tender['id'], tender['status']),
                                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_FOUND_MULTILOT_COMPLETE}, {"TENDER_ID": tender['id']}))
                            yield tender
                    elif tender['status'] == "complete":
                        logger.info('{} sync: Found tender in complete status {}'.format(direction.capitalize(), tender['id']),
                                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_FOUND_NOLOT_COMPLETE}, {"TENDER_ID": tender['id']}))
                        yield tender
                else:
                    logger.debug('{} sync: Skipping tender {} in status {}'.format(direction.capitalize(), tender['id'], tender['status']),
                                 extra=journal_context(params={"TENDER_ID": tender['id']}))

            logger.info('Sleep {} sync...'.format(direction), extra=journal_context({"MESSAGE_ID": DATABRIDGE_SYNC_SLEEP}))
            gevent.sleep(delay)
            logger.info('Restore {} sync'.format(direction), extra=journal_context({"MESSAGE_ID": DATABRIDGE_SYNC_RESUME}))
            logger.debug('{} {}'.format(direction, params))
            response = self.tenders_sync_client.sync_tenders(params, extra_headers={'X-Client-Request-ID': generate_req_id()})

    def _put_tender_in_cache_by_contract(self, contract, tender_id):
        dateModified = self.basket.get(contract['id'])
        if dateModified:
            # TODO: save tender in cache only if all active contracts are
            # handled successfully
            self.cache_db.put(tender_id, dateModified)
        self.basket.pop(contract['id'], None)

    def _get_tender_contracts(self):
        try:
            tender_to_sync = self.tenders_queue.get()
            tender = self.tenders_sync_client.get_tender(tender_to_sync['id'],
                                                         extra_headers={'X-Client-Request-ID': generate_req_id()})['data']
        except Exception, e:
            logger.warn('Fail to get tender info {}'.format(tender_to_sync['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, params={"TENDER_ID": tender_to_sync['id']}))
            logger.exception(e)
            logger.info('Put tender {} back to tenders queue'.format(tender_to_sync['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, params={"TENDER_ID": tender_to_sync['id']}))
            self.tenders_queue.put(tender_to_sync)
            gevent.sleep(self.on_error_delay)
        else:
            if 'contracts' not in tender:
                logger.warn('!!!No contracts found in tender {}'.format(tender['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, params={"TENDER_ID": tender['id']}))
                return
            for contract in tender['contracts']:
                if contract["status"] == "active":

                    self.basket[contract['id']] = tender_to_sync['dateModified']
                    try:
                        if not self.cache_db.has(contract['id']):
                            self.contracting_client_ro.get_contract(contract['id'])
                        else:
                            logger.info('Contract {} exists in local db'.format(contract['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_CACHED}, params={"CONTRACT_ID": contract['id']}))
                            self._put_tender_in_cache_by_contract(contract, tender_to_sync['id'])
                            continue
                    except ResourceNotFound:
                        logger.info('Sync contract {} of tender {}'.format(contract['id'], tender['id']), extra=journal_context(
                            {"MESSAGE_ID": DATABRIDGE_CONTRACT_TO_SYNC}, {"CONTRACT_ID": contract['id'], "TENDER_ID": tender['id']}))
                    except Exception, e:
                        logger.warn('Fail to contract existance {}'.format(contract['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, params={"TENDER_ID": tender_to_sync['id'],
                                                                                                                                                                "CONTRACT_ID": contract['id']}))
                        logger.exception(e)
                        logger.info('Put tender {} back to tenders queue'.format(tender_to_sync['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, params={"TENDER_ID": tender_to_sync['id'],
                                                                                                                                                                            "CONTRACT_ID": contract['id']}))
                        self.tenders_queue.put(tender_to_sync)
                        break
                    else:
                        self.cache_db.put(contract['id'], True)
                        logger.info('Contract exists {}'.format(contract['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_CONTRACT_EXISTS},
                                                                                                       {"TENDER_ID": tender_to_sync['id'], "CONTRACT_ID": contract['id']}))
                        self._put_tender_in_cache_by_contract(contract, tender_to_sync['id'])
                        continue

                    contract['tender_id'] = tender['id']
                    contract['procuringEntity'] = tender['procuringEntity']
                    if tender.get('mode'):
                        contract['mode'] = tender['mode']

                    if not contract.get('items'):
                        logger.info('Copying contract {} items'.format(contract['id']), extra=journal_context({"MESSAGE_ID": DATABRIDGE_COPY_CONTRACT_ITEMS},
                                                                                                              {"CONTRACT_ID": contract['id'], "TENDER_ID": tender_to_sync['id']}))
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
                                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, params={"CONTRACT_ID": contract['id'], "TENDER_ID": tender['id']}))
                        else:
                            logger.debug('Copying all tender {} items into contract {}'.format(tender['id'], contract['id']),
                                         extra=journal_context({"MESSAGE_ID": DATABRIDGE_COPY_CONTRACT_ITEMS}, params={"CONTRACT_ID": contract['id'], "TENDER_ID": tender['id']}))
                            contract['items'] = tender['items']

                    if not contract.get('items'):
                        logger.warn('Contact {} of tender {} does not contain items info'.format(contract['id'], tender['id']),
                                    extra=journal_context({"MESSAGE_ID": DATABRIDGE_MISSING_CONTRACT_ITEMS},
                                                          {"CONTRACT_ID": contract['id'], "TENDER_ID": tender['id']}))

                    for item in contract.get('items', []):
                        if 'deliveryDate' in item and item['deliveryDate'].get('startDate') and item['deliveryDate'].get('endDate'):
                            if item['deliveryDate']['startDate'] > item['deliveryDate']['endDate']:
                                logger.info("Found dates missmatch {} and {}".format(item['deliveryDate']['startDate'], item['deliveryDate']['endDate']),
                                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, params={"CONTRACT_ID": contract['id'], "TENDER_ID": tender['id']}))
                                del item['deliveryDate']['startDate']
                                logger.info("startDate value cleaned.",
                                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, params={"CONTRACT_ID": contract['id'], "TENDER_ID": tender['id']}))

                    self.handicap_contracts_queue.put(contract)

    def get_tender_contracts(self):
        while True:
            try:
                self._get_tender_contracts()
            except Exception, e:
                logger.warn("Fail to handle tender contracts", extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, {}))
                logger.exception(e)
                gevent.sleep(self.on_error_delay)
            gevent.sleep(0)

    def prepare_contract_data(self):
        while True:
            contract = self.handicap_contracts_queue.get()
            try:
                logger.info("Getting extra info for tender {}".format(contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_GET_EXTRA_INFO}, {"TENDER_ID": contract['tender_id'], "CONTRACT_ID": contract['id']}))
                tender_data = self.get_tender_credentials(contract['tender_id'])
                assert 'owner' in tender_data.data
                assert 'tender_token' in tender_data.data
            except Exception, e:
                logger.warn("Can't get tender credentials {}".format(contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, {"TENDER_ID": contract['tender_id'], "CONTRACT_ID": contract['id']}))
                logger.exception(e)
                self.handicap_contracts_queue.put(contract)
                gevent.sleep(self.on_error_delay)
            else:
                logger.debug("Got extra info for tender {}".format(contract['tender_id']),
                             extra=journal_context({"MESSAGE_ID": DATABRIDGE_GOT_EXTRA_INFO}, {"TENDER_ID": contract['tender_id'], "CONTRACT_ID": contract['id']}))
                data = tender_data.data
                contract['owner'] = data['owner']
                contract['tender_token'] = data['tender_token']
                self.contracts_put_queue.put(contract)
            gevent.sleep(0)

    def put_contracts(self):
        while True:
            contract = self.contracts_put_queue.get()
            try:
                logger.info("Creating contract {} of tender {}".format(contract['id'], contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_CONTRACT}, {"CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
                data = {"data": contract.toDict()}
                self.contracting_client.create_contract(data)
                logger.info("Successfully created contract {} of tender {}".format(contract['id'], contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CONTRACT_CREATED}, {"CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
            except Exception, e:
                logger.info("Unsuccessful put for contract {0} of tender {1}".format(contract['id'], contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, {"CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
                logger.exception(e)
                logger.info("Schedule retry for contract {0}".format(contract['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_RETRY_CREATE}, {"CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
                self.contracts_retry_put_queue.put(contract)
            else:
                self.cache_db.put(contract['id'], True)
                self._put_tender_in_cache_by_contract(contract, contract['tender_id'])

            gevent.sleep(0)

    @retry(stop_max_attempt_number=15, wait_exponential_multiplier=1000 * 60)
    def _put_with_retry(self, contract):
        try:
            data = {"data": contract.toDict()}
            logger.info("Creating contract {} of tender {}".format(contract['id'], contract['tender_id']),
                        extra=journal_context({"MESSAGE_ID": DATABRIDGE_CREATE_CONTRACT}, {"CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
            self.contracting_client.create_contract(data)
        except Exception, e:
            logger.exception(e)
            raise

    def retry_put_contracts(self):
        while True:
            try:
                contract = self.contracts_retry_put_queue.get()
                self._put_with_retry(contract)
                logger.info("Successfully created contract {} of tender {}".format(contract['id'], contract['tender_id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_CONTRACT_CREATED}, {"CONTRACT_ID": contract['id'], "TENDER_ID": contract['tender_id']}))
            except:
                logger.warn("Can't create contract {}".format(contract['id']),  extra=journal_context({"MESSAGE_ID": DATABRIDGE_EXCEPTION}, {"TENDER_ID": contract['tender_id'], "CONTRACT_ID": contract['id']}))
            else:
                self.cache_db.put(contract['id'], True)
                self._put_tender_in_cache_by_contract(contract, contract['tender_id'])
            gevent.sleep(0)

    def get_tender_contracts_forward(self):
        logger.info('Start forward data sync worker...')
        params = {'opt_fields': 'status,lots', 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="forward"):
                logger.info('Forward sync: Put tender {} to process...'.format(tender_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_PROCESS}, {"TENDER_ID": tender_data['id']}))
                self.tenders_queue.put(tender_data)
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Forward worker died!', extra=journal_context({"MESSAGE_ID": DATABRIDGE_WORKER_DIED}, {}))
            logger.exception(e)
        else:
            logger.warn('Forward data sync finished!', extra=journal_context({"MESSAGE_ID": DATABRIDGE_WORKER_DIED}, {}))  # Should never happen!!!

    def get_tender_contracts_backward(self):
        logger.info('Start backward data sync worker...')
        params = {'opt_fields': 'status,lots', 'descending': 1, 'mode': '_all_'}
        try:
            for tender_data in self.get_tenders(params=params, direction="backward"):
                stored = self.cache_db.get(tender_data['id'])
                if stored and stored == tender_data['dateModified']:
                    logger.info('Tender {} not modified from last check. Skipping'.format(tender_data['id']), extra=journal_context(
                        {"MESSAGE_ID": DATABRIDGE_SKIP_NOT_MODIFIED}, {"TENDER_ID": tender_data['id']}))
                    continue
                logger.info('Backward sync: Put tender {} to process...'.format(tender_data['id']),
                            extra=journal_context({"MESSAGE_ID": DATABRIDGE_TENDER_PROCESS}, {"TENDER_ID": tender_data['id']}))
                self.tenders_queue.put(tender_data)
        except Exception, e:
            # TODO reset queues and restart sync
            logger.warn('Backward worker died!', extra=journal_context({"MESSAGE_ID": DATABRIDGE_WORKER_DIED}, {}))
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


    def _start_synchronization_workers(self):
        logger.info('Starting forward and backward sync workers')
        self.jobs = [gevent.spawn(self.get_tender_contracts_backward),
                     gevent.spawn(self.get_tender_contracts_forward)]

    def _restart_synchronization_workers(self):
        logger.warn("Restarting synchronization", extra=journal_context({"MESSAGE_ID": DATABRIDGE_RESTART}, {}))
        for j in self.jobs:
            j.kill()
        self._start_synchronization_workers()

    def _start_contract_sculptors(self):
        self.immortal_jobs = {'get_tender_contracts': gevent.spawn(self.get_tender_contracts),
                              'prepare_contract_data': gevent.spawn(self.prepare_contract_data),
                              'put_contracts': gevent.spawn(self.put_contracts),
                              'retry_put_contracts': gevent.spawn(self.retry_put_contracts)}

    def run(self):
        logger.info('Start Contracting Data Bridge', extra=journal_context({"MESSAGE_ID": DATABRIDGE_START}, {}))
        self._start_contract_sculptors()
        self._start_synchronization_workers()
        backward_worker, forward_worker = self.jobs
        counter = 0

        try:
            while True:
                gevent.sleep(self.jobs_watcher_delay)
                if counter == 20:
                    logger.info(
                        'Current state: Tenders to process {}; Unhandled contracts {}; Contracts to create {}; Retrying to create {}'.format(
                        self.tenders_queue.qsize(), self.handicap_contracts_queue.qsize(), self.contracts_put_queue.qsize(),
                        self.contracts_retry_put_queue.qsize()))
                    counter = 0
                counter += 1
                if forward_worker.dead or (backward_worker.dead and not backward_worker.successful()):
                    self._restart_synchronization_workers()
                    backward_worker, forward_worker = self.jobs

                for name, job in self.immortal_jobs.items():
                    if job.dead:
                        logger.warn('Restarting {} worker'.format(name))
                        self.immortal_jobs[name] = gevent.spawn(getattr(self, name))

        except KeyboardInterrupt:
            logger.info('Exiting...')
            gevent.killall(self.jobs, timeout=5)
            gevent.killall(self.immortal_jobs, timeout=5)
        except Exception, e:
            logger.exception(e)


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
