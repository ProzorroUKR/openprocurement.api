# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.tests.base import test_organization


# TenderAwardComplaintResourceTest

def review_tender_award_claim(self):
    for status in ['invalid', 'resolved', 'declined']:
        #self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': test_organization,
            'status': 'claim'
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        complaint_token = response.json['access']['token']

        #self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'], self.tender_token), {"data": {
            "status": "answered",
            "resolutionType": status,
            "resolution": "resolution text for {} status".format(status)
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["resolutionType"], status)

        #self.app.authorization = ('Basic', ('token', ''))
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'], complaint_token), {"data": {
            "satisfied": 'i' in status,
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["satisfied"], 'i' in status)
