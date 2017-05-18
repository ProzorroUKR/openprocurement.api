# -*- coding: utf-8 -*-
from copy import deepcopy
from openprocurement.tender.esco.models import TenderESCOEU


# TenderESCOEUTest


def simple_add_tender(self):
    u = TenderESCOEU(self.initial_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb['tenderID']
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "esco.EU"
    assert fromdb['procurementMethodType'] == "esco.EU"

    u.delete_instance(self.db)


def tender_value(self):
    invalid_data = deepcopy(self.initial_data)
    invalid_data['value'] = invalid_data['minValue']
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
    self.assertEqual(response.json['data']['minValue']['amount'], 500)
    self.assertEqual(response.json['data']['minValue']['currency'], 'UAH')


    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"minValue": {"amount": 1500}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('minValue', response.json['data'])
    self.assertEqual(response.json['data']['minValue']['amount'], 1500)
    self.assertEqual(response.json['data']['minValue']['currency'], 'UAH')


# TestTenderEUResourse


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
        u'complaintPeriod', u'minimalStep', u'items', u'minValue', u'owner',
        u'procuringEntity', u'next_check', u'procurementMethod',
        u'awardCriteria', u'submissionMethod', u'title', u'title_en',  u'date', u'NBUdiscountRate']))
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

    # switch to active.qualification
    self.set_status('active.auction', {"auctionPeriod": {"startDate": None}, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
    self.assertNotEqual(response.json['data']['date'], tender['date'])


# TestTenderEUProcess


def one_bid_tender(self):
    # empty tenders listing
    response = self.app.get('/tenders')
    self.assertEqual(response.json['data'], [])
    # create tender
    response = self.app.post_json('/tenders', {'data': self.initial_data})
    tender_id = self.tender_id = response.json['data']['id']
    # create bid
    response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                  {'data': self.test_bids_data[0]})
    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {'id': tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(tender_id), {'data': {'id': tender_id}})
    # tender should switch to 'unsuccessful'
    response = self.app.get('/tenders/{}'.format(tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
