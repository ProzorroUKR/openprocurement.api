# -*- coding: utf-8 -*-
import unittest
from uuid import uuid4
from copy import deepcopy
from datetime import timedelta
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
        assert u.doc_id == test_contract_data['id']
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

    def test_create_contract_invalid(self):
        request_path = '/contracts'
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                 u"Content-Type header should be one of ['application/json']", u'location': u'header',
             u'name': u'Content-Type'}
        ])

        response = self.app.post(
            request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
             u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
             u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
             u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'data': []}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
             u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'data': {
            'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

    def test_create_contract_generated(self):
        data = test_contract_data.copy()
        data.update({'id': uuid4().hex, 'doc_id': uuid4().hex, 'contractID': uuid4().hex})
        response = self.app.post_json('/contracts', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        contract = response.json['data']
        self.assertEqual(set(contract), set([
            u'id', u'dateModified', u'contractID', u'status', u'suppliers',
            u'contractNumber', u'period', u'dateSigned', u'value', u'awardID',
            u'items', u'owner', u'tender_id']))
        self.assertEqual(data['id'], contract['id'])
        self.assertNotEqual(data['doc_id'], contract['id'])
        self.assertEqual(data['contractID'], contract['contractID'])

    def test_create_contract(self):
        response = self.app.get('/contracts')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/contracts', {"data": test_contract_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        contract = response.json['data']
        self.assertEqual(contract['status'], 'draft')

        response = self.app.get('/contracts/{}'.format(contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set(contract))
        self.assertEqual(response.json['data'], contract)

        data = deepcopy(test_contract_data)
        data['id'] = uuid4().hex
        response = self.app.post_json('/contracts?opt_jsonp=callback', {"data": data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('callback({"', response.body)

        data['id'] = uuid4().hex
        response = self.app.post_json('/contracts?opt_pretty=1', {"data": data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)

        data['id'] = uuid4().hex
        response = self.app.post_json('/contracts', {"data": data, "options": {"pretty": True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)

        # broker has no permissions to create contract
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/contracts', {"data": test_contract_data}, status=403)
        self.assertEqual(response.status, '403 Forbidden')


class ContractResource4BrokersTest(BaseContractWebTest):
    """ contract resource test """
    initial_auth = ('Basic', ('broker', ''))

    def test_contract_status_change(self):
        tender_token = self.initial_data['tender_token']

        response = self.app.get('/contracts/{}'.format(self.contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "draft")

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], tender_token),
                                       {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        response = self.app.patch_json('/contracts/{}/credentials?acc_token={}'.format(self.contract['id'], tender_token),
                                       {'data': ''})
        self.assertEqual(response.status, '200 OK')
        token = response.json['access']['token']

        # draft > active allowed
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        # active > draft not allowed
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"status": "draft"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        # active > terminated allowed
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"status": "terminated"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'terminated')

        # terminated > active not allowed
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        # terminated > draft not allowed
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"status": "draft"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        # draft > terminated allowed ?
        data = deepcopy(self.initial_data)
        data['id'] = uuid4().hex
        self.app.authorization = ('Basic', ('contracting', ''))
        response = self.app.post_json('/contracts', {"data": data})
        self.app.authorization = self.initial_auth
        self.assertEqual(response.status, '201 Created')
        contract = response.json['data']
        self.assertEqual(contract['status'], 'draft')

        response = self.app.patch_json('/contracts/{}/credentials?acc_token={}'.format(contract['id'], data['tender_token']),
                                       {'data': ''})
        self.assertEqual(response.status, '200 OK')
        token = response.json['access']['token']

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(contract['id'], token),
                                       {"data": {"status": "terminated"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'terminated')

    def test_patch_tender_contract(self):
        response = self.app.patch_json('/contracts/{}'.format(self.contract['id']), {"data": {"title": "New Title"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        tender_token = self.initial_data['tender_token']
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], tender_token),
                                       {"data": {"title": "New Title"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        response = self.app.patch_json('/contracts/{}/credentials?acc_token={}'.format(self.contract['id'], tender_token),
                                       {'data': ''})
        self.assertEqual(response.status, '200 OK')
        token = response.json['access']['token']

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"title": "New Title"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "data", "description": "Can't update contract in current (draft) status"}])

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"title": "New Title"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], "New Title")

        # response = self.app.patch_json('/contracts/{}?acc_token={}'.format(contract['id'], token),
                                       # {"data": {"value": {"currency": "USD"}}})
        # response = self.app.patch_json('/contracts/{}?acc_token={}'.format(contract['id'], token),
                                       # {"data": {"value": {"valueAddedTaxIncluded": False}}})

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"value": {"amount": 238}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        custom_period_start_date = get_now().isoformat()
        custom_period_end_date = (get_now() + timedelta(days=3)).isoformat()
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"period": {'startDate': custom_period_start_date,
                                                            'endDate': custom_period_end_date}}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"status": "terminated"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'terminated')

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract['id'], token),
                                       {"data": {"title": "fff"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        response = self.app.patch_json('/contracts/some_id', {"data": {"status": "active"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.get('/contracts/{}'.format(self.contract['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "terminated")
        self.assertEqual(response.json['data']["value"]['amount'], 238)
        self.assertEqual(response.json['data']['period']['startDate'], custom_period_start_date)
        self.assertEqual(response.json['data']['period']['endDate'], custom_period_end_date)


class ContractCredentialsTest(BaseContractWebTest):
    """ Contract credentials tests """

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_contract_data

    def test_get_credentials(self):
        response = self.app.get('/contracts/{0}/credentials?acc_token={1}'.format(self.contract_id,
                                                                                  self.initial_data['tender_token']), status=405)
        self.assertEqual(response.status, '405 Method Not Allowed')

    def test_generate_credentials(self):
        tender_token = self.initial_data['tender_token']
        response = self.app.patch_json('/contracts/{0}/credentials?acc_token={1}'.format(self.contract_id, tender_token), {'data': ''})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['id'], self.initial_data['id'])
        self.assertNotIn('tender_token', response.json['data'])
        self.assertNotIn('owner_token', response.json['data'])
        self.assertEqual(response.json['data']['owner'], 'broker')
        self.assertEqual(len(response.json['access']['token']), 32)
        token1 = response.json['access']['token']

        # try second time generation
        response = self.app.patch_json('/contracts/{0}/credentials?acc_token={1}'.format(self.contract_id, tender_token), {'data': ''})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['id'], self.initial_data['id'])
        self.assertEqual(len(response.json['access']['token']), 32)
        token2 = response.json['access']['token']
        self.assertNotEqual(token1, token2)

        # first access token is non-workable
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, token1),
                                       {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

        # activate contract and try to generate credentials
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, token2),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/contracts/{0}/credentials?acc_token={1}'.format(self.contract_id, tender_token),
                                       {'data': ''}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [
            {u'description': u"Can't generate credentials in current (active) contract status", u'location': u'body', u'name': u'data'}])

        # terminated contract is also protected
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, token2),
                                       {"data": {"status": "terminated"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/contracts/{0}/credentials?acc_token={1}'.format(self.contract_id, tender_token),
                                       {'data': ''}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [
            {u'description': u"Can't generate credentials in current (terminated) contract status", u'location': u'body', u'name': u'data'}])

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractTest))
    suite.addTest(unittest.makeSuite(ContractResourceTest))
    suite.addTest(unittest.makeSuite(ContractCredentialsTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
