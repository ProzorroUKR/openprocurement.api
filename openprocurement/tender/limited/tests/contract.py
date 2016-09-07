# -*- coding: utf-8 -*-
import unittest
import time
from iso8601 import parse_date
from datetime import timedelta

from openprocurement.api.models import get_now, SANDBOX_MODE
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest, test_tender_data, test_tender_negotiation_data,
    test_tender_negotiation_quick_data, test_organization, test_lots)


class TenderContractResourceTest(BaseTenderContentWebTest):
    initial_status = 'active'
    initial_data = test_tender_data
    initial_bids = None  # test_bids

    def create_award(self):
        # Create award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization], 'status': 'pending',
                                                          'qualified': True, 'value': {"amount": 469,
                                                                                       "currency": "UAH",
                                                                                       "valueAddedTaxIncluded": True}}})
        award = response.json['data']
        self.award_id = award['id']
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {"data": {"status": "active"}})

    def setUp(self):
        super(TenderContractResourceTest, self).setUp()
        self.create_award()

    def test_create_tender_contract_invalid(self):
        # This can not be, but just in case check
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/some_id/contracts',
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award_id}},
                                      status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/contracts?acc_token={}'.format(self.tender_id, self.tender_token)

        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']",
             u'location': u'header',
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

        response = self.app.post_json(
            request_path, {'not_data': {}}, status=422)
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

        response = self.app.post_json(request_path, {'data': {'awardID': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'awardID should be one of awards'], u'location': u'body', u'name': u'awardID'}
        ])

    def test_create_tender_contract_with_token(self):
        # This can not be, but just in case check
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/contracts'.format(self.tender_id),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        contract = response.json['data']
        self.assertIn('id', contract)
        self.assertIn(contract['id'], response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                       {"data": {"status": "terminated"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "terminated")

        response = self.app.patch_json('/tenders/{}/contracts/{}'.format(self.tender_id, contract['id']),
                                       {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update contract status")

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            if i.get('complaintPeriod', {}):  # works for negotiation tender
                i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, contract['id'], self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'complete')

        response = self.app.post_json('/tenders/{}/contracts'.format(self.tender_id),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award_id}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')

    def test_create_tender_contract(self):
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = response.json['data'][0]['id']

        response = self.app.post_json('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award_id}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')

        # at next steps we test to create contract in 'complete' tender status
        # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            if i.get('complaintPeriod', {}):  # reporting procedure does not have complaintPeriod
                i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'complete')

        response = self.app.post_json('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award_id}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')

        # at next steps we test to create contract in 'cancelled' tender status
        response = self.app.post_json('/tenders?acc_token={}',
                                      {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender_id = response.json['data']['id']
        tender_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            tender_id, tender_token), {'data': {'reason': 'cancellation reason', 'status': 'active'}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'cancelled')

        response = self.app.post_json('/tenders/{}/contracts?acc_token={}'.format(tender_id, tender_token),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award_id}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')

    def test_patch_tender_contract(self):
        response = self.app.get('/tenders/{}/contracts'.format(
                self.tender_id))
        self.contract_id = response.json['data'][0]['id']

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"value": {"currency": "USD"}}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can\'t update currency for contract value")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"value": {"valueAddedTaxIncluded": False}}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can\'t update valueAddedTaxIncluded for contract value")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"value": {"amount": 501}}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Value amount should be less or equal to awarded amount (469.0)")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"value": {"amount": 238}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertIn("dateSigned", response.json['data'])

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "cancelled"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update contract in current (complete) tender status")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update contract in current (complete) tender status")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update contract in current (complete) tender status")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"awardID": "894917dc8b1244b6aab9ab0ad8c8f48a"}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')

        # at next steps we test to patch contract in 'cancelled' tender status
        response = self.app.post_json('/tenders?acc_token={}',
                                      {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender_id = response.json['data']['id']
        tender_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(tender_id, tender_token),
                                      {'data': {'suppliers': [test_organization], 'status': 'pending'}})
        award_id = response.json['data']['id']
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, tender_token),
                                       {"data": {'qualified': True, "status": "active"}})

        response = self.app.get('/tenders/{}/contracts'.format(tender_id))
        contract_id = response.json['data'][0]['id']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active'}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'cancelled')

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            tender_id, contract_id, tender_token),
            {"data": {"awardID": "894917dc8b1244b6aab9ab0ad8c8f48a"}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            tender_id, contract_id, tender_token), {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update contract in current (cancelled) tender status")

        response = self.app.patch_json('/tenders/{}/contracts/some_id?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": "active"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/contracts/some_id', {"data": {"status": "active"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/contracts/{}'.format(self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["value"]['amount'], 238)

    def test_tender_contract_signature_date(self):
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.assertNotIn("dateSigned", response.json['data'][0])
        self.contract_id = response.json['data'][0]['id']

        one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"dateSigned": one_hour_in_furure}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'],
                         [{u'description': [u"Contract signature date can't be in the future"],
                           u'location': u'body',
                           u'name': u'dateSigned'}])

        custom_signature_date = get_now().isoformat()
        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"dateSigned": custom_signature_date}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["dateSigned"], custom_signature_date)
        self.assertIn("dateSigned", response.json['data'])

    def test_get_tender_contract(self):
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = response.json['data'][0]['id']

        response = self.app.get('/tenders/{}/contracts/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.get('/tenders/some_id/contracts/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_contracts(self):
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.get('/tenders/some_id/contracts', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_award_id_change_is_not_allowed(self):
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {"data": {"status": "cancelled"}})
        old_award_id = self.award_id

        # upload new award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'suppliers': [test_organization]}})
        award = response.json['data']
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {"data": {'qualified': True, "status": "active"}})
        response = self.app.get('/tenders/{}/contracts'.format(
                self.tender_id))
        contract = response.json['data'][-1]
        self.assertEqual(contract['awardID'], award['id'])
        self.assertNotEqual(contract['awardID'], old_award_id)

        # try to update awardID value
        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, contract['id'], self.tender_token), {"data": {"awardID": old_award_id}})
        response = self.app.get('/tenders/{}/contracts'.format(
                self.tender_id))
        contract = response.json['data'][-1]
        self.assertEqual(contract['awardID'], award['id'])
        self.assertNotEqual(contract['awardID'], old_award_id)


class TenderNegotiationContractResourceTest(TenderContractResourceTest):
    initial_data = test_tender_negotiation_data
    stand_still_period_days = 10

    def test_patch_tender_contract(self):
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = response.json['data'][0]['id']

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"status": "active"}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn("Can't sign contract before stand-still period end (", response.json['errors'][0]["description"])

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 1)
        award = response.json['data'][0]
        start = parse_date(award['complaintPeriod']['startDate'])
        end = parse_date(award['complaintPeriod']['endDate'])
        delta = end - start
        self.assertEqual(delta.days, 0 if SANDBOX_MODE else self.stand_still_period_days)

        # at next steps we test to patch contract in 'complete' tender status
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"value": {"currency": "USD"}}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can\'t update currency for contract value")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"value": {"valueAddedTaxIncluded": False}}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can\'t update valueAddedTaxIncluded for contract value")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"value": {"amount": 501}}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Value amount should be less or equal to awarded amount (469.0)")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"value": {"amount": 238}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertIn(u"dateSigned", response.json['data'])

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "cancelled"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update contract in current (complete) tender status")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update contract in current (complete) tender status")

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update contract in current (complete) tender status")

        # at next steps we test to patch contract in 'cancelled' tender status
        response = self.app.post_json('/tenders?acc_token={}', {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender_id = response.json['data']['id']
        tender_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(tender_id, tender_token),
                                      {'data': {'suppliers': [test_organization], 'status': 'pending'}})
        award_id = response.json['data']['id']
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, tender_token),
                                       {"data": {'qualified': True, "status": "active"}})

        response = self.app.get('/tenders/{}/contracts'.format(tender_id))
        contract_id = response.json['data'][0]['id']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active'}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'cancelled')

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            tender_id, contract_id, tender_token),
            {"data": {"awardID": "894917dc8b1244b6aab9ab0ad8c8f48a"}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            tender_id, contract_id, tender_token), {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update contract in current (cancelled) tender status")

        response = self.app.patch_json('/tenders/{}/contracts/some_id?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": "active"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/contracts/some_id', {"data": {"status": "active"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/contracts/{}'.format(self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

    def test_tender_contract_signature_date(self):
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.assertNotIn("dateSigned", response.json['data'][0])
        self.contract_id = response.json['data'][0]['id']

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"dateSigned": one_hour_in_furure}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'],
                         [{u'description': [u"Contract signature date can't be in the future"],
                           u'location': u'body',
                           u'name': u'dateSigned'}])

        before_stand_still = i['complaintPeriod']['startDate']
        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            {"data": {"dateSigned": before_stand_still}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'], [{u'description': [u'Contract signature date should be after award complaint period end date ({})'.format(i['complaintPeriod']['endDate'])], u'location': u'body', u'name': u'dateSigned'}])

        custom_signature_date = get_now().isoformat()
        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"dateSigned": custom_signature_date}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["dateSigned"], custom_signature_date)
        self.assertIn("dateSigned", response.json['data'])


class TenderNegotiationLotContractResourceTest(TenderNegotiationContractResourceTest):
    initial_data = test_tender_negotiation_data
    stand_still_period_days = 10

    def create_award(self):
        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'items': self.initial_data['items']}})

        # create lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot1 = response.json['data']
        self.lot1 = lot1

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'items': [{'relatedLot': lot1['id']}]
                                      }
                             })
        # Create award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization], 'status': 'pending',
                                                          'qualified': True, 'value': {"amount": 469,
                                                                                       "currency": "UAH",
                                                                                       "valueAddedTaxIncluded": True},
                                                          'lotID': lot1['id']}})
        award = response.json['data']
        self.award_id = award['id']
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {"data": {"status": "active"}})

    def test_award_id_change_is_not_allowed(self):
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {"data": {"status": "cancelled"}})
        old_award_id = self.award_id

        # upload new award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'suppliers': [test_organization],
                                                'lotID': self.lot1['id']}})
        award = response.json['data']
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {"data": {'qualified': True, "status": "active"}})
        response = self.app.get('/tenders/{}/contracts'.format(
                self.tender_id))
        contract = response.json['data'][-1]
        self.assertEqual(contract['awardID'], award['id'])
        self.assertNotEqual(contract['awardID'], old_award_id)

        # try to update awardID value
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, contract['id'], self.tender_token), {"data": {"awardID": old_award_id}})
        response = self.app.get('/tenders/{}/contracts'.format(
                self.tender_id))
        contract = response.json['data'][-1]
        self.assertEqual(contract['awardID'], award['id'])
        self.assertNotEqual(contract['awardID'], old_award_id)


class TenderNegotiationLot2ContractResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data
    stand_still_period_days = 10

    def setUp(self):
        super(TenderNegotiationLot2ContractResourceTest, self).setUp()
        self.create_award()

    def create_award(self):
        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'items': self.initial_data['items'] * 2}})

        # create lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot1 = response.json['data']
        self.lot1 = lot1

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot2 = response.json['data']
        self.lot2 = lot2

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'items': [{'relatedLot': lot1['id']},
                                                {'relatedLot': lot2['id']}]
                                      }
                             })
        # Create award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization], 'status': 'pending',
                                                          'qualified': True, 'value': {"amount": 469,
                                                                                       "currency": "UAH",
                                                                                       "valueAddedTaxIncluded": True},
                                                          'lotID': lot1['id']}})
        award = response.json['data']
        self.award1_id = award['id']
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award1_id, self.tender_token), {"data": {"status": "active"}})

        # Create another award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization], 'status': 'pending',
                                                          'qualified': True, 'value': {"amount": 469,
                                                                                       "currency": "UAH",
                                                                                       "valueAddedTaxIncluded": True},
                                                          'lotID': lot2['id']}})
        award = response.json['data']
        self.award2_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award2_id, self.tender_token), {"data": {"status": "active"}})

    def test_create_two_contract(self):
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract1_id = response.json['data'][0]['id']
        self.contract2_id = response.json['data'][1]['id']

        response = self.app.post_json('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award1_id}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')

        # at next steps we test to create contract in 'complete' tender status
        # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            if i.get('complaintPeriod', {}):  # reporting procedure does not have complaintPeriod
                i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract1_id, self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertNotEqual(response.json['data']['status'], 'complete')

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract2_id, self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'complete')

        response = self.app.post_json('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award1_id}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')

        # at next steps we test to create contract in 'cancelled' tender status
        response = self.app.post_json('/tenders?acc_token={}',
                                      {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender_id = response.json['data']['id']
        tender_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            tender_id, tender_token), {'data': {'reason': 'cancellation reason', 'status': 'active'}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'cancelled')

        response = self.app.post_json('/tenders/{}/contracts?acc_token={}'.format(tender_id, tender_token),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award1_id}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')


class TenderNegotiationQuickContractResourceTest(TenderNegotiationContractResourceTest):
    initial_data = test_tender_negotiation_quick_data
    stand_still_period_days = 5


class TenderNegotiationQuickLotContractResourceTest(TenderNegotiationLotContractResourceTest):
    initial_data = test_tender_negotiation_quick_data
    stand_still_period_days = 5


class TenderNegotiationQuickAccelerationTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_quick_data
    stand_still_period_days = 5
    accelerator = 'quick,accelerator=172800'  # 5 days=432000 sec; 432000/172800=2.5 sec
    time_sleep_in_sec = 3  # time which reduced

    def create_award(self):
        # Create award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization], 'status': 'pending'}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {"data": {'qualified': True, "status": "active"}})

    def setUp(self):
        super(TenderNegotiationQuickAccelerationTest, self).setUp()
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'procurementMethodDetails': self.accelerator}})
        self.assertEqual(response.status, '200 OK')
        self.create_award()

    @unittest.skipUnless(SANDBOX_MODE, "not supported accelerator")
    def test_create_tender_contract_negotination_quick(self):
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = response.json['data'][0]['id']

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertIn("Can't sign contract before stand-still period end (", response.json['errors'][0]["description"])

        time.sleep(self.time_sleep_in_sec)
        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')


class TenderNegotiationQuickLotAccelerationTest(TenderNegotiationQuickAccelerationTest):
    initial_data = test_tender_negotiation_quick_data
    stand_still_period_days = 5
    accelerator = 'quick,accelerator=172800'  # 5 days=432000 sec; 432000/172800=2.5 sec
    time_sleep_in_sec = 3  # time which reduced

    def create_award(self):
        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'items': self.initial_data['items'] * 2}})

        # create lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot1 = response.json['data']
        self.lot1 = lot1

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'items': [{'relatedLot': lot1['id']}]
                                      }
                             })
        # Create award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization], 'status': 'pending',
                                                          'qualified': True, 'value': {"amount": 469,
                                                                                       "currency": "UAH",
                                                                                       "valueAddedTaxIncluded": True},
                                                          'lotID': lot1['id']}})
        award = response.json['data']
        self.award_id = award['id']
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {"data": {"status": "active"}})


class TenderNegotiationAccelerationTest(TenderNegotiationQuickAccelerationTest):
    stand_still_period_days = 10
    time_sleep_in_sec = 6


class TenderContractDocumentResourceTest(BaseTenderContentWebTest):
    initial_status = 'active'
    initial_bids = None

    def create_award(self):
        # Create award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'suppliers': [test_organization], 'status': 'pending'}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {"data": {"status": "active", 'qualified': True}})

    def setUp(self):
        super(TenderContractDocumentResourceTest, self).setUp()
        self.create_award()
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = response.json['data'][0]['id']

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/contracts/some_id/documents?acc_token={}',
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/contracts/some_id/documents?acc_token={}'.format(
            self.tender_id, self.tender_token), status=404, upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            status=404,
            upload_files=[('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/contracts/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/contracts/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.get('/tenders/some_id/contracts/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/contracts/some_id/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.get('/tenders/{}/contracts/{}/documents/some_id'.format(self.tender_id, self.contract_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/contracts/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/contracts/some_id/documents/some_id?acc_token={}'.format(
            self.tender_id, self.tender_token), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.put('/tenders/{}/contracts/{}/documents/some_id?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            status=404,
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_contract_document(self):
        response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/contracts/{}/documents'.format(self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/contracts/{}/documents?all=true'.format(self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/contracts/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.contract_id, doc_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/contracts/{}/documents/{}?{}'.format(
            self.tender_id, self.contract_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/contracts/{}/documents/{}'.format(
            self.tender_id, self.contract_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "cancelled"}})
        self.assertEqual(response.json['data']["status"], "cancelled")

        response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current contract status")

        self.set_status('complete')

        response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't add document in current (complete) tender status")

    def test_put_tender_contract_document(self):
        response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, doc_id, self.tender_token),
            status=404,
            upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, doc_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/contracts/{}/documents/{}?{}'.format(
            self.tender_id, self.contract_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/contracts/{}/documents/{}'.format(
            self.tender_id, self.contract_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, doc_id, self.tender_token), 'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/contracts/{}/documents/{}?{}'.format(
            self.tender_id, self.contract_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), {"data": {"status": "cancelled"}})
        self.assertEqual(response.json['data']["status"], "cancelled")

        response = self.app.put('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, doc_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content3')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current contract status")

        self.set_status('complete')

        response = self.app.put('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, doc_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content3')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update document in current (complete) tender status")

    def test_patch_tender_contract_document(self):
        response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
            self.tender_id, self.contract_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, doc_id, self.tender_token),
            {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/tenders/{}/contracts/{}/documents/{}'.format(
            self.tender_id, self.contract_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

        # cancel contract by award cancellation
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {"data": {"status": "cancelled"}})
        self.assertEqual(response.json['data']["status"], "cancelled")

        response = self.app.patch_json('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, doc_id, self.tender_token),
            {"data": {"description": "document description"}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update document in current contract status")

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, doc_id, self.tender_token),
            {"data": {"description": "document description"}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update document in current (complete) tender status")


class TenderContractNegotiationDocumentResourceTest(TenderContractDocumentResourceTest):
    initial_data = test_tender_negotiation_data


class TenderContractNegotiationLotDocumentResourceTest(TenderContractDocumentResourceTest):
    initial_data = test_tender_negotiation_data

    def create_award(self):
        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'items': self.initial_data['items'] * 2}})

        # create lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot1 = response.json['data']
        self.lot1 = lot1

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'items': [{'relatedLot': lot1['id']}]
                                      }
                             })
        # Create award
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization], 'status': 'pending',
                                                          'qualified': True, 'value': {"amount": 469,
                                                                                       "currency": "UAH",
                                                                                       "valueAddedTaxIncluded": True},
                                                          'lotID': lot1['id']}})
        award = response.json['data']
        self.award_id = award['id']
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {"data": {"status": "active"}})


class TenderContractNegotiationQuickDocumentResourceTest(TenderContractNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderContractNegotiationQuickLotDocumentResourceTest(TenderContractNegotiationLotDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderContractDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
