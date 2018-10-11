# -*- coding: utf-8 -*-
import unittest
from uuid import uuid4
from copy import deepcopy
from datetime import timedelta
from iso8601 import parse_date

from openprocurement.api.utils import get_now
from openprocurement.api.constants import COORDINATES_REG_EXP, ROUTE_PREFIX, SANDBOX_MODE
from openprocurement.tender.cfaselectionua.constants import BOT_NAME, ENQUIRY_PERIOD
from openprocurement.tender.core.constants import (
    CANT_DELETE_PERIOD_START_DATE_FROM, CPV_ITEMS_CLASS_FROM,
)
from openprocurement.tender.cfaselectionua.models.tender import CFASelectionUATender as Tender
from openprocurement.tender.cfaselectionua.tests.base import (
    test_organization,
    test_agreement,
)

# TenderTest


def simple_add_tender(self):

    u = Tender(self.initial_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb['tenderID']
    assert u.doc_type == "Tender"

    u.delete_instance(self.db)

# TestCoordinatesRegExp


def coordinates_reg_exp(self):
    self.assertEqual('1', COORDINATES_REG_EXP.match('1').group())
    self.assertEqual('1.1234567890', COORDINATES_REG_EXP.match('1.1234567890').group())
    self.assertEqual('12', COORDINATES_REG_EXP.match('12').group())
    self.assertEqual('12.1234567890', COORDINATES_REG_EXP.match('12.1234567890').group())
    self.assertEqual('123', COORDINATES_REG_EXP.match('123').group())
    self.assertEqual('123.1234567890', COORDINATES_REG_EXP.match('123.1234567890').group())
    self.assertEqual('0', COORDINATES_REG_EXP.match('0').group())
    self.assertEqual('0.1234567890', COORDINATES_REG_EXP.match('0.1234567890').group())
    self.assertEqual('-0.1234567890', COORDINATES_REG_EXP.match('-0.1234567890').group())
    self.assertEqual('-1', COORDINATES_REG_EXP.match('-1').group())
    self.assertEqual('-1.1234567890', COORDINATES_REG_EXP.match('-1.1234567890').group())
    self.assertEqual('-12', COORDINATES_REG_EXP.match('-12').group())
    self.assertEqual('-12.1234567890', COORDINATES_REG_EXP.match('-12.1234567890').group())
    self.assertEqual('-123', COORDINATES_REG_EXP.match('-123').group())
    self.assertEqual('-123.1234567890', COORDINATES_REG_EXP.match('-123.1234567890').group())
    self.assertNotEqual('1.', COORDINATES_REG_EXP.match('1.').group())
    self.assertEqual(None, COORDINATES_REG_EXP.match('.1'))
    self.assertNotEqual('1.1.', COORDINATES_REG_EXP.match('1.1.').group())
    self.assertNotEqual('1..1', COORDINATES_REG_EXP.match('1..1').group())
    self.assertNotEqual('1.1.1', COORDINATES_REG_EXP.match('1.1.1').group())
    self.assertEqual(None, COORDINATES_REG_EXP.match('$tr!ng'))
    self.assertEqual(None, COORDINATES_REG_EXP.match(''))

# TenderResourceTest


def listing(self):
    response = self.app.get('/tenders')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    tenders = []

    data = deepcopy(self.initial_data)
    data['agreements'] = [{'id': uuid4().hex}]
    for i in range(3):
        offset = get_now().isoformat()
        response = self.app.post_json('/tenders', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(response.json['data']['id'], response.json['access']['token']),
            {'data': {'status': 'draft.pending'}}
        )
        tenders.append(response.json['data'])

    ids = ','.join([i['id'] for i in tenders])

    while True:
        response = self.app.get('/tenders')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in tenders]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders]))

    while True:
        response = self.app.get('/tenders?offset={}'.format(offset))
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/tenders?limit=2')
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

    response = self.app.get('/tenders', params=[('opt_fields', 'status')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
    self.assertIn('opt_fields=status', response.json['next_page']['uri'])

    response = self.app.get('/tenders', params=[('opt_fields', 'status,enquiryPeriod')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
    self.assertIn('opt_fields=status%2CenquiryPeriod', response.json['next_page']['uri'])

    response = self.app.get('/tenders?descending=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders], reverse=True))

    response = self.app.get('/tenders?descending=1&limit=2')
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

    test_tender_data2 = data.copy()
    test_tender_data2['mode'] = 'test'
    response = self.app.post_json('/tenders', {'data': test_tender_data2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json(
        '/tenders/{}?acc_token={}'.format(response.json['data']['id'], response.json['access']['token']),
        {'data': {'status': 'draft.pending'}}
    )

    while True:
        response = self.app.get('/tenders?mode=test')
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/tenders?mode=_all_')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)


def listing_changes(self):
    response = self.app.get('/tenders?feed=changes')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    tenders = []

    data = deepcopy(self.initial_data)
    data['agreements'] = [{'id': uuid4().hex}]
    for i in range(3):
        response = self.app.post_json('/tenders', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(response.json['data']['id'], response.json['access']['token']),
            {'data': {'status': 'draft.pending'}}
        )
        tenders.append(response.json['data'])

    ids = ','.join([i['id'] for i in tenders])

    while True:
        response = self.app.get('/tenders?feed=changes')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(','.join([i['id'] for i in response.json['data']]), ids)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in tenders]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders]))

    response = self.app.get('/tenders?feed=changes&limit=2')
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

    response = self.app.get('/tenders?feed=changes', params=[('opt_fields', 'status')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
    self.assertIn('opt_fields=status', response.json['next_page']['uri'])

    response = self.app.get('/tenders?feed=changes', params=[('opt_fields', 'status,enquiryPeriod')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
    self.assertIn('opt_fields=status%2CenquiryPeriod', response.json['next_page']['uri'])

    response = self.app.get('/tenders?feed=changes&descending=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders], reverse=True))

    response = self.app.get('/tenders?feed=changes&descending=1&limit=2')
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

    test_tender_data2 = data.copy()
    test_tender_data2['mode'] = 'test'
    response = self.app.post_json('/tenders', {'data': test_tender_data2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json(
        '/tenders/{}?acc_token={}'.format(response.json['data']['id'], response.json['access']['token']),
        {'data': {'status': 'draft.pending'}}
    )

    while True:
        response = self.app.get('/tenders?feed=changes&mode=test')
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/tenders?feed=changes&mode=_all_')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)


def listing_draft(self):
    response = self.app.get('/tenders')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    tenders = []
    data = self.initial_data.copy()
    data.update({'status': 'draft', 'agreements': [{'id': uuid4().hex}]})

    for i in range(3):
        response = self.app.post_json('/tenders', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        response = self.app.post_json('/tenders', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(response.json['data']['id'], response.json['access']['token']),
            {'data': {'status': 'draft.pending'}}
        )
        tenders.append(response.json['data'])

    ids = ','.join([i['id'] for i in tenders])

    while True:
        response = self.app.get('/tenders')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in tenders]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in tenders]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in tenders]))


def create_tender_invalid(self):
    request_path = '/tenders'
    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
            u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
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

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'invalid_value'}}, status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not implemented', u'location': u'data', u'name': u'procurementMethodType'}
    ])

    response = self.app.post_json(request_path, {'data': {
        "procurementMethodType": "closeFrameworkAgreementSelectionUA",
        'invalid_field': 'invalid_value'
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {'data': {
        "procurementMethodType": "closeFrameworkAgreementSelectionUA",
        'value': 'invalid_value'
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            u'Please use a mapping for this field or Value instance instead of unicode.'], u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json(request_path, {'data': {
        "procurementMethodType": "closeFrameworkAgreementSelectionUA",
        'procurementMethod': 'invalid_value'
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn({u'description': [u"Value must be one of ['open', 'selective', 'limited']."], u'location': u'body', u'name': u'procurementMethod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'tenderPeriod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStep'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'enquiryPeriod'}, response.json['errors'])

    response = self.app.post_json(request_path, {'data': {
        "procurementMethodType": "closeFrameworkAgreementSelectionUA",
        'enquiryPeriod': {'endDate': 'invalid_value'}
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'endDate': [u"Could not parse invalid_value. Should be ISO8601."]}, u'location': u'body', u'name': u'enquiryPeriod'}
    ])

    response = self.app.post_json(request_path, {'data': {
        "procurementMethodType": "closeFrameworkAgreementSelectionUA",
        'enquiryPeriod': {'endDate': '9999-12-31T23:59:59.999999'}
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'endDate': [u'date value out of range']}, u'location': u'body', u'name': u'enquiryPeriod'}
    ])

    data = self.initial_data['tenderPeriod']
    self.initial_data['tenderPeriod'] = {'startDate': '2014-10-31T00:00:00', 'endDate': '2014-10-01T00:00:00'}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['tenderPeriod'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'startDate': [u'period should begin before its end']}, u'location': u'body', u'name': u'tenderPeriod'}
    ])

    data = self.initial_data['tenderPeriod']
    self.initial_data['tenderPeriod'] = {'startDate': '2014-10-31T00:00:00', 'endDate': '2015-10-01T00:00:00'}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['tenderPeriod'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'period should begin after enquiryPeriod'], u'location': u'body', u'name': u'tenderPeriod'}
    ])

    now = get_now()
    self.initial_data['awardPeriod'] = {'startDate': now.isoformat(), 'endDate': now.isoformat()}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    del self.initial_data['awardPeriod']
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'period should begin after tenderPeriod'], u'location': u'body', u'name': u'awardPeriod'}
    ])

    self.initial_data['auctionPeriod'] = {'startDate': (now + timedelta(days=15)).isoformat(), 'endDate': (now + timedelta(days=15)).isoformat()}
    self.initial_data['awardPeriod'] = {'startDate': (now + timedelta(days=14)).isoformat(), 'endDate': (now + timedelta(days=14)).isoformat()}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    del self.initial_data['auctionPeriod']
    del self.initial_data['awardPeriod']
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'period should begin after auctionPeriod'], u'location': u'body', u'name': u'awardPeriod'}
    ])

    data = self.initial_data["items"][0].pop("additionalClassifications")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data["items"][0]['classification']['id']
        self.initial_data["items"][0]['classification']['id'] = '99999999-9'
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["items"][0]["additionalClassifications"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.initial_data["items"][0]['classification']['id'] = cpv_code
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'additionalClassifications': [u'This field is required.']}], u'location': u'body', u'name': u'items'}
    ])

    data = self.initial_data["items"][0]["additionalClassifications"][0]["scheme"]
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = 'Не ДКПП'
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data["items"][0]['classification']['id']
        self.initial_data["items"][0]['classification']['id'] = '99999999-9'
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.initial_data["items"][0]['classification']['id'] = cpv_code
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'additionalClassifications': [u"One of additional classifications should be one of [ДК003, ДК015, ДК018, specialNorms]."]}], u'location': u'body', u'name': u'items'}
        ])
    else:
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'additionalClassifications': [u"One of additional classifications should be one of [ДКПП, NONE, ДК003, ДК015, ДК018]."]}], u'location': u'body', u'name': u'items'}
        ])

    data = test_organization["contactPoint"]["telephone"]
    del test_organization["contactPoint"]["telephone"]
    # response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    test_organization["contactPoint"]["telephone"] = data
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'description': {u'contactPoint': {u'email': [u'telephone or email should be present']}}, u'location': u'body', u'name': u'procuringEntity'}
    # ])

    data = self.initial_data["items"][0].copy()
    data['id'] = uuid4().hex
    classification = data['classification'].copy()
    classification["id"] = u'19212310-1'
    data['classification'] = classification
    self.initial_data["items"] = [self.initial_data["items"][0], data]
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(response.json['errors'], [
            {u'description': [u'CPV class of items should be identical'], u'location': u'body', u'name': u'items'}
        ])
    else:
        self.assertEqual(response.json['errors'], [
            {u'description': [u'CPV group of items be identical'], u'location': u'body', u'name': u'items'}
        ])

    cpv = self.initial_data["items"][0]['classification']["id"]
    self.initial_data["items"][0]['classification']["id"] = u'160173000-1'
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["items"][0]['classification']["id"] = cpv
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn(u'classification', response.json['errors'][0][u'description'][0])
    self.assertIn(u'id', response.json['errors'][0][u'description'][0][u'classification'])
    self.assertIn("Value must be one of [u", response.json['errors'][0][u'description'][0][u'classification'][u'id'][0])

    cpv = self.initial_data["items"][0]['classification']["id"]
    self.initial_data["items"][0]['classification']["id"] = u'00000000-0'
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["items"][0]['classification']["id"] = cpv
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn(u'classification', response.json['errors'][0][u'description'][0])
    self.assertIn(u'id', response.json['errors'][0][u'description'][0][u'classification'])
    self.assertIn("Value must be one of [u", response.json['errors'][0][u'description'][0][u'classification'][u'id'][0])
    data = deepcopy(self.initial_data)
    data["items"] = [data["items"][0]]
    data["items"][0]['classification']['id'] = u'33600000-6'
    del data["items"][0]['additionalClassifications']

    # Because validations removed in https://github.com/ProzorroUKR/openprocurement.api/pull/2

    # data["items"][0]['additionalClassifications'] = [{
    #     "scheme": u"INN",
    #     "id": u"17.21.1",
    #     "description": u"папір і картон гофровані, паперова й картонна тара"
    # }]

    # response = self.app.post_json('/tenders', {"data": data}, status=422)
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'],
    #                  [{u'description': [
    #                      {u'additionalClassifications': [{u'id': [u"Value must be one of {}.".format(INN_CODES)]}]}],
    #                      u'name': u'items', u'location': u'body'}]
    #                  )

    # assign correct id code
    # data['items'][0]['additionalClassifications'][0]['id'] = u'sodium oxybate'
    # additional_classification = {
    #     "scheme": u"ATC",
    #     "id": u"17.21.1",
    #     "description": u"папір і картон гофровані, паперова й картонна тара"
    # }
    # data['items'][0]['additionalClassifications'].append(additional_classification)

    # response = self.app.post_json('/tenders', {"data": data}, status=422)
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'],
    #                  [{u'description': [
    #                      {u'additionalClassifications': [{u'id': [u"Value must be one of {}.".format(ATC_CODES)]}]}],
    #                      u'name': u'items', u'location': u'body'}]
    #                  )

    procuringEntity = self.initial_data["procuringEntity"]
    data = self.initial_data["procuringEntity"].copy()
    del data['kind']
    self.initial_data["procuringEntity"] = data
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=403)
    self.initial_data["procuringEntity"] = procuringEntity
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"'' procuringEntity cannot publish this type of procedure. Only general, special, defense, other are allowed.", u'location': u'procuringEntity', u'name': u'kind'}
    ])


def create_tender_generated(self):
    data = self.initial_data.copy()

    #del data['awardPeriod']
    data.update({'id': 'hash', 'doc_id': 'hash2', 'tenderID': 'hash3'})
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    if 'procurementMethodDetails' in tender:
        tender.pop('procurementMethodDetails')
    self.assertEqual(
        set(tender),
        {u'procurementMethodType', u'id', u'date', u'dateModified', u'tenderID', u'status',
         u'minimalStep', u'procuringEntity', u'items', u'procurementMethod',
         u'awardCriteria', u'submissionMethod', u'title', u'owner', u'agreements', u'lots'})
    self.assertNotEqual(data['id'], tender['id'])
    self.assertNotEqual(data['doc_id'], tender['id'])
    self.assertNotEqual(data['tenderID'], tender['tenderID'])


def create_tender_draft(self):
    data = self.initial_data.copy()
    data.update({'status': 'draft'})
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(tender['status'], 'draft')

    response = self.app.get('/tenders/{}'.format(tender['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    self.assertEqual(tender['status'], self.primary_tender_status)


def create_tender_from_terminated_agreement(self):
    agreement = deepcopy(self.initial_agreement)
    agreement['status'] = 'terminated'
    agreement['id'] = self.agreement_id

    tender = deepcopy(self.initial_data)
    tender['agreements'] = [{'id': agreement['id']}]
    response = self.app.post_json('/tenders', {'data': tender})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    token = response.json['access']['token']
    tender_id = response.json['data']['id']

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, token),
                                   {'data': {'status': 'draft.pending'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'draft.pending')

    self.app.authorization = ('Basic', (BOT_NAME, ''))

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, token),
                                   {'data': {'agreements': [agreement]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    self.assertEqual(tender['agreements'][0]['status'], 'terminated')
    self.assertEqual(tender['status'], 'draft.unsuccessful')


def create_tender(self):
    response = self.app.get('/tenders')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.initial_data['agreements'] = [{'id': self.agreement_id}]
    response = self.app.post_json('/tenders', {"data": self.initial_data})
    self.assertEqual((response.status, response.content_type), ('201 Created', 'application/json'))
    self.assertEqual(response.json['data']['agreements'][0]['id'], self.agreement_id)
    tender = response.json['data']

    response = self.app.get('/tenders/{}'.format(tender['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(tender))

    response = self.app.post_json('/tenders?opt_jsonp=callback', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"', response.body)

    response = self.app.post_json('/tenders?opt_pretty=1', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)

    response = self.app.post_json('/tenders', {"data": self.initial_data, "options": {"pretty": True}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)

    data = deepcopy(self.initial_data)
    del data["items"][0]['deliveryAddress']['postalCode']
    del data["items"][0]['deliveryAddress']['locality']
    del data["items"][0]['deliveryAddress']['streetAddress']
    del data["items"][0]['deliveryAddress']['region']
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('postalCode', response.json['data']['items'][0]['deliveryAddress'])
    self.assertNotIn('locality', response.json['data']['items'][0]['deliveryAddress'])
    self.assertNotIn('streetAddress', response.json['data']['items'][0]['deliveryAddress'])
    self.assertNotIn('region', response.json['data']['items'][0]['deliveryAddress'])

    data = deepcopy(self.initial_data)
    data["items"] = [data["items"][0]]
    data["items"][0]['classification']['id'] = u'33600000-6'

    additional_classification_0 = {
    "scheme": u"INN",
    "id": u"sodium oxybate",
    "description": u"папір і картон гофровані, паперова й картонна тара"
    }
    data["items"][0]['additionalClassifications'] = [additional_classification_0]

    response = self.app.post_json('/tenders', {"data": data})
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['items'][0]['classification']['id'], '33600000-6')
    self.assertEqual(response.json['data']['items'][0]['classification']['scheme'], u'ДК021')
    self.assertEqual(response.json['data']['items'][0]['additionalClassifications'][0], additional_classification_0)

    additional_classification_1 = {
    "scheme": u"ATC",
    "id": u"A02AF",
    "description": u"папір і картон гофровані, паперова й картонна тара"
    }
    data['items'][0]['additionalClassifications'].append(additional_classification_1)
    response = self.app.post_json('/tenders', {"data": data})
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['items'][0]['classification']['id'], '33600000-6')
    self.assertEqual(response.json['data']['items'][0]['classification']['scheme'], u'ДК021')
    self.assertEqual(response.json['data']['items'][0]['additionalClassifications'],
    [additional_classification_0, additional_classification_1])

    tender_data = deepcopy(self.initial_data)
    tender_data['guarantee'] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json('/tenders', {'data': tender_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    data = response.json['data']
    self.assertIn('guarantee', data)
    self.assertEqual(data['guarantee']['amount'], 100500)
    self.assertEqual(data['guarantee']['currency'], "USD")


def tender_funders(self):
    tender_data = deepcopy(self.initial_data)
    tender_data['funders'] = [deepcopy(test_organization)]
    tender_data['funders'][0]['identifier']['id'] = '44000'
    tender_data['funders'][0]['identifier']['scheme'] = 'XM-DAC'
    response = self.app.post_json('/tenders', {'data': tender_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('funders', response.json['data'])
    self.assertEqual(response.json['data']['funders'][0]['identifier']['id'], '44000')
    self.assertEqual(response.json['data']['funders'][0]['identifier']['scheme'], 'XM-DAC')
    tender = response.json['data']
    self.tender_id = tender['id']
    token = response.json['access']['token']

    tender_data['funders'].append(deepcopy(test_organization))
    tender_data['funders'][1]['identifier']['id'] = '44000'
    tender_data['funders'][1]['identifier']['scheme'] = 'XM-DAC'
    response = self.app.post_json('/tenders', {'data': tender_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Funders' identifier should be unique"], u'location': u'body', u'name': u'funders'}
    ])

    tender_data['funders'][0]['identifier']['id'] = 'some id'
    response = self.app.post_json('/tenders', {'data': tender_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Funder identifier should be one of the values allowed"], u'location': u'body', u'name': u'funders'}
    ])
    # tender_data['funders'][0]['identifier']['id'] = '11111111'
    # response = self.app.post_json('/tenders', {'data': tender_data})
    # self.assertEqual(response.status, '201 Created')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertIn('funders', response.json['data'])
    # self.assertEqual(len(response.json['data']['funders']), 2)
    # tender = response.json['data']
    # token = response.json['access']['token']

    # response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), {'data': {'funders': [{
    #     "identifier": {'id': '22222222'}}, {}]}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertIn('funders', response.json['data'])
    # self.assertEqual(len(response.json['data']['funders']), 2)
    # self.assertEqual(response.json['data']['funders'][0]['identifier']['id'], '22222222')


def tender_fields(self):
    response = self.app.post_json('/tenders', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    self.assertEqual(set(tender) - set(self.initial_data), set(
        [u'id', u'dateModified', u'tenderID', u'date', u'status', u'procurementMethod', u'awardCriteria',
         u'submissionMethod', u'owner']))
    self.assertIn(tender['id'], response.headers['Location'])


def get_tender(self):
    response = self.app.get('/tenders')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']

    response = self.app.get('/tenders/{}'.format(tender['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], tender)

    response = self.app.get('/tenders/{}?opt_jsonp=callback'.format(tender['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get('/tenders/{}?opt_pretty=1'.format(tender['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "data": {\n        "', response.body)


def tender_features_invalid(self):
    data = self.initial_data.copy()
    item = data['items'][0].copy()
    item['id'] = "1"
    data['items'] = [item, item.copy()]
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Item id should be uniq for all items'], u'location': u'body', u'name': u'items'}
    ])
    data['items'][0]["id"] = "0"
    data['features'] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "lot",
            "title": u"Потужність всмоктування",
            "enum": [
                {
                    "value": 0.1,
                    "title": u"До 1000 Вт"
                },
                {
                    "value": 0.15,
                    "title": u"Більше 1000 Вт"
                }
            ]
        }
    ]
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedItem': [u'This field is required.']}], u'location': u'body', u'name': u'features'}
    ])
    data['features'][0]["relatedItem"] = "2"
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedItem': [u'relatedItem should be one of lots']}], u'location': u'body', u'name': u'features'}
    ])
    data['features'][0]["featureOf"] = "item"
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedItem': [u'relatedItem should be one of items']}], u'location': u'body', u'name': u'features'}
    ])
    data['features'][0]["relatedItem"] = "1"
    data['features'][0]["enum"][0]["value"] = 0.5
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'enum': [{u'value': [u'Float value should be less than 0.3.']}]}], u'location': u'body', u'name': u'features'}
    ])
    data['features'][0]["enum"][0]["value"] = 0.15
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'enum': [u'Feature value should be uniq for feature']}], u'location': u'body', u'name': u'features'}
    ])
    data['features'][0]["enum"][0]["value"] = 0.1
    data['features'].append(data['features'][0].copy())
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Feature code should be uniq for all features'], u'location': u'body', u'name': u'features'}
    ])
    data['features'][1]["code"] = u"OCDS-123454-YEARS"
    data['features'][1]["enum"][0]["value"] = 0.2
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Sum of max value of all features for lot should be less then or equal to 30%'], u'location': u'body', u'name': u'features'}
    ])


def tender_features(self):
    data = self.initial_data.copy()
    data['procuringEntity']['contactPoint']['faxNumber'] = u"0440000000"
    item = data['items'][0].copy()
    data['items'] = [item]
    data['features'] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": item['id'],
            "title": u"Потужність всмоктування",
            "title_en": u"Air Intake",
            "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [
                {
                    "value": 0.05,
                    "title": u"До 1000 Вт"
                },
                {
                    "value": 0.1,
                    "title": u"Більше 1000 Вт"
                }
            ]
        },
        {
            "code": "OCDS-123454-YEARS",
            "featureOf": "tenderer",
            "title": u"Років на ринку",
            "title_en": u"Years trading",
            "description": u"Кількість років, які організація учасник працює на ринку",
            "enum": [
                {
                    "value": 0.05,
                    "title": u"До 3 років"
                },
                {
                    "value": 0.1,
                    "title": u"Більше 3 років"
                }
            ]
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "title_en": u"Postponement of payment",
            "description": u"Термін відстрочки платежу",
            "enum": [
                {
                    "value": 0.05,
                    "title": u"До 90 днів"
                },
                {
                    "value": 0.1,
                    "title": u"Більше 90 днів"
                }
            ]
        }
    ]
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    self.tender_id = tender['id']
    token = response.json['access']['token']
    self.assertEqual(tender['features'], data['features'])

    # switch to active.enquiries
    self.set_status('active.enquiries')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), {'data': {'features': [{
        "featureOf": "tenderer",
        "relatedItem": None
    }, {}, {}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('features', response.json['data'])
    self.assertNotIn('relatedItem', response.json['data']['features'][0])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), {'data': {'procuringEntity': {'contactPoint': {'faxNumber': None}}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('features', response.json['data'])
    self.assertNotIn('faxNumber', response.json['data']['procuringEntity']['contactPoint'])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), {'data': {'features': []}})
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('features', response.json['data'])


@unittest.skip("this test requires fixed version of jsonpatch library")
def patch_tender_jsonpatch(self):
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    token = response.json['access']['token']
    tender.pop('dateModified')

    import random
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), {'data': {'items': [{"additionalClassifications": [
        {
            "scheme": "ДКПП",
            "id": "{}".format(i),
            "description": "description #{}".format(i)
        }
        for i in random.sample(range(30), 25)
    ]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), {'data': {'items': [{"additionalClassifications": [
        {
            "scheme": "ДКПП",
            "id": "{}".format(i),
            "description": "description #{}".format(i)
        }
        for i in random.sample(range(30), 20)
    ]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')


def patch_tender(self):
    data = self.initial_data.copy()
    data['items'].append(deepcopy(data['items'][0]))
    data['items'][-1]['id'] = uuid4().hex
    data['items'][-1]['description'] = 'test_description'
    data['procuringEntity']['contactPoint']['faxNumber'] = u"0440000000"
    response = self.app.get('/tenders')
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual((response.status, response.content_type), ('201 Created', 'application/json'))
    tender = response.json['data']
    self.tender_id = tender['id']
    owner_token = response.json['access']['token']

    # switch to active.enquiries
    self.set_status('active.enquiries')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']

    endDate = (parse_date(tender['tenderPeriod']['startDate']) + timedelta(days=2)).isoformat()
    response = self.app.patch_json('/tenders/{}?acc_token={}'
            .format(self.tender_id, owner_token),
            {'data': {'tenderPeriod': {'endDate': endDate}}},
            status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {
            "location": "body",
            "name": "data",
            "description": "tenderPeriod should last at least 3 days"
        }
    ])

    endDate = (parse_date(tender['tenderPeriod']['startDate']) + timedelta(days=4)).isoformat()
    response = self.app.patch_json('/tenders/{}?acc_token={}'
            .format(self.tender_id, owner_token),
            {'data': {'tenderPeriod': {'endDate': endDate}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(endDate, tender['tenderPeriod']['endDate'])

    items = deepcopy(tender['items'])
    items[0]['quantity'] += 1
    items[-1]['quantity'] += 2
    response = self.app.patch_json('/tenders/{}?acc_token={}'
            .format(self.tender_id, owner_token),
            {'data': {'items': items}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['items'][0]['quantity'], tender['items'][0]['quantity'] + 1)
    self.assertEqual(response.json['data']['items'][1]['quantity'], tender['items'][1]['quantity'] + 2)
    
    items[0], items[-1] = items[-1], items[0]
    response = self.app.patch_json('/tenders/{}?acc_token={}'
            .format(self.tender_id, owner_token),
            {'data': {'items': items}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    # items not switched
    self.assertNotEqual(response.json['data']['items'], items)
    items[0], items[-1] = items[-1], items[0]
    self.assertEqual(response.json['data']['items'], items)

    # user cannot patch tender in active.enquiries
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                   {'data': {'title': 'test_title'}}, status=403)
    self.assertEqual((response.status, response.content_type), ('403 Forbidden', 'application/json'))

    # owner can't also
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                   {'data': {'title': 'test_title'}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['title'], tender['title'])


    response = self.app.get('/tenders/{}'.format(tender['id']))
    tender = response.json['data']
    dateModified = tender.pop('dateModified')
    # user cannot patch tender in active.enquiries
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                   {'data': {'status': 'active.tendering'}}, status=403)
    self.assertEqual((response.status, response.content_type), ('403 Forbidden', 'application/json'))

    response = self.app.get('/tenders/{}'.format(tender['id']))
    tender = response.json['data']
    dateModified = tender.pop('dateModified')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'status': 'cancelled'}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertNotEqual(response.json['data']['status'], 'cancelled')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'procuringEntity': {'kind': 'defense'}}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertNotEqual(response.json['data']['procuringEntity']['kind'], 'defense')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'procuringEntity': {'contactPoint': {'faxNumber': None}}}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertIn('faxNumber', response.json['data']['procuringEntity']['contactPoint'])
    tender = response.json['data']

    startDate = (parse_date(tender['tenderPeriod']['startDate']) + timedelta(days=1)).isoformat()
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'tenderPeriod': {'startDate': startDate}}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertNotEqual(startDate, tender['tenderPeriod']['startDate'])

    endDate = (parse_date(tender['tenderPeriod']['endDate']) + timedelta(days=1)).isoformat()
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'tenderPeriod': {'endDate': endDate}}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertEqual(endDate, tender['tenderPeriod']['endDate'])

    self.set_status('active.tendering')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']

    startDate = (parse_date(tender['tenderPeriod']['startDate']) + timedelta(days=1)).isoformat()
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'tenderPeriod': {'startDate': startDate}}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertNotEqual(startDate, tender['tenderPeriod']['startDate'])

    # can't change endDate either
    endDate = (parse_date(tender['tenderPeriod']['endDate']) + timedelta(days=1)).isoformat()
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'tenderPeriod': {'endDate': endDate}}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json['data']
    self.assertNotEqual(endDate, tender['tenderPeriod']['endDate'])

    tender_data = self.db.get(tender['id'])
    tender_data['status'] = 'complete'
    self.db.save(tender_data)

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'status': 'active.auction'}}, status=403)
    self.assertEqual((response.status, response.content_type), ('403 Forbidden', 'application/json'))
    self.assertEqual(response.json['errors'][0]["description"], "Can't update tender in current (complete) status")


def patch_tender_bot(self):

    def create_tender_and_prepare_for_bot_patch():
        self.app.authorization = ('Basic', ('broker', ''))
        data = deepcopy(self.initial_data)
        data['status'] = 'draft'
        data['agreements'] = [{'id': self.agreement_id}]

        response = self.app.post_json('/tenders', {'data': data})
        self.assertEqual((response.status, response.content_type), ('201 Created', 'application/json'))
        global tender
        tender = response.json['data']
        global owner_token
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'status': 'draft.pending'}})
        self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
        self.assertEqual(response.json['data']['status'], 'draft.pending')

        self.app.authorization = ('Basic', (BOT_NAME, ''))


    # only bot can change tender in draft.pending
    create_tender_and_prepare_for_bot_patch()
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                   {'data': {'procuringEntity': {'kind': 'defense'}}}, status=403)
    self.assertEqual((response.status, response.content_type), ('403 Forbidden', 'application/json'))
    self.assertEqual(response.json['errors'][0]['description'],
                     "Can't update tender in current (draft.pending) tender status")

    # tender items are not subset of agreement items
    self.app.authorization = ('Basic', (BOT_NAME, ''))
    response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.enquiries'}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'draft.unsuccessful')

    # patch tender items with correct items by bot
    create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement['period']['endDate'] = (get_now() + timedelta(days=7, minutes=1)).isoformat()

    response = self.app.patch_json('/tenders/{}/agreements/{}'.format(
        self.tender_id, self.agreement_id), {"data": agreement})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['agreementID'], self.initial_agreement['agreementID'])

    response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.enquiries'}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'active.enquiries')
    enquiry_period = ENQUIRY_PERIOD
    if SANDBOX_MODE:
         enquiry_period = ENQUIRY_PERIOD / 1440
    self.assertEqual(
        parse_date(response.json['data']['enquiryPeriod']['startDate']) + enquiry_period,
        parse_date(response.json['data']['enquiryPeriod']['endDate'])
    )
    # patch tender by bot in wrong status
    response = self.app.patch_json('/tenders/{}'.format(tender['id']),
                                   {'data': {'status': 'draft'}}, status=403)
    self.assertEqual((response.status, response.content_type), ('403 Forbidden', 'application/json'))
    self.assertEqual(response.json['errors'][0]['description'],
                     "Can't update tender in current (active.enquiries) tender status")


    # patch tender with less than 7 days to end
    create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement['period']['endDate'] = (get_now() + timedelta(days=6)).isoformat()

    response = self.app.patch_json('/tenders/{}/agreements/{}'.format(
        self.tender_id, self.agreement_id), {"data": agreement})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['agreementID'], self.initial_agreement['agreementID'])

    response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.enquiries'}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'draft.unsuccessful')

    # patch tender with less than 3 active contracts
    create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement['period']['endDate'] = (get_now() + timedelta(days=7, minutes=1)).isoformat()
    agreement['contracts'] = agreement['contracts'][:2]  # only first and second contract

    response = self.app.patch_json('/tenders/{}/agreements/{}'.format(
        self.tender_id, self.agreement_id), {"data": agreement})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['agreementID'], self.initial_agreement['agreementID'])

    response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.enquiries'}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'draft.unsuccessful')

    # patch tender with wrong minimalStep
    create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement['contracts'][0]['unitPrices'][0]['value']['currency'] = u'USD'  # value.currancy on minimalStep is UAH

    response = self.app.patch_json('/tenders/{}/agreements/{}'.format(
        self.tender_id, self.agreement_id), {"data": agreement})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['agreementID'], self.initial_agreement['agreementID'])

    response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.enquiries'}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'draft.unsuccessful')


@unittest.skipIf(get_now() < CANT_DELETE_PERIOD_START_DATE_FROM, "Can`t delete period start date only from {}".format(CANT_DELETE_PERIOD_START_DATE_FROM))
def required_field_deletion(self):
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    token = response.json['access']['token']

    # TODO: Test all the required fields
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], token), {'data': {'enquiryPeriod': {'startDate': None}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'startDate': [u'This field cannot be deleted']}, u'location': u'body', u'name': u'enquiryPeriod'}
    ])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], token), {'data': {'tenderPeriod': {'startDate': None}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'startDate': [u'This field cannot be deleted']}, u'location': u'body', u'name': u'tenderPeriod'}
    ])


def dateModified_tender(self):
    response = self.app.get('/tenders')
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual((response.status, response.content_type), ('201 Created', 'application/json'))
    tender = response.json['data']
    self.tender_id = tender['id']
    token = response.json['access']['token']
    dateModified = tender['dateModified']

    response = self.app.get('/tenders/{}'.format(tender['id']))
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['dateModified'], dateModified)

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], token), {'data': {'procurementMethodRationale': 'Open'}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['dateModified'], dateModified)


def tender_not_found(self):
    response = self.app.get('/tenders')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.get('/tenders/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
    ])

    response = self.app.patch_json(
        '/tenders/some_id', {'data': {}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
    ])

    # put custom document object into database to check tender construction on non-Tender data
    data = {'contract': 'test', '_id': uuid4().hex}
    self.db.save(data)

    response = self.app.get('/tenders/{}'.format(data['_id']), status=404)
    self.assertEqual(response.status, '404 Not Found')


def guarantee(self):
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertNotIn('guarantee', response.json['data'])
    tender = response.json['data']
    self.tender_id = tender['id']
    token = response.json['access']['token']

    # switch to active.enquiries
    self.set_status('active.enquiries')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token),
                                   {'data': {'guarantee': {"amount": 55}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('guarantee', response.json['data'])
    self.assertEqual(response.json['data']['guarantee']['amount'], 55)
    self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token),
                                   {"data": {"guarantee": {"currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token),
                                   {'data': {'guarantee': {"amount": 100500, "currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('guarantee', response.json['data'])
    self.assertEqual(response.json['data']['guarantee']['amount'], 100500)
    self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), {'data': {'guarantee': None}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('guarantee', response.json['data'])
    self.assertEqual(response.json['data']['guarantee']['amount'], 100500)
    self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

    data = deepcopy(self.initial_data)
    data['guarantee'] = {"amount": 100, "currency": "USD"}
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertIn('guarantee', response.json['data'])
    self.assertEqual(response.json['data']['guarantee']['amount'], 100)
    self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token),
                                   {"data": {"guarantee": {"valueAddedTaxIncluded": True}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'][0],
                     {u'description': {u'valueAddedTaxIncluded': u'Rogue field'}, u'location': u'body',
                      u'name': u'guarantee'})


def tender_Administrator_change(self):
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']

    #response = self.app.post_json('/tenders/{}/questions'.format(tender['id']), {'data': {'title': 'question title', 'description': 'question description', 'author': test_organization}})
    #self.assertEqual(response.status, '201 Created')
    #self.assertEqual(response.content_type, 'application/json')
    #question = response.json['data']

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'mode': u'test', 'procuringEntity': {"identifier": {"id": "00000000"}}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['mode'], u'test')
    self.assertEqual(response.json['data']["procuringEntity"]["identifier"]["id"], "00000000")

    #response = self.app.patch_json('/tenders/{}/questions/{}'.format(tender['id'], question['id']), {"data": {"answer": "answer"}}, status=403)
    #self.assertEqual(response.status, '403 Forbidden')
    #self.assertEqual(response.content_type, 'application/json')
    #self.assertEqual(response.json['errors'], [
        #{"location": "url", "name": "role", "description": "Forbidden"}
    #])
    self.app.authorization = authorization

    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    token = response.json['access']['token']

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender['id'], token),
                                  {'data': {'reason': 'cancellation reason', 'status': 'active'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'mode': u'test'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['mode'], u'test')


def patch_not_author(self):
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                   {'data': {'status': 'draft.pending'}})

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('bot', 'bot'))

    response = self.app.post('/tenders/{}/documents'.format(tender['id']),
                             upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    self.app.authorization = authorization
    response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(tender['id'], doc_id, owner_token),
                                   {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

# TenderProcessTest


def invalid_tender_conditions(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    self.set_status('active.tendering')

    response = self.app.post_json('/tenders/{}/complaints'.format(tender_id),
                                  {'data': {'title': 'invalid conditions', 'description': 'description',
                                            'author': test_organization, 'status': 'claim'}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'text/plain')

    # cancellation
    self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token), {'data': {
        'reason': 'invalid conditions',
        'status': 'active'
    }})
    # check status
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], 'cancelled')


def one_valid_bid_tender(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders', {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    response = self.set_status(
        'active.tendering',
        {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}}]})
    self.assertIn("auctionPeriod", response.json['data']['lots'][0])
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json(
        '/tenders/{}/bids'.format(tender_id),
        {'data': {'tenderers': [test_organization],
                  'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.initial_data['lots'][0]['id']}]}}
    )
    # switch to active.qualification
    self.set_status('active.tendering', start_end='end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    award_date = [i['date'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active"}})
    self.assertNotEqual(response.json['data']['date'], award_date)

    # get contract id
    response = self.app.get('/tenders/{}'.format(tender_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    self.set_status('active.awarded', start_end='end')
    # time travel
    tender = self.db.get(tender_id)
    self.db.save(tender)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token), {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')


def one_invalid_bid_tender(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    self.set_status('active.tendering')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json(
        '/tenders/{}/bids'.format(tender_id),
        {'data': {'tenderers': [test_organization],
                  'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.initial_data['lots'][0]['id']}]}}
    )
    # switch to active.qualification
    self.set_status('active.tendering', start_end='end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as unsuccessful
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
        self.tender_id, award_id, owner_token), {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual((response.status, response.content_type), ('403 Forbidden', 'application/json'))
    self.assertEqual(
        response.json['errors'][0]['description'],
        "Can't update award status to unsuccessful, if tender status is active.qualification"
        " and there is no cancelled award with the same bid_id")

    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
        self.tender_id, award_id, owner_token), {"data": {"status": "active"}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'active')

    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
        self.tender_id, award_id, owner_token), {"data": {"status": "cancelled"}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    self.assertEqual(response.json['data']['status'], 'cancelled')

    response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
    new_award_id = response.json['data']['awards'][-1]['id']
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
        self.tender_id, new_award_id, owner_token), {"data": {"status": "unsuccessful"}})
    self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))

    # time travel
    tender = self.db.get(tender_id)
    self.db.save(tender)
    # set tender status after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']['status'], 'active.awarded')


def first_bid_tender(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    self.set_status('active.tendering')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json(
        '/tenders/{}/bids'.format(tender_id),
        {'data': {'tenderers': [test_organization],
                  'lotValues': [{"value": {"amount": 500}, "relatedLot": self.initial_data['lots'][0]['id']}]}}
    )
    bid_id = response.json['data']['id']
    bid_token = response.json['access']['token']
    # create second bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json(
        '/tenders/{}/bids'.format(tender_id),
        {'data': {'tenderers': [test_organization],
                  'lotValues': [{"value": {"amount": 500}, "relatedLot": self.initial_data['lots'][0]['id']}]}}
    )
    # switch to active.auction
    self.set_status('active.auction')

    lot_id = self.initial_data['lots'][0]['id']
    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls
    response = self.app.patch_json(
        '/tenders/{}/auction/{}'.format(tender_id, lot_id),
        {
            'data': {
                "lots": [{
                    'auctionUrl': 'https://tender.auction.url'
                }],
                'bids': [
                    {
                        'id': i['id'],
                        'lotValues': [{
                            'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id']),
                            'relatedLot': lot_id
                        }]
                    }
                    for i in auction_bids_data
                ]
            }
        }
    )
    # view bid participationUrl
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json['data']["lotValues"][0]['participationUrl'],
                     'https://tender.auction.url/for_bid/{}'.format(bid_id))

    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id),
                                  {'data': {'bids': auction_bids_data}})

    ## get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active"}})
    # get contract id
    response = self.app.get('/tenders/{}'.format(tender_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # create tender contract document for test
    response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(tender_id, contract_id, owner_token), upload_files=[('file', 'name.doc', 'content')], status=201)
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    # after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    self.set_status('active.awarded', start_end='end')

    tender = self.db.get(tender_id)
    self.db.save(tender)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token), {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(tender_id, contract_id, owner_token), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) tender status")

    response = self.app.patch_json('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(tender_id, contract_id, doc_id, owner_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")

    response = self.app.put('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(tender_id, contract_id, doc_id, owner_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


def lost_contract_for_active_award(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # create tender
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    self.set_status('active.tendering')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json(
        '/tenders/{}/bids'.format(tender_id),
        {'data': {'tenderers': [test_organization],
                  'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.initial_data['lots'][0]['id']}]}}
    )
    # switch to active.qualification
    self.set_status('active.tendering', start_end='end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                                   {"data": {"status": "active"}})
    # lost contract
    tender = self.db.get(tender_id)
    tender['contracts'] = None
    self.db.save(tender)
    # check tender
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']['status'], 'active.awarded')
    self.assertNotIn('contracts', response.json['data'])
    self.assertIn('next_check', response.json['data'])
    # create lost contract
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.awarded')
    self.assertIn('contracts', response.json['data'])
    self.assertNotIn('next_check', response.json['data'])
    contract_id = response.json['data']['contracts'][-1]['id']
    # time travel
    tender = self.db.get(tender_id)
    self.db.save(tender)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token), {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')


def patch_tender_to_draft_pending(self):
    data = self.initial_data.copy()
    data.pop('agreements')
    data.update({'status': 'active.tendering'})
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(tender['status'], 'draft')
    self.assertIn('items', tender)
    self.assertNotIn('agreements', tender)

    patch_data = {'data': {'status': 'draft.pending'}}
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), patch_data, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'],
        [{u'description': u"Can't switch tender to (draft.pending) status without agreements or items.",
          u'location': u'body',
          u'name': u'data'}])

    agreement_id = uuid4().hex
    patch_data['data']['agreements'] = [{'id': agreement_id}, {}]

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), patch_data, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(
        response.json['errors'],
        [{"location": "body", "name": "agreements", "description": [{"id": ["This field is required."]}]}]
    )

    patch_data['data']['agreements'].pop(1)
    patch_data['data']['status'] = 'active.tendering'
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), patch_data, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u"Can't switch tender from (draft) to (active.tendering) status.",
                       u'location': u'body',
                       u'name': u'data'}])

    patch_data['data']['status'] = 'draft.pending'
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), patch_data)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'draft.pending')
    self.assertEqual(response.json['data']['agreements'], [{'id': agreement_id}])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token),
                                   {'data': {'status': 'active.tendering'}},
                                   status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'],
        [{
            "location": "body",
            "name": "data",
            "description": "Can't update tender in current (draft.pending) tender status"
        }]
    )

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token),
                                   {'data': {'status': 'draft'}},
                                   status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'],
        [{
            "location": "body",
            "name": "data",
            "description": "Can't update tender in current (draft.pending) tender status"
        }]
    )
