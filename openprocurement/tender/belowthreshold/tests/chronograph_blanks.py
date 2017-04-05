# -*- coding: utf-8 -*-
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_organization
)


# TenderSwitchTenderingResourceTest


def switch_to_tendering_by_tenderPeriod_startDate(self):
    self.set_status('active.tendering', {'status': 'active.enquiries', "tenderPeriod": {}})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertNotEqual(response.json['data']["status"], "active.tendering")
    self.set_status('active.tendering', {'status': self.initial_status, "enquiryPeriod": {}})
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "active.tendering")


# TenderSwitchQualificationResourceTest


def switch_to_qualification(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.qualification")
    self.assertEqual(len(response.json['data']["awards"]), 1)


# TenderSwitchAuctionResourceTest


def switch_to_auction(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.auction")


# TenderSwitchUnsuccessfulResourceTest


def switch_to_unsuccessful(self):
    self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")
    if self.initial_lots:
        self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(["unsuccessful"]))


# TenderAuctionPeriodResourceTest


def set_auction_period(self):
    self.set_status('active.tendering', {'status': 'active.enquiries'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    if self.initial_lots:
        item = response.json['data']["lots"][0]
    else:
        item = response.json['data']
    self.assertIn('auctionPeriod', item)
    self.assertIn('shouldStartAfter', item['auctionPeriod'])
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertIn('T00:00:00+', item['auctionPeriod']['shouldStartAfter'])
    self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

    if self.initial_lots:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
        item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(item['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

    if self.initial_lots:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": None}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": None}}})
        item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('startDate', item['auctionPeriod'])


def reset_auction_period(self):
    self.set_status('active.tendering', {'status': 'active.enquiries'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.tendering')
    if self.initial_lots:
        item = response.json['data']["lots"][0]
    else:
        item = response.json['data']
    self.assertIn('auctionPeriod', item)
    self.assertIn('shouldStartAfter', item['auctionPeriod'])
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

    if self.initial_lots:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
        item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertIn('9999-01-01T00:00:00', item['auctionPeriod']['startDate'])

    self.set_status('active.auction', {'status': 'active.tendering'})
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    item = response.json['data']["lots"][0] if self.initial_lots else response.json['data']
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])

    if self.initial_lots:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
        item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertIn('9999-01-01T00:00:00', item['auctionPeriod']['startDate'])
    self.assertIn('9999-01-01T00:00:00', response.json['data']['next_check'])

    now = get_now().isoformat()
    tender = self.db.get(self.tender_id)
    if self.initial_lots:
        tender['lots'][0]['auctionPeriod']['startDate'] = now
    else:
        tender['auctionPeriod']['startDate'] = now
    self.db.save(tender)

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    item = response.json['data']["lots"][0] if self.initial_lots else response.json['data']
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertGreater(response.json['data']['next_check'], item['auctionPeriod']['startDate'])
    self.assertEqual(response.json['data']['next_check'], self.db.get(self.tender_id)['next_check'])

    if self.initial_lots:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": response.json['data']['tenderPeriod']['endDate']}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": response.json['data']['tenderPeriod']['endDate']}}})
        item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertNotIn('9999-01-01T00:00:00', item['auctionPeriod']['startDate'])
    self.assertGreater(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

    tender = self.db.get(self.tender_id)
    self.assertGreater(tender['next_check'], response.json['data']['tenderPeriod']['endDate'])
    tender['tenderPeriod']['endDate'] = tender['tenderPeriod']['startDate']
    if self.initial_lots:
        tender['lots'][0]['auctionPeriod']['startDate'] = tender['tenderPeriod']['startDate']
    else:
        tender['auctionPeriod']['startDate'] = tender['tenderPeriod']['startDate']
    self.db.save(tender)

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    if self.initial_lots:
        item = response.json['data']["lots"][0]
    else:
        item = response.json['data']
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertNotIn('next_check', response.json['data'])
    self.assertNotIn('next_check', self.db.get(self.tender_id))
    shouldStartAfter = item['auctionPeriod']['shouldStartAfter']

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    if self.initial_lots:
        item = response.json['data']["lots"][0]
    else:
        item = response.json['data']
    self.assertEqual(item['auctionPeriod']['shouldStartAfter'], shouldStartAfter)
    self.assertNotIn('next_check', response.json['data'])

    if self.initial_lots:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
        item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertIn('9999-01-01T00:00:00', item['auctionPeriod']['startDate'])
    self.assertIn('9999-01-01T00:00:00', response.json['data']['next_check'])


# TenderComplaintSwitchResourceTest


def switch_to_pending(self):
    response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), {'data': {
        'title': 'complaint title',
        'description': 'complaint description',
        'author': test_organization,
        'status': 'claim'
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'claim')

    tender = self.db.get(self.tender_id)
    tender['complaints'][0]['dateSubmitted'] = (get_now() - timedelta(days=1 if 'procurementMethodDetails' in tender else 4)).isoformat()
    self.db.save(tender)

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["complaints"][0]['status'], 'pending')


def switch_to_complaint(self):
    for status in ['invalid', 'resolved', 'declined']:
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': test_organization,
            'status': 'claim'
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'claim')
        complaint = response.json['data']
        response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint['id'], self.tender_token), {"data": {
            "status": "answered",
            "resolution": status * 4,
            "resolutionType": status
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "answered")
        self.assertEqual(response.json['data']["resolutionType"], status)

        tender = self.db.get(self.tender_id)
        tender['complaints'][-1]['dateAnswered'] = (get_now() - timedelta(days=1 if 'procurementMethodDetails' in tender else 4)).isoformat()
        self.db.save(tender)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["complaints"][-1]['status'], status)


# TenderAwardComplaintSwitchResourceTest


def award_switch_to_pending(self):
    token = self.initial_bids_tokens.values()[0]
    response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, self.award_id, token), {'data': {
        'title': 'complaint title',
        'description': 'complaint description',
        'author': test_organization,
        'status': 'claim'
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'claim')

    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    tender = self.db.get(self.tender_id)
    tender['awards'][0]['complaints'][0]['dateSubmitted'] = (get_now() - timedelta(days=1 if 'procurementMethodDetails' in tender else 4)).isoformat()
    self.db.save(tender)

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['awards'][0]["complaints"][0]['status'], 'pending')


def award_switch_to_complaint(self):
    token = self.initial_bids_tokens.values()[0]
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    for status in ['invalid', 'resolved', 'declined']:
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, self.award_id, token), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': test_organization,
            'status': 'claim'
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'claim')
        complaint = response.json['data']

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'], self.tender_token), {"data": {
            "status": "answered",
            "resolution": status * 4,
            "resolutionType": status
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "answered")
        self.assertEqual(response.json['data']["resolutionType"], status)

        tender = self.db.get(self.tender_id)
        tender['awards'][0]['complaints'][-1]['dateAnswered'] = (get_now() - timedelta(days=1 if 'procurementMethodDetails' in tender else 4)).isoformat()
        self.db.save(tender)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['awards'][0]["complaints"][-1]['status'], status)
