# -*- coding: utf-8 -*-
from copy import deepcopy
from openprocurement.tender.esco.models import TenderESCOEU
from openprocurement.tender.esco.tests.base import (
    test_tender_eu_data as test_tender_esco_data
)


# TenderESCOEUTest


def simple_add_tender(self):
    u = TenderESCOEU(test_tender_esco_data)
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


def tender_with_value(self):
    invalid_data = deepcopy(test_tender_esco_data)
    invalid_data['value'] = invalid_data['minValue']
    response = self.app.post_json('/tenders', {'data': invalid_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field',
            u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json('/tenders', {'data': test_tender_esco_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"value": {"amount": 100}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field',
            u'location': u'body', u'name': u'value'}
    ])


def tender_with_min_value(self):
    data = deepcopy(test_tender_esco_data)
    data.update({'id': 'hash', 'doc_id': 'hash2', 'tenderID': 'hash3'})
    response = self.app.post_json('/tenders', {'data': test_tender_esco_data})
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
        u'awardCriteria', u'submissionMethod', u'title', u'title_en',  u'date',]))
    self.assertNotEqual(data['id'], tender['id'])
    self.assertNotEqual(data['doc_id'], tender['id'])
    self.assertNotEqual(data['tenderID'], tender['tenderID'])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {"data": {"minValue": {"amount": 1500}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('minValue', response.json['data'])
    self.assertEqual(response.json['data']['minValue']['amount'], 1500)
    self.assertEqual(response.json['data']['minValue']['currency'], 'UAH')
