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
        u'complaintPeriod', u'minimalStep', u'items', u'value', u'owner',
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
