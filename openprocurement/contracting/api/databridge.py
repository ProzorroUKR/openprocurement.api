from gevent import monkey
monkey.patch_all()

try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

import time
import logging
import logging.config
import os
import argparse

from copy import deepcopy
from retrying import retry
from uuid import uuid4

import gevent
from gevent.queue import Queue

from openprocurement_client.client import TendersClient
from openprocurement_client.contract import ContractingClient
from openprocurement_client.client import ResourceNotFound
from yaml import load


logger = logging.getLogger("openprocurement.contracting.api.databridge")
# logger = logging.getLogger(__name__)


def generate_req_id():
    return b'contracting-data-bridge-req-' + str(uuid4()).encode('ascii')


class ContractingDataBridge(object):
    """ Contracting Data Bridge """

    def __init__(self, config):
        super(ContractingDataBridge, self).__init__()
        self.config = config
        self.contracting_client = ContractingClient(
            self.config_get('api_token'),
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version')
        )
        params = {'opt_fields': 'status,lots',
                  'mode': '_all_'}
        self.tenders_client_forward = TendersClient(
            '',
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
            params=params
        )

        params_desc = deepcopy(params)
        params_desc['descending'] = 1
        self.tenders_client_backward = TendersClient(
            '',
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
            params=params_desc
        )

        self.client = TendersClient(
            self.config_get('api_token'),
            host_url=self.config_get('tenders_api_server'),
            api_version=self.config_get('tenders_api_version'),
        )

        self.tenders_queue = Queue()
        self.handicap_contracts_queue = Queue()
        self.contracts_put_queue = Queue()
        self.contracts_retry_put_queue = Queue()

    def config_get(self, name):
        return self.config.get('main').get(name)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def get_tender_credentials(self, tender_id):
        return self.client.extract_credentials(tender_id)

    def get_tenders(self, client):
        while True:
            request_id = generate_req_id()
            client.headers.update({'X-Client-Request-ID': request_id})
            tenders_list = list(client.get_tenders())
            delay = 101
            if tenders_list:
                delay = 15
                logger.info("Client params: {}".format(client.params))
            for tender in tenders_list:
                if tender['status'] in ("active.qualification",
                                        "active.awarded", "complete"):
                    if hasattr(tender, "lots"):
                        if any([1 for lot in tender['lots'] if lot['status'] == "complete"]):
                            logger.info('found multilot tender {} in status {}'.format(tender['id'], tender['status']))
                            yield tender
                    elif tender['status'] == "complete":
                        logger.info('Found tender in complete status {}'.format(tender['id']))
                        yield tender
                else:
                    logger.debug('Skipping tender {} in status {}'.format(tender['id'], tender['status']))

            logger.info('Sleep...')
            time.sleep(delay)

    def get_tender_contracts(self):
        while True:
            request_id = generate_req_id()
            self.tenders_client_backward.headers.update({'X-Client-Request-ID': request_id})
            tender = self.tenders_client_backward.get_tender(self.tenders_queue.get()['id'])['data']
            if 'contracts' not in tender:
                logger.warn('!!!No contracts found in tender {}'.format(tender['id']))
                continue
            for contract in tender['contracts']:
                if contract["status"] == "active":
                    try:
                        self.contracting_client.get_contract(contract['id'])
                    except ResourceNotFound:
                        logger.info('Sync contract {} of tender {}'.format(contract['id'], tender['id']))
                    else:
                        logger.info('Contract exists {}'.format(contract['id']))
                        continue

                    contract['tender_id'] = tender['id']
                    contract['procuringEntity'] = tender['procuringEntity']
                    self.handicap_contracts_queue.put(contract)

    def prepare_contract_data(self):
        while True:
            contract = self.handicap_contracts_queue.get()
            try:
                logger.info("Getting extra info for tender {}".format(contract['tender_id']))
                tender_data = self.get_tender_credentials(contract['tender_id'])
            except Exception, e:
                logger.info("Can't get tender credentials {}".format(contract['tender_id']))
                self.handicap_contracts_queue.put(contract)
            else:
                logger.debug("Got extra info for tender {}".format(
                    contract['tender_id']))
                data = tender_data.data
                if data.get('mode'):
                    contract['mode'] = data['mode']
                contract['owner'] = data['owner']
                contract['tender_token'] = data['tender_token']
                del contract['status']  # create contract in 'draft' status
                self.contracts_put_queue.put(contract)
            gevent.sleep(0)

    def put_contracts(self):
        while True:
            contract = self.contracts_put_queue.get()
            try:
                logger.info("Creating contract {} of tender {}".format(
                    contract['id'], contract['tender_id']))
                data = {"data": contract.toDict()}
                self.contracting_client.create_contract(data)
            except Exception, e:
                logger.info("Unsuccessful put for contract {0} of tender {1}".format(
                    contract['id'], contract['tender_id']))
                logger.info("Schedule retry for contract {0}".format(contract['id']))
                self.contracts_retry_put_queue.put(contract)
            gevent.sleep(0)

    @retry(stop_max_attempt_number=15, wait_exponential_multiplier=1000 * 60)
    def _put_with_retry(self, contract):
        try:
            data = {"data": contract.toDict()}
            logger.info("Creating contract {} of tender {}".format(
                contract['id'], contract['tender_id']))
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
                logger.warn("can't create contract {}".format(contract))
            else:
                self.contracts_retry_put_queue.get()
            gevent.sleep(0)

    def get_tender_contracts_forward(self):
        logger.info('Start forward data sync...')
        for tender_data in self.get_tenders(self.tenders_client_forward):
            logger.info('Forward sync: Put tender to process...')
            self.tenders_queue.put(tender_data)

    def get_tender_contracts_backward(self):
        logger.info('Start backward data sync...')
        for tender_data in self.get_tenders(self.tenders_client_backward):
            logger.info('Backward sync: Put tender to process...')
            self.tenders_queue.put(tender_data)

    def run(self):
        try:
            logger.info('Start Contracting Data Bridge')
            jobs = [gevent.spawn(self.get_tender_contracts_forward),
                    gevent.spawn(self.get_tender_contracts_backward),
                    gevent.spawn(self.get_tender_contracts),
                    gevent.spawn(self.prepare_contract_data),
                    gevent.spawn(self.put_contracts),
                    gevent.spawn(self.retry_put_contracts),
                    ]
            gevent.joinall(jobs)
        except Exception, e:
            logger.exception(e)
            logger.info('Exiting...')
            gevent.killall(jobs)


def main():
    parser = argparse.ArgumentParser(description='Contracting Data Bridge')
    parser.add_argument('config', type=str, help='Path to configuration file')
    params = parser.parse_args()
    if os.path.isfile(params.config):
        with open(params.config) as config_file_obj:
            config = load(config_file_obj.read())
        logging.config.dictConfig(config)
        ContractingDataBridge(config).run()
    else:
        logger.info('Invalid configuration file. Exiting...')


if __name__ == "__main__":
    main()
