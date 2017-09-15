# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import CPV_ITEMS_CLASS_FROM, SANDBOX_MODE
from openprocurement.api.utils import get_now

from openprocurement.tender.esco.models import TenderESCO


# TenderESCOTest


def simple_add_tender(self):
    u = TenderESCO(self.initial_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb['tenderID']
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "esco"
    assert fromdb['procurementMethodType'] == "esco"

    u.delete_instance(self.db)


def tender_value(self):
    invalid_data = deepcopy(self.initial_data)
    value = {
        "value": {
            "amount": 100
        }
    }
    invalid_data['value'] = value
    response = self.app.post_json('/tenders', {'data': invalid_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"value": {"amount": 100}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location': u'body', u'name': u'value'}
    ])


def tender_min_value(self):
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    owner_token = response.json['access']['token']
    self.assertIn('minValue', response.json['data'])
    self.assertEqual(response.json['data']['minValue']['amount'], 0)
    self.assertEqual(response.json['data']['minValue']['currency'], 'UAH')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"minValue": {"amount": 1500}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('minValue', response.json['data'])
    self.assertEqual(response.json['data']['minValue']['amount'], 0)
    self.assertEqual(response.json['data']['minValue']['currency'], 'UAH')


def tender_minimal_step_invalid(self):
    data = self.initial_data
    data['minimalStep'] = {'amount': 100}
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    owner_token = response.json['access']['token']
    self.assertNotIn('minimalStep', response.json['data'])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"minimalStep": {"amount": 100}}})
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('minimalStep', response.json['data'])


# TestTenderEU


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

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'esco',
                                  'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'esco',
                                                          'minValue': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            u'Please use a mapping for this field or Value instance instead of unicode.'], u'location': u'body', u'name': u'minValue'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'esco',
                                                          'procurementMethod': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn({u'description': [u"Value must be one of ['open', 'selective', 'limited']."], u'location': u'body',
                   u'name': u'procurementMethod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'tenderPeriod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'esco',
                                                          'enquiryPeriod': {'endDate': 'invalid_value'}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'endDate': [u"Could not parse invalid_value. Should be ISO8601."]}, u'location': u'body', u'name': u'enquiryPeriod'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'esco',
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

    data = self.initial_data['minimalStepPercentage']
    self.initial_data['minimalStepPercentage'] = 0.001
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Float value should be greater than 0.005.'], u'location': u'body', u'name': u'minimalStepPercentage'}
    ])
    self.initial_data['minimalStepPercentage'] = 0.5
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Float value should be less than 0.03.'], u'location': u'body', u'name': u'minimalStepPercentage'}
    ])
    self.initial_data['minimalStepPercentage'] = data

    data = self.initial_data['fundingKind']
    self.initial_data['fundingKind'] = 'invalid funding kind'
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Value must be one of ['budget', 'other']."], u'location': u'body', u'name': u'fundingKind'}
    ])
    self.initial_data['fundingKind'] = data

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

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"minimalStepPercentage": 0.025}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['minimalStepPercentage'], 0.025)

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"fundingKind": "budget"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['fundingKind'], 'budget')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"fundingKind": "other"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['fundingKind'], 'other')

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


def tender_with_nbu_discount_rate(self):
    data = deepcopy(self.initial_data)
    del data['NBUdiscountRate']
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'],
         u'location': u'body', u'name': u'NBUdiscountRate'}
    ])

    data = deepcopy(self.initial_data)
    data.update({'id': 'hash', 'doc_id': 'hash2', 'tenderID': 'hash3'})
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    owner_token = response.json['access']['token']
    if 'procurementMethodDetails' in tender:
        tender.pop('procurementMethodDetails')
    self.assertEqual(set(tender), set([
        u'procurementMethodType', u'id', u'dateModified', u'tenderID',
        u'status', u'enquiryPeriod', u'tenderPeriod', u'auctionPeriod',
        u'complaintPeriod', u'items', u'minValue', u'owner', u'minimalStepPercentage',
        u'procuringEntity', u'next_check', u'procurementMethod', u'submissionMethodDetails',  # TODO: remove u'submissionMethodDetails' from set after adding auction
        u'awardCriteria', u'submissionMethod', u'title', u'title_en',  u'date', u'NBUdiscountRate',
        u'fundingKind', u'yearlyPaymentsPercentageRange']))
    self.assertNotEqual(data['id'], tender['id'])
    self.assertNotEqual(data['doc_id'], tender['id'])
    self.assertNotEqual(data['tenderID'], tender['tenderID'])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                   {"data": {"NBUdiscountRate": 1.2}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Float value should be less than 0.99.'],
         u'location': u'body', u'name': u'NBUdiscountRate'}
    ])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                   {"data": {"NBUdiscountRate": -2}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Float value should be greater than 0.'],
         u'location': u'body', u'name': u'NBUdiscountRate'}
    ])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                   {"data": {"NBUdiscountRate": 0.3}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('NBUdiscountRate', response.json['data'])
    self.assertEqual(response.json['data']['NBUdiscountRate'], 0.3)


def invalid_bid_tender_features(self):
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
    response = self.app.post_json('/tenders', {"data": data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']

    # create bid
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update({'parameters': [{
        'code': 'OCDS-123454-POSTPONEMENT', 'value': 0.1}]
    })
    invalid_bid_data = deepcopy(bid_data)
    invalid_bid_data.update({'value': {'amount': 500}})
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': invalid_bid_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'location': u'body', u'name': u'value',
         u'description': {u'contractDuration': [u'This field is required.'],
                          u'annualCostsReduction': [u'This field is required.'],
                          u'yearlyPayments': [u'This field is required.']}}
    ])

    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': bid_data})
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

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {'id': tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
    self.assertNotEqual(response.json['data']['date'], tender['date'])


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
        u'status', u'enquiryPeriod', u'tenderPeriod', u'auctionPeriod', u'submissionMethodDetails',  # TODO: remove u'submissionMethodDetails' from set after adding auction
        u'complaintPeriod', u'items', u'minValue', u'owner', u'minimalStepPercentage',
        u'procuringEntity', u'next_check', u'procurementMethod', u'NBUdiscountRate',
        u'awardCriteria', u'submissionMethod', u'title', u'title_en',  u'date',
        u'fundingKind', u'yearlyPaymentsPercentageRange']))
    self.assertNotEqual(data['id'], tender['id'])
    self.assertNotEqual(data['doc_id'], tender['id'])
    self.assertNotEqual(data['tenderID'], tender['tenderID'])


# TODO: remove this test after adding auction
def tender_submission_method_details_no_auction_only(self):
    response = self.app.get('/tenders')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    my_data = deepcopy(self.initial_data)
    my_data['submissionMethodDetails'] = 'quick(mode:fast-forward)'

    response = self.app.post_json('/tenders', {"data": my_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description':
             u'Invalid field value "quick(mode:fast-forward)". Only "quick(mode:no-auction)" is allowed while auction module for this type of procedure is not fully implemented',
             u'location': u'data',
             u'name': u'submissionMethodDetails'}
    ])

    response = self.app.post_json('/tenders', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['submissionMethodDetails'], "quick(mode:no-auction)")
    tender = response.json['data']
    self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']

    response = self.app.get('/tenders/{}'.format(tender['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(tender))
    self.assertEqual(response.json['data'], tender)
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'submissionMethodDetails': "quick(mode:fast-forward)"}}, status=403)

    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Invalid field value "quick(mode:fast-forward)". Only "quick(mode:no-auction)" is allowed while auction module for this type of procedure is not fully implemented',
         u'location': u'data',
         u'name': u'submissionMethodDetails'}
    ])

    response = self.app.get('/tenders/{}'.format(tender['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['submissionMethodDetails'], "quick(mode:no-auction)")
