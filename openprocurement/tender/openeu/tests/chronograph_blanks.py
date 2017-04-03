# -*- coding: utf-8 -*-
from copy import deepcopy

from openprocurement.tender.belowthreshold.tests.base import test_organization

# TenderSwitchPreQualificationResourceTest


def pre_qual_switch_to_auction(self):
    response = self.set_status('active.pre-qualification', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.pre-qualification")

# TenderSwitchAuctionResourceTest


def switch_to_auction(self):
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                          {"data": {'status': 'active'}})

        response = self.set_status('active.auction', {'status': 'active.pre-qualification.stand-still'})

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.auction")

# TenderSwitchUnsuccessfulResourceTest


def switch_to_unsuccessful(self):
        self.set_status('active.pre-qualification', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")

# TenderAuctionPeriodResourceTest


def set_auction_period(self):
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                   {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

    response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                   {'data': {"auctionPeriod": {"startDate": None}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('auctionPeriod', response.json['data'])

# TenderComplaintSwitchResourceTest


def switch_to_complaint(self):
        user_data = deepcopy(test_organization)
        for status in ['invalid', 'resolved', 'declined']:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), {'data': {
                'title': 'complaint title',
                'description': 'complaint description',
                'author': user_data,
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

        response = self.set_status('active.pre-qualification', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.pre-qualification")
        self.assertEqual(response.json['data']["complaints"][-1]['status'], status)
