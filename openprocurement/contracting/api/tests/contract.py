# -*- coding: utf-8 -*-
import unittest
from uuid import uuid4
from copy import deepcopy
from openprocurement.api import ROUTE_PREFIX
from openprocurement.contracting.api.models import Contract
from openprocurement.contracting.api.tests.base import (
    test_contract_data, BaseWebTest, BaseContractWebTest)
from openprocurement.api.models import get_now


class ContractTest(BaseWebTest):

    def test_simple_add_contract(self):
        u = Contract(test_contract_data)
        u.contractID = "UA-C"

        assert u.id == test_contract_data['id']
        assert u.rev is None

        u.store(self.db)

        assert u.id == test_contract_data['id']
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.contractID == fromdb['contractID']
        assert u.doc_type == "Contract"

        u.delete_instance(self.db)


class ContractResourceTest(BaseWebTest):
    """ contract resource test """

    def test_empty_listing(self):
        response = self.app.get('/contracts')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertNotIn('{\n    "', response.body)
        self.assertNotIn('callback({', response.body)
        self.assertEqual(response.json['next_page']['offset'], '')
        self.assertNotIn('prev_page', response.json)

        response = self.app.get('/contracts?opt_jsonp=callback')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertNotIn('{\n    "', response.body)
        self.assertIn('callback({', response.body)

        response = self.app.get('/contracts?opt_pretty=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)
        self.assertNotIn('callback({', response.body)

        response = self.app.get('/contracts?opt_jsonp=callback&opt_pretty=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('{\n    "', response.body)
        self.assertIn('callback({', response.body)

        response = self.app.get('/contracts?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertIn('descending=1', response.json['next_page']['uri'])
        self.assertIn('limit=10', response.json['next_page']['uri'])
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertIn('limit=10', response.json['prev_page']['uri'])

        response = self.app.get('/contracts?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertEqual(response.json['next_page']['offset'], '')
        self.assertNotIn('prev_page', response.json)

        response = self.app.get('/contracts?feed=changes&offset=0', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Offset expired/invalid', u'location': u'params', u'name': u'offset'}
        ])

        response = self.app.get('/contracts?feed=changes&descending=1&limit=10')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertIn('descending=1', response.json['next_page']['uri'])
        self.assertIn('limit=10', response.json['next_page']['uri'])
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertIn('limit=10', response.json['prev_page']['uri'])

    def test_listing(self):
        response = self.app.get('/contracts')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        contracts = []

        for i in range(3):
            offset = get_now().isoformat()
            data = deepcopy(test_contract_data)
            data['id'] = uuid4().hex
            response = self.app.post_json('/contracts', {'data': data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            contracts.append(response.json['data'])

        response = self.app.get('/contracts')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in contracts]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                         set([i['dateModified'] for i in contracts]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in contracts]))

        response = self.app.get('/contracts?offset={}'.format(offset))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/contracts?limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('prev_page', response.json)
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/contracts', params=[('opt_fields', 'contractID')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'contractID']))
        self.assertIn('opt_fields=contractID', response.json['next_page']['uri'])

        response = self.app.get('/contracts?descending=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in contracts]))
        self.assertEqual([i['dateModified'] for i in response.json['data']],
                         sorted([i['dateModified'] for i in contracts], reverse=True))

        response = self.app.get('/contracts?descending=1&limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        test_contract_data2 = deepcopy(test_contract_data)
        test_contract_data2['mode'] = 'test'
        response = self.app.post_json('/contracts', {'data': test_contract_data2})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.get('/contracts?mode=test')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/contracts?mode=_all_')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 4)

    def test_listing_changes(self):
        response = self.app.get('/contracts?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        contracts = []

        for i in range(3):
            data = deepcopy(test_contract_data)
            data['id'] = uuid4().hex
            response = self.app.post_json('/contracts', {'data': data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            contracts.append(response.json['data'])

        response = self.app.get('/contracts?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in contracts]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                         set([i['dateModified'] for i in contracts]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in contracts]))

        response = self.app.get('/contracts?feed=changes&limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('prev_page', response.json)
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/contracts?feed=changes', params=[('opt_fields', 'contractID')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'contractID']))
        self.assertIn('opt_fields=contractID', response.json['next_page']['uri'])

        response = self.app.get('/contracts?feed=changes&descending=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in contracts]))
        self.assertEqual([i['dateModified'] for i in response.json['data']],
                         sorted([i['dateModified'] for i in contracts], reverse=True))

        response = self.app.get('/contracts?feed=changes&descending=1&limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        test_contract_data2 = test_contract_data.copy()
        test_contract_data2['mode'] = 'test'
        response = self.app.post_json('/contracts', {'data': test_contract_data2})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.get('/contracts?feed=changes&mode=test')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/contracts?feed=changes&mode=_all_')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 4)

    def test_get_contract(self):
        response = self.app.get('/contracts')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/contracts', {'data': test_contract_data})
        self.assertEqual(response.status, '201 Created')
        contract = response.json['data']
        self.assertEqual(contract['id'], test_contract_data['id'])

        response = self.app.get('/contracts/{}'.format(contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], contract)

        response = self.app.get('/contracts/{}?opt_jsonp=callback'.format(contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('callback({"data": {"', response.body)

        response = self.app.get('/contracts/{}?opt_pretty=1'.format(contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "data": {\n        "', response.body)

    def test_not_found(self):
        response = self.app.get('/contracts')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/contracts/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'contract_id'}
        ])

        response = self.app.patch_json(
            '/contracts/some_id', {'data': {}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'contract_id'}
        ])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractTest))
    suite.addTest(unittest.makeSuite(ContractResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
