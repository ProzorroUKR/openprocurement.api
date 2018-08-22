# -*- coding: utf-8 -*-
from datetime import timedelta
from copy import deepcopy

from iso8601 import parse_date
from mock import patch
from openprocurement.api.constants import CPV_ITEMS_CLASS_FROM
from openprocurement.api.utils import get_now

from openprocurement.tender.belowthreshold.tests.base import test_organization

from openprocurement.tender.cfaua.models.tender import CloseFrameworkAgreementUA
from openprocurement.tender.cfaua.utils import add_next_awards

# TenderTest


def simple_add_tender(self):
    u = CloseFrameworkAgreementUA(self.initial_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb['tenderID']
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "closeFrameworkAgreementUA"
    assert fromdb['procurementMethodType'] == "closeFrameworkAgreementUA"

    u.delete_instance(self.db)

# TenderResourceTest


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

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'closeFrameworkAgreementUA',
                                  'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType':'closeFrameworkAgreementUA',
                                                          'value': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            u'Please use a mapping for this field or Value instance instead of unicode.'], u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'closeFrameworkAgreementUA',
                                                          'procurementMethod': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    
    self.assertIn({u'description': [u"Value must be one of ['open', 'selective', 'limited']."], u'location': u'body',
                   u'name': u'procurementMethod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'tenderPeriod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStep'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'maxAwardsCount'}, response.json['errors'])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'closeFrameworkAgreementUA',
                                                          'enquiryPeriod': {'endDate': 'invalid_value'}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'endDate': [u"Could not parse invalid_value. Should be ISO8601."]}, u'location': u'body', u'name': u'enquiryPeriod'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'closeFrameworkAgreementUA',
                                                          'enquiryPeriod': {'endDate': '9999-12-31T23:59:59.999999'}}}, status=422)
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

    self.initial_data['tenderPeriod']['startDate'] = (get_now() - timedelta(minutes=30)).isoformat()
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    del self.initial_data['tenderPeriod']['startDate']
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'tenderPeriod.startDate should be in greater than current date'], u'location': u'body', u'name': u'tenderPeriod'}
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

    self.initial_data['auctionPeriod'] = {'startDate': (now + timedelta(days=35)).isoformat(), 'endDate': (now + timedelta(days=35)).isoformat()}
    self.initial_data['awardPeriod'] = {'startDate': (now + timedelta(days=34)).isoformat(), 'endDate': (now + timedelta(days=34)).isoformat()}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    del self.initial_data['auctionPeriod']
    del self.initial_data['awardPeriod']
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'period should begin after auctionPeriod'], u'location': u'body', u'name': u'awardPeriod'}
    ])

    data = self.initial_data['minimalStep']
    self.initial_data['minimalStep'] = {'amount': '1000.0'}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['minimalStep'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'value should be less than value of tender'], u'location': u'body', u'name': u'minimalStep'}
    ])

    data = self.initial_data['minimalStep']
    self.initial_data['minimalStep'] = {'amount': '100.0', 'valueAddedTaxIncluded': False}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['minimalStep'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of tender'], u'location': u'body', u'name': u'minimalStep'}
    ])

    data = self.initial_data['minimalStep']
    self.initial_data['minimalStep'] = {'amount': '100.0', 'currency': "USD"}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['minimalStep'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'currency should be identical to currency of value of tender'], u'location': u'body', u'name': u'minimalStep'}
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

    data = self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    del self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'contactPoint': {u'email': [u'telephone or email should be present']}},
         u'location': u'body', u'name': u'procuringEntity'}
    ])

    data = self.initial_data["items"][0].copy()
    classification = data['classification'].copy()
    classification["id"] = u'19212310-1'
    data['classification'] = classification
    self.initial_data["items"] = [self.initial_data["items"][0], data]
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'CPV group of items be identical'], u'location': u'body', u'name': u'items'}
    ])

    data = deepcopy(self.initial_data)
    del data["items"][0]['deliveryDate']
    response = self.app.post_json(request_path, {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'deliveryDate': [u'This field is required.']}], u'location': u'body', u'name': u'items'}
    ])

    data = deepcopy(self.initial_data)
    data['maxAwardsCount'] = self.min_bids_number - 1
    response = self.app.post_json(request_path, {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Maximal awards number can't be less then minimal bids number"], u'location': u'body', u'name': u'maxAwardsCount'}
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
    self.assertEqual(set(tender), set([
        u'procurementMethodType', u'id', u'dateModified', u'tenderID',
        u'status', u'enquiryPeriod', u'tenderPeriod', u'auctionPeriod',
        u'complaintPeriod', u'minimalStep', u'items', u'value', u'owner',
        u'procuringEntity', u'next_check', u'procurementMethod',
        u'awardCriteria', u'submissionMethod', u'title', u'title_en',  u'date',
        u'maxAwardsCount']))
    self.assertNotEqual(data['id'], tender['id'])
    self.assertNotEqual(data['doc_id'], tender['id'])
    self.assertNotEqual(data['tenderID'], tender['tenderID'])


def patch_tender(self):
    response = self.app.get('/tenders')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    dateModified = tender.pop('dateModified')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                   {'data': {'tenderPeriod': {'startDate': tender['enquiryPeriod']['endDate']}}},
                                   status=422
                                   )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [{
        "location": "body",
        "name": "tenderPeriod",
        "description": [
            "tenderPeriod should be greater than 30 days"
        ]
    }
    ])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'procurementMethodRationale': 'Open'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('invalidationDate', response.json['data']['enquiryPeriod'])
    new_tender = response.json['data']
    new_enquiryPeriod = new_tender.pop('enquiryPeriod')
    new_dateModified = new_tender.pop('dateModified')
    tender.pop('enquiryPeriod')
    tender['procurementMethodRationale'] = 'Open'
    self.assertEqual(tender, new_tender)
    self.assertNotEqual(dateModified, new_dateModified)

    revisions = self.db.get(tender['id']).get('revisions')
    self.assertTrue(any([i for i in revisions[-1][u'changes'] if i['op'] == u'remove' and i['path'] == u'/procurementMethodRationale']))

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'dateModified': new_dateModified}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_tender2 = response.json['data']
    new_enquiryPeriod2 = new_tender2.pop('enquiryPeriod')
    new_dateModified2 = new_tender2.pop('dateModified')
    self.assertEqual(new_tender, new_tender2)
    self.assertNotEqual(new_enquiryPeriod, new_enquiryPeriod2)
    self.assertNotEqual(new_dateModified, new_dateModified2)

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'procuringEntity': {'kind': 'defense'}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['procuringEntity']['kind'], 'defense')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'items': [self.initial_data['items'][0]]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'items': [{}, self.initial_data['items'][0]]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    item0 = response.json['data']['items'][0]
    item1 = response.json['data']['items'][1]
    self.assertNotEqual(item0.pop('id'), item1.pop('id'))
    self.assertEqual(item0, item1)

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'items': [{}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']['items']), 1)

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"classification": {
        "scheme": "CPV",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах"
    }}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"additionalClassifications": [
        tender['items'][0]["additionalClassifications"][0] for i in range(3)
    ]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"additionalClassifications": tender['items'][0]["additionalClassifications"]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'enquiryPeriod': {'endDate': new_dateModified2}}},status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"guarantee": {"valueAddedTaxIncluded": True}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'][0], {u'description': {u'valueAddedTaxIncluded': u'Rogue field'}, u'location': u'body', u'name': u'guarantee'})

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"guarantee": {"amount": 12}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('guarantee', response.json['data'])
    self.assertEqual(response.json['data']['guarantee']['amount'], 12)
    self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"guarantee": {"currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

    #response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.auction'}})
    #self.assertEqual(response.status, '200 OK')

    #response = self.app.get('/tenders/{}'.format(tender['id']))
    #self.assertEqual(response.status, '200 OK')
    #self.assertEqual(response.content_type, 'application/json')
    #self.assertIn('auctionUrl', response.json['data'])

    self.set_status('complete')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'status': 'active.auction'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update tender in current (complete) status")

def patch_tender_period(self):
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    owner_token = response.json['access']['token']
    self.tender_id = tender['id']
    self.go_to_enquiryPeriod_end()
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {"description": "new description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "tenderPeriod should be extended by 7 days")
    tenderPeriod_endDate = get_now() + timedelta(days=7, seconds=10)
    enquiryPeriod_endDate = tenderPeriod_endDate - (timedelta(minutes=10) if SANDBOX_MODE else timedelta(days=10))
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data':
        {
            "description": "new description",
            "tenderPeriod": {
                "endDate": tenderPeriod_endDate.isoformat()
            }
        }
    })
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['tenderPeriod']['endDate'], tenderPeriod_endDate.isoformat())
    self.assertEqual(response.json['data']['enquiryPeriod']['endDate'], enquiryPeriod_endDate.isoformat())


def tender_contract_period(self):
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'active.tendering')
    self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']

    self.app.authorization = ('Basic', ('token', ''))
    # active.tendering
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
        {'data': {'contractPeriod': {'endDate': '2018-08-09'}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    
    # patch shouldn't affect changes
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('contractPeriod', response.json['data'])

    self.set_status('active.awarded')
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('contractPeriod', response.json['data'])
    self.assertNotIn('endDate', response.json['data']['contractPeriod'])

    self.set_status('complete')
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('contractPeriod', response.json['data'])
    self.assertIn('endDate', response.json['data']['contractPeriod'])



def invalid_bid_tender_features(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    data = deepcopy(self.initial_data)
    data['features'] = [
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
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
    response = self.app.post_json('/tenders',
                                  {"data": data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']

    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'parameters': [{"code": "OCDS-123454-POSTPONEMENT", "value": 0.1}],
                                            'tenderers': [test_organization], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid_id = response.json['data']['id']
    bid_token = response.json['access']['token']

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"features": [{"code": "OCDS-123-POSTPONEMENT"}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json['data']["features"][0]["code"])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token),
                                   {'data': {'parameters': [{"code": "OCDS-123-POSTPONEMENT"}],
                                             'status': 'pending'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json['data']["parameters"][0]["code"])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"features": [{"enum": [{"value": 0.2}]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(0.2, response.json['data']["features"][0]["enum"][0]["value"])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token),
                                   {'data': {'parameters': [{"value": 0.2}],
                                             'status': 'pending'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json['data']["parameters"][0]["code"])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"features": []}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn("features", response.json['data'])

    # switch to active.qualification
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
    self.assertNotEqual(response.json['data']['date'], tender['date'])


def invalid_bid_tender_lot(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    lots = []
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                  {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lots.append(response.json['data']['id'])

    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'status': 'draft',
                                            'lotValues': [{"value": self.test_bids_data[0]['value'],
                                                           'relatedLot': i} for i in lots],
                                            'tenderers': [test_organization]}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lots[0], owner_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    # switch to active.qualification
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
    self.assertNotEqual(response.json['data']['date'], tender['date'])


# TenderProcessTest


def one_bid_tender(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    # create bid
    bidder_data = deepcopy(test_organization)
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [bidder_data], "value": self.test_bids_data[0]['value']}})
    # switch to active.pre-qualification
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # tender should switch to "unsuccessful"
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "unsuccessful")


def unsuccessful_after_prequalification_tender(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # create bid
    bidder_data = deepcopy(test_organization)
    self.app.authorization = ('Basic', ('broker', ''))
    for x in range(self.min_bids_number):
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': [bidder_data], "value": self.test_bids_data[0]['value']}})

    # switch to active.pre-qualification
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # tender should switch to "active.pre-qualification"
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification")
    # list qualifications
    response = self.app.get('/tenders/{}/qualifications'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json['data']
    self.assertEqual(len(qualifications), self.min_bids_number)
    # disqualify all bids
    self.app.authorization = ('Basic', ('broker', ''))
    for qualification in qualifications:
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(tender_id, qualification['id'], owner_token), {"data": {"status": "unsuccessful"}})
        self.assertEqual(response.status, "200 OK")
    # switch to next status
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                   {"data": {"status": "active.pre-qualification.stand-still"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status('active.pre-qualification.stand-still', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], "unsuccessful")
    for bid in response.json['data']['bids']:
        self.assertEqual(bid["status"], 'unsuccessful')
        self.assertEqual(set(bid.keys()), set([
            u'id', u'status', u'selfEligible', u'tenderers', u'selfQualified',
        ]))


def one_qualificated_bid_tender(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    tender_owner_token = response.json['access']['token']
    # create bids
    bidder_data = deepcopy(test_organization)
    self.app.authorization = ('Basic', ('broker', ''))

    for i in range(self.min_bids_number):
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': [bidder_data], "value": self.test_bids_data[i]['value']}})

    # switch to active.pre-qualification
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # tender should switch to "active.pre-qualification"
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification")
    # list qualifications
    response = self.app.get('/tenders/{}/qualifications'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json['data']
    self.assertEqual(len(qualifications), self.min_bids_number)
    # approve first qualification/bid
    self.app.authorization = None
    response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(tender_id, qualifications[0]['id']), {"data": {"status": "active", "qualified": True, "eligible": True}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(tender_id, qualifications[0]['id']), {"data": {"status": "active", "qualified": True, "eligible": True}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(tender_id, qualifications[0]['id'], "c"*32), {"data": {"status": "active", "qualified": True, "eligible": True}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.app.authorization = ('Basic', ('broker', ''))
    for i in range(self.min_bids_number-1):
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(tender_id, qualifications[i]['id'], tender_owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, "200 OK")
    # bid should be activated
    response = self.app.get('/tenders/{}/bids/{}'.format(tender_id, qualifications[0]['bidID']))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active")
    # invalidate second qualification/bid
    response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(tender_id, qualifications[self.min_bids_number-1]['id'], tender_owner_token), {"data": {"status": "unsuccessful"}})

    # bid should be cancelled
    response = self.app.get('/tenders/{}/bids/{}'.format(tender_id, qualifications[self.min_bids_number-1]['bidID']))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "unsuccessful")
    self.assertNotIn('value', response.json['data'])
    # switch to next status
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, tender_owner_token),
                                   {"data": {"status": "active.pre-qualification.stand-still"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")
    # tender should switch to "unsuccessful"
    self.set_status('active.pre-qualification.stand-still', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # ensure that tender has been switched to "unsuccessful"
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "unsuccessful")


def multiple_bidders_tender(self):
    # create tender
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    tender_owner_token = response.json['access']['token']
    # create bids
    bidder_data = deepcopy(test_organization)
    self.app.authorization = ('Basic', ('broker', ''))

    for i in range(self.min_bids_number):
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [bidder_data], "value": self.test_bids_data[0]['value']}})

    bid_id = response.json['data']['id']
    bid_token = response.json['access']['token']
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [bidder_data], "value": self.test_bids_data[0]['value']}})
    # switch to active.pre-qualification
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # tender should switch to "active.pre-qualification"
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification")
    # list qualifications
    response = self.app.get('/tenders/{}/qualifications'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json['data']
    self.assertEqual(len(qualifications), self.min_bids_number+1)
    # approve first two bids qualification/bid
    self.app.authorization = ('Basic', ('broker', ''))
    for i in range(self.min_bids_number - 1):
        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(tender_id, qualifications[i]['id'], tender_owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    # cancel qualification for second bid
    response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
        tender_id, qualifications[self.min_bids_number - 1]['id'], tender_owner_token),
        {"data": {"status": "cancelled"}})

    self.assertEqual(response.status, "200 OK")
    self.assertIn('Location', response.headers)
    new_qualification_location = response.headers['Location']
    qualification_id  = new_qualification_location[-32:]
    # approve the bid again
    response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(tender_id, qualification_id,
                                                                                       tender_owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, "200 OK")
    # try to change tender state by chronograph leaving one bid unreviewed
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification")
    # reject third bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(tender_id, qualifications[self.min_bids_number]['id'], tender_owner_token), {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, "200 OK")
    # switch to next status
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, tender_owner_token),
                                   {"data": {"status": "active.pre-qualification.stand-still"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")
    # ensure that tender has been switched to "active.pre-qualification.stand-still"
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")
    # 'active.auction' status can't be set with chronograpth tick
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")
    # time traver
    self.set_status('active.pre-qualification.stand-still', 'end')
    # change tender state
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.auction")

    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls
    response = self.app.patch_json('/tenders/{}/auction'.format(tender_id),
                                   {
                                       'data': {
                                           'auctionUrl': 'https://tender.auction.url',
                                           'bids': [
                                               {
                                                   'id': i['id'],
                                                   'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                                               }
                                               for i in auction_bids_data
                                           ]
                                       }
    })
    # view bid participationUrl
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json['data']['participationUrl'], 'https://tender.auction.url/for_bid/{}'.format(bid_id))
    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(tender_id),
                                  {'data': {'bids': auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, tender_owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as unsuccessful
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, tender_owner_token),
                                   {"data": {"status": "unsuccessful"}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, tender_owner_token))
    # get pending award
    award2_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    self.assertNotEqual(award_id, award2_id)
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award2_id, tender_owner_token),
                        {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, "200 OK")
    # get agreement id
    response = self.app.get('/tenders/{}'.format(tender_id))
    agreement_id = response.json['data']['agreements'][-1]['id']

    # XXX rewrite following part with less of magic actions
    # after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    self.set_status('active.awarded', 'end')
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(tender_id, agreement_id, tender_owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')


def lost_contract_for_active_award(self):
    # create tender
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']

    # create bids
    for i in range(self.min_bids_number):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], "value": self.test_bids_data[0]['value']}})

    # switch to active.pre-qualification
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # tender should switch to "active.pre-qualification"
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['status'], "active.pre-qualification")
    # list qualifications
    response = self.app.get('/tenders/{}/qualifications'.format(tender_id))
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json['data']
    # approve qualification
    for qualification in qualifications:
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(tender_id, qualification['id'], owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")

    # switch to active.auction
    self.set_status('active.auction')

    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(tender_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(tender_id),
                                  {'data': {'bids': auction_bids_data}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
    # lost agreement
    tender = self.db.get(tender_id)
    tender['agreements'] = None
    self.db.save(tender)
    # check tender
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']['status'], 'active.awarded')
    self.assertNotIn('agreements', response.json['data'])
    self.assertIn('next_check', response.json['data'])
    # create lost agreement
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.awarded')
    self.assertIn('agreements', response.json['data'])
    self.assertNotIn('next_check', response.json['data'])
    agreement_id = response.json['data']['agreements'][-1]['id']
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/tenders/{}/agreements/{}?acc_token={}'.format(tender_id, agreement_id, owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']['status'], 'complete')


def patch_tender_active_qualification_2_active_qualification_stand_still(self):
    self.app.authorization = ('Basic', ('broker', ''))

    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')

    awards = response.json['data']
    for award in awards:
        self.assertEqual(award['status'], 'pending')

    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, awards[0]['id'], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}})

    # try to switch not all awards qualified
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {"data": {"status": 'active.qualification.stand-still'}},
                                   status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     u"Can't switch to 'active.qualification.stand-still' while not all awards are qualified")

    for award in awards[1:]:
        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {"data": {"status": 'active.qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.qualification.stand-still')

    # check award.complaintPeriod.endDate
    tender = response.json['data']
    for award in tender['awards']:
        self.assertEqual(award['complaintPeriod']['endDate'], tender['awardPeriod']['endDate'])


def switch_tender_to_active_awarded(self):
    """ Test for switch tender from active.qualification.stand-still to active.awarded """

    status = 'active.qualification.stand-still'
    self.set_status(status)

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.json['data']['status'], status)

    # Try switch with role 'broker'
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'],
                     [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}])

    # Try switch before awardPeriod complete
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], status)
    self.assertGreater(response.json['data']['awardPeriod']['endDate'], get_now().isoformat())

    # Switch after awardPeriod complete
    # Use timeshift
    with patch('openprocurement.tender.cfaua.utils.get_now') as mocked_time:
        mocked_time.return_value = parse_date(response.json['data']['awardPeriod']['endDate'])
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active.awarded')
    self.assertIn('contractPeriod', response.json['data'])


def patch_max_awards(self):
    min_awards_number = self.min_bids_number

    response = self.app.get('/tenders')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    self.tender_id = response.json['data']['id']
    self.tender_token = response.json['access']['token']

    self.app.authorization = ('Basic', ('token', ''))

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
        {'data': {'maxAwardsCount': min_awards_number - 1}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [{
        u'description': [u"Maximal awards number can't be less then minimal bids number"],
        u'location': u'body', u'name': u'maxAwardsCount'}])
    
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
            {'data': {'maxAwardsCount': min_awards_number}})
    tender = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(tender['maxAwardsCount'], min_awards_number)

    self.set_status('active.pre-qualification')
    # should not change max awards number in active.pre-qualification
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
            {'data': {'maxAwardsCount': min_awards_number + 1}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(tender['maxAwardsCount'], min_awards_number + 1)


def _awards_to_bids_number(self, max_awards_number, bids_number, expected_awards_number):
    response = self.app.get('/tenders')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    initial_data = self.initial_data
    initial_data['maxAwardsCount'] = max_awards_number

    response = self.app.post_json('/tenders', {'data': initial_data})
    self.assertEqual(response.status, '201 Created')
    self.tender_id = response.json['data']['id']
    self.tender_token = response.json['access']['token']
    # create bids
    for _ in range(bids_number):
        response = self.app.post_json('/tenders/{}/bids?acc_token={}'.format(self.tender_id, self.tender_token),
                                  {'data': {'selfEligible': True, 'selfQualified': True,
                                            'tenderers': [test_organization], "value": self.test_bids_data[0]['value']}})
    # switch to active.pre-qualification
    self.set_status('active.tendering', 'end')
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    # list qualifications
    response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json['data']
    # approve qualification
    for qualification in qualifications:
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.set_status('active.auction')
    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': auction_bids_data}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), expected_awards_number)
    del self.db[self.tender_id]


def awards_to_bids_number(self):
    self.app.authorization = ('Basic', ('broker', ''))
    _awards_to_bids_number(self, max_awards_number=3, bids_number=3, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=3, bids_number=4, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=3, bids_number=5, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=4, bids_number=3, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=4, bids_number=4, expected_awards_number=4)
    _awards_to_bids_number(self, max_awards_number=4, bids_number=5, expected_awards_number=4)
    _awards_to_bids_number(self, max_awards_number=5, bids_number=3, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=5, bids_number=4, expected_awards_number=4)
    _awards_to_bids_number(self, max_awards_number=5, bids_number=5, expected_awards_number=5)
