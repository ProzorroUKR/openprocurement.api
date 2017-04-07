# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta

from openprocurement.tender.belowthreshold.tests.base import test_organization

from openprocurement.tender.core.models import get_now, CPV_ITEMS_CLASS_FROM

from openprocurement.tender.openuadefense.models import Tender


# TenderUATest
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
    assert u.procurementMethodType == "aboveThresholdUA.defense"

    u.delete_instance(self.db)


# TenderUAResourceTest
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

    response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value',
                                                 'procurementMethodType': 'aboveThresholdUA.defense'},
                                                }, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {'data': {'value': 'invalid_value', 'procurementMethodType': 'aboveThresholdUA.defense'},
                                                }, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            u'Please use a mapping for this field or Value instance instead of unicode.'], u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethod': 'invalid_value', 'procurementMethodType': 'aboveThresholdUA.defense'}
                                                }, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn({u'description': [u"Value must be one of ['open', 'selective', 'limited']."], u'location': u'body', u'name': u'procurementMethod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'tenderPeriod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStep'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])
    # self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'enquiryPeriod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])

    response = self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': 'invalid_value'},
                                                 'procurementMethodType': 'aboveThresholdUA.defense'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'endDate': [u"Could not parse invalid_value. Should be ISO8601."]}, u'location': u'body', u'name': u'enquiryPeriod'}
    ])

    response = self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': '9999-12-31T23:59:59.999999'},
                                                'procurementMethodType': 'aboveThresholdUA.defense'}}, status=422)
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

    # data = self.initial_data['tenderPeriod']
    # self.initial_data['tenderPeriod'] = {'startDate': '2014-10-31T00:00:00', 'endDate': '2015-10-01T00:00:00'}
    # response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    # self.initial_data['tenderPeriod'] = data
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'description': [u'period should begin after enquiryPeriod'], u'location': u'body', u'name': u'tenderPeriod'}
    # ])

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

    self.initial_data['auctionPeriod'] = {'startDate': (now + timedelta(days=16)).isoformat(), 'endDate': (now + timedelta(days=16)).isoformat()}
    self.initial_data['awardPeriod'] = {'startDate': (now + timedelta(days=15)).isoformat(), 'endDate': (now + timedelta(days=15)).isoformat()}
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

    data = test_organization["contactPoint"]["telephone"]
    del self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'contactPoint': {u'email': [u'telephone or email should be present']}}, u'location': u'body', u'name': u'procuringEntity'}
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

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'status': 'cancelled'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['status'], 'cancelled')

    response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'cancelled'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['status'], 'cancelled')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'procuringEntity': {'kind': 'general'}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['procuringEntity']['kind'], 'general')

    response = self.app.patch_json('/tenders/{}'.format(tender['id']),
        {'data': {'tenderPeriod': {'startDate': tender['enquiryPeriod']['endDate']}}},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [{
            "location": "body",
            "name": "tenderPeriod",
            "description": [
                "tenderPeriod should be greater than 6 working days"
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
        "id": "44620000-2",
        "description": "Cartons 2"
    }}]}}, status=200)

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"classification": {
        "scheme": "CPV",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах"
    }}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't change classification")

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"additionalClassifications": [
        tender['items'][0]["additionalClassifications"][0] for i in range(3)
    ]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'items': [{"additionalClassifications": tender['items'][0]["additionalClassifications"]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        tender['id'], owner_token), {'data': {'enquiryPeriod': {'endDate': new_dateModified2}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't change enquiryPeriod")

    self.set_status('complete')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'status': 'active.auction'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update tender in current (complete) status")


def patch_tender_ua(self):
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    owner_token = response.json['access']['token']
    dateModified = tender.pop('dateModified')
    self.tender_id = tender['id']
    self.go_to_enquiryPeriod_end()

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {"value": {
        "amount": 501,
        "currency": u"UAH"
    }}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "tenderPeriod should be extended by 2 working days")
    tenderPeriod_endDate = get_now() + timedelta(days=7, seconds=10)
    #enquiryPeriod_endDate = tenderPeriod_endDate - timedelta(days=2)
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data':
        {
            "value": {
                "amount": 501,
                "currency": u"UAH"
            },
            "tenderPeriod": {
                "endDate": tenderPeriod_endDate.isoformat()
            }
        }
    })
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['tenderPeriod']['endDate'], tenderPeriod_endDate.isoformat())
    #self.assertEqual(response.json['data']['enquiryPeriod']['endDate'], enquiryPeriod_endDate.isoformat())


# TenderUAProcessTest
def one_valid_bid_tender_ua(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders',
                                  {"data": self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering XXX temporary action.
    response = self.set_status('active.tendering', {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}})
    self.assertIn("auctionPeriod", response.json['data'])


    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'tenderers': [test_organization], "value": {"amount": 500}, 'selfEligible': True, 'selfQualified': True}})

    bid_id = self.bid_id = response.json['data']['id']


    # switch to active.qualification
    self.set_status('active.auction', {"auctionPeriod": {"startDate": None}, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.qualification')


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
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': {'tenderers': [test_organization], "value": {"amount": 500}, 'selfEligible': True, 'selfQualified': True}})
    # switch to active.qualification
    self.set_status('active.auction', {"auctionPeriod": {"startDate": None}, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # get awards
    self.assertEqual(response.json['data']['status'], 'active.qualification')
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as unsuccessful
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
                                   {"data": {"status": "unsuccessful"}})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(tender)
    # set tender status after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
