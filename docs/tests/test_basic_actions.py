# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta
from mock import patch
from openprocurement.tender.core.tests.base import change_auth
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.models import get_now
from openprocurement.tender.openeu.tests.tender import BaseTenderWebTest

from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.base.data import (
    question, complaint, claim, lots, subcontracting,
    bid_draft, bid2, bid3_with_docs,
    qualified, tender_openeu
)
from tests.base.helpers import complaint_create_pending

test_tender_data = deepcopy(tender_openeu)
test_lots = deepcopy(lots)
bid = deepcopy(bid_draft)
bid2 = deepcopy(bid2)
bid3 = deepcopy(bid3_with_docs)

bid.update(subcontracting)
bid.update(qualified)
bid2.update(qualified)
bid3.update(qualified)

test_lots[0]['value'] = test_tender_data['value']
test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
test_lots[1]['value'] = test_tender_data['value']
test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

TARGET_DIR = 'docs/source/tendering/http/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(TenderResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderResourceTest, self).tearDown()

    def test_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        with open(TARGET_DIR + 'complaints/claim-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints'.format(self.tender_id),
                {'data': claim})
            self.assertEqual(response.status, '201 Created')

        complaint_token = response.json['access']['token']
        complaint_id = response.json['data']['id']

        with open(TARGET_DIR + 'complaints/complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/complaints/{}/documents?acc_token={}'.format(self.tender_id, complaint_id,
                                                                          complaint_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint_id, complaint_token),
                {"data": {"status": "claim"}})
            self.assertEqual(response.status, '200 OK')

        claim_data = {'data': complaint.copy()}
        claim_data['data']['status'] = 'claim'
        with open(TARGET_DIR + 'complaints/complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints'.format(self.tender_id), claim_data)
            self.assertEqual(response.status, '201 Created')

        complaint2_token = response.json['access']['token']
        complaint2_id = response.json['data']['id']

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'

        complaint_url = "/tenders/{}/complaints".format(self.tender_id)
        complaint3_id, complaint3_token = complaint_create_pending(self, complaint_url, complaint_data)

        response = self.app.post_json(
            '/tenders/{}/complaints'.format(self.tender_id), claim_data)
        self.assertEqual(response.status, '201 Created')
        complaint4_id = response.json['data']['id']
        complaint4_token = response.json['access']['token']

        with open(TARGET_DIR + 'complaints/complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints'.format(self.tender_id),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'complaints/complaint-complaint.http', 'w') as self.app.file_obj:
            if get_now() < RELEASE_2020_04_19:
                response = self.app.patch_json(
                    '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint1_id, complaint1_token),
                    {"data": {"status": "pending"}})
            else:
                with change_auth(self.app, ("Basic", ("bot", ""))):
                    response = self.app.patch_json(
                        '/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id),
                        {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/complaint-answer.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint2_id, owner_token),
                {'data': {
                    "status": "answered",
                    "resolutionType": "resolved",
                    "resolution": "Виправлено неконкурентні умови"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint4_id, owner_token),
            {'data': {
                "status": "answered",
                "resolutionType": "invalid",
                "resolution": "Вимога не відповідає предмету закупівлі"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint2_id, complaint2_token),
                {"data": {
                    "satisfied": True,
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/complaint-escalate.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint4_id, complaint4_token),
                {"data": {
                    "satisfied": False,
                    "status": "pending"
                }})
            self.assertEqual(response.status, '200 OK')

        complaint5_id, complaint5_token = complaint_create_pending(self, complaint_url, complaint_data)

        complaint6_id, complaint6_token = complaint_create_pending(self, complaint_url, complaint_data)

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaints/complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint4_id),
                {'data': {
                    "status": "invalid",
                    "rejectReason": "alreadyExists"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id),
                {'data': {
                    "status": "accepted",
                    "reviewDate": get_now().isoformat(),
                    "reviewPlace": "Place of review"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/complaints/{}'.format(self.tender_id, complaint3_id),
            {'data': {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "Place of review"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/complaints/{}'.format(self.tender_id, complaint5_id),
            {'data': {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "Place of review"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/complaints/{}'.format(self.tender_id, complaint6_id),
            {'data': {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "Place of review"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/complaints/{}/documents'.format(self.tender_id, complaint1_id),
                                     upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id),
                {'data': {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint3_id),
                {'data': {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint5_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped",
                    "rejectReason": "tenderCancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'complaints/complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint1_id, owner_token),
                {'data': {
                    "tendererAction": "Умови виправлено",
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint6_id, complaint6_token),
                {"data": {
                    "cancellationReason": "Тендер скасовується замовником",
                    "status": "stopping"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaints/complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint6_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped",
                    "rejectReason": "tenderCancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json(
            '/tenders/{}/complaints'.format(self.tender_id),
            {'data': complaint})
        self.assertEqual(response.status, '201 Created')
        complaint7_id = response.json['data']['id']
        complaint7_token = response.json['access']['token']

        with open(TARGET_DIR + 'complaints/complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint7_id, complaint7_token),
                {"data": {
                    "cancellationReason": "Умови виправлено",
                    "status": "cancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        complaint_url = "/tenders/{}/complaints".format(self.tender_id)
        complaint8_id, complaint8_token = complaint_create_pending(self, complaint_url, complaint_data)

        self.app.authorization = ('Basic', ('reviewer', ''))

        with open(TARGET_DIR + 'complaints/complaint-post-reviewer-complaint-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints/{}/posts'.format(
                    self.tender_id, complaint8_id),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Відсутній документ",
                    "recipient": "complaint_owner",
                }})
            self.assertEqual(response.status, '201 Created')

        post1_id = response.json['data']['id']

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'complaints/complaint-post-complaint-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints/{}/posts?acc_token={}'.format(
                    self.tender_id, complaint8_id, complaint8_token),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Додано документ",
                    "recipient": "aboveThresholdReviewers",
                    "relatedPost": post1_id,
                    "documents": [{
                        'title': u'post_document_complaint.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf'
                    }]
                }})
            self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('reviewer', ''))

        with open(TARGET_DIR + 'complaints/complaint-post-reviewer-tender-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints/{}/posts'.format(
                    self.tender_id, complaint8_id),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Відсутній документ",
                    "recipient": "tender_owner",
                }})
            self.assertEqual(response.status, '201 Created')

        post2_id = response.json['data']['id']

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'complaints/complaint-post-tender-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints/{}/posts?acc_token={}'.format(
                    self.tender_id, complaint8_id, owner_token),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Додано документ",
                    "recipient": "aboveThresholdReviewers",
                    "relatedPost": post2_id,
                    "documents": [{
                        'title': u'post_document_tender.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf'
                    }]
                }})
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

    def test_qualification_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid})
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid_id, bid_token),
            {'data': {"status": "pending"}})

        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid2})

        # Pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json(
            '/tenders/{}'.format(self.tender_id),
            {'data': {"id": self.tender_id}})
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, "200 OK")

        self.tick()

        # active.pre-qualification.stand-still
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
            {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        qualification_id = qualifications[0]['id']

        with open(TARGET_DIR + 'complaints/qualification-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                    self.tender_id, qualification_id, bid_token),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'complaints/qualification-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/qualification-complaint-complaint.http', 'w') as self.app.file_obj:
            if get_now() < RELEASE_2020_04_19:
                response = self.app.patch_json(
                    '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                        self.tender_id, qualification_id, complaint1_id, complaint1_token),
                    {"data": {"status": "pending"}})
            else:
                with change_auth(self.app, ("Basic", ("bot", ""))):
                    response = self.app.patch_json(
                        '/tenders/{}/qualifications/{}/complaints/{}'.format(
                            self.tender_id, qualification_id, complaint1_id),
                        {"data": {"status": "pending"}})
        self.assertEqual(response.status, '200 OK')

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'

        complaint_url = "/tenders/{}/qualifications/{}/complaints".format(self.tender_id, qualification_id)
        complaint2_id, complaint2_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        complaint3_id, complaint3_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        complaint4_id, complaint4_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        complaint5_id, complaint5_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        claim_data = {'data': complaint.copy()}
        claim_data['data']['status'] = 'claim'
        with open(TARGET_DIR + 'complaints/qualification-complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                    self.tender_id, qualification_id, bid_token), claim_data)
            self.assertEqual(response.status, '201 Created')

        complaint6_token = response.json['access']['token']
        complaint6_id = response.json['data']['id']

        with open(TARGET_DIR + 'complaints/qualification-complaint-answer.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint6_id, owner_token),
                {"data": {
                    "status": "answered",
                    "resolutionType": "resolved",
                    "resolution": "Умови виправлено, вибір переможня буде розгянуто повторно"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/qualification-complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint6_id, complaint6_token),
                {"data": {
                    "satisfied": True,
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token), claim_data)
        self.assertEqual(response.status, '201 Created')
        complaint7_token = response.json['access']['token']
        complaint7_id = response.json['data']['id']

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, qualification_id, complaint7_id, owner_token),
            {'data': {
                "status": "answered",
                "resolutionType": "invalid",
                "resolution": "Вимога не відповідає предмету закупівлі"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/qualification-complaint-unsatisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint7_id, complaint7_token),
                {"data": {
                    "satisfied": False,
                }})
            self.assertEqual(response.status, '200 OK')

        complaint_url = "/tenders/{}/qualifications/{}/complaints".format(self.tender_id, qualification_id)
        complaint8_id, complaint8_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        self.app.authorization = ('Basic', ('reviewer', ''))

        with open(TARGET_DIR + 'complaints/qualification-complaint-post-reviewer-complaint-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/qualifications/{}/complaints/{}/posts'.format(
                    self.tender_id, qualification_id, complaint8_id),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Відсутній документ",
                    "recipient": "complaint_owner",
                }})
            self.assertEqual(response.status, '201 Created')

        post1_id = response.json['data']['id']

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'complaints/qualification-complaint-post-complaint-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/qualifications/{}/complaints/{}/posts?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint8_id, complaint8_token),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Додано документ",
                    "recipient": "aboveThresholdReviewers",
                    "relatedPost": post1_id,
                    "documents": [{
                        'title': u'post_document_complaint.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf'
                    }]
                }})
            self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('reviewer', ''))

        with open(TARGET_DIR + 'complaints/qualification-complaint-post-reviewer-tender-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/qualifications/{}/complaints/{}/posts'.format(
                    self.tender_id, qualification_id, complaint8_id),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Відсутній документ",
                    "recipient": "tender_owner",
                }})
            self.assertEqual(response.status, '201 Created')

        post2_id = response.json['data']['id']

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'complaints/qualification-complaint-post-tender-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/qualifications/{}/complaints/{}/posts?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint8_id, owner_token),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Додано документ",
                    "recipient": "aboveThresholdReviewers",
                    "relatedPost": post2_id,
                    "documents": [{
                        'title': u'post_document_tender.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf'
                    }]
                }})
            self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token),
            {'data': claim})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/qualification-complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id,
                    response.json['data']['id'], response.json['access']['token']),
                {"data": {
                    "status": "claim"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, bid_token),
            {'data': complaint})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/qualification-complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id,
                    response.json['data']['id'], response.json['access']['token']),
                {"data": {
                    "cancellationReason": "Умови виправлено",
                    "status": "cancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaints/qualification-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint2_id),
                {"data": {
                    "status": "invalid",
                    "rejectReason": "alreadyExists"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/qualification-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint1_id),
                {"data": {
                    "status": "accepted",
                    "reviewDate": get_now().isoformat(),
                    "reviewPlace": "Place of review"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint3_id),
            {"data": {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "Place of review"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint4_id),
            {"data": {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "Place of review"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint5_id),
            {"data": {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "Place of review"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/qualification-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/qualifications/{}/complaints/{}/documents'.format(
                    self.tender_id, qualification_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/qualification-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint1_id),
                {"data": {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/qualification-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint3_id),
                {"data": {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/qualification-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint5_id),
                {"data": {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped",
                    "rejectReason": "tenderCancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'complaints/qualification-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint1_id, owner_token),
                {"data": {
                    "tendererAction": "Умови виправлено",
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/qualification-complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint4_id, complaint4_token),
                {"data": {
                    "cancellationReason": "Тендер скасовується замовником",
                    "status": "stopping"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaints/qualification-complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint4_id),
                {"data": {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped",
                    "rejectReason": "tenderCancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = None
        with open(TARGET_DIR + 'complaints/qualification-complaints-list.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/qualifications/{}/complaints'.format(
                    self.tender_id, qualification_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/qualification-complaint.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

    def test_award_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid})
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid_id, bid_token),
            {'data': {"status": "pending"}})

        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid2})

        # Pre-qualification
        self.set_status(
            'active.pre-qualification',
            {"id": self.tender_id, 'status': 'active.tendering'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json(
            '/tenders/{}'.format(self.tender_id),
            {'data': {"id": self.tender_id}})
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualification['id'], owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
            {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
            '/tenders/{}/auction'.format(self.tender_id),
            {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
            {"data": {
                "status": "active",
                "qualified": True,
                "eligible": True
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                    self.tender_id, award_id, bid_token),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        self.tick()

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'complaints/award-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
                    self.tender_id, award_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/award-complaint-complaint.http', 'w') as self.app.file_obj:
            if get_now() < RELEASE_2020_04_19:
                response = self.app.patch_json(
                    '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                        self.tender_id, award_id, complaint1_id, complaint1_token),
                    {"data": {"status": "pending"}})
            else:
                with change_auth(self.app, ("Basic", ("bot", ""))):
                    response = self.app.patch_json(
                        '/tenders/{}/awards/{}/complaints/{}'.format(
                            self.tender_id, award_id, complaint1_id),
                        {"data": {"status": "pending"}})

            self.assertEqual(response.status, '200 OK')

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'
        # with open(TARGET_DIR + 'complaints/award-complaint-submission-complaint.http', 'w') as self.app.file_obj:
        #     response = self.app.post_json(
        #         '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
        #             self.tender_id, award_id, bid_token),
        #         complaint_data)
        #     self.assertEqual(response.status, '201 Created')
        #
        # complaint2_id = response.json['data']['id']

        complaint_url = "/tenders/{}/awards/{}/complaints".format(self.tender_id, award_id)
        complaint2_id, complaint2_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        complaint3_id, complaint3_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        complaint4_id, complaint4_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        complaint5_id, complaint5_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        claim_data = {'data': complaint.copy()}
        claim_data['data']['status'] = 'claim'
        with open(TARGET_DIR + 'complaints/award-complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                    self.tender_id, award_id, bid_token), claim_data)
            self.assertEqual(response.status, '201 Created')

        complaint6_token = response.json['access']['token']
        complaint6_id = response.json['data']['id']

        with open(TARGET_DIR + 'complaints/award-complaint-answer.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint6_id, owner_token),
                {'data': {
                    "status": "answered",
                    "resolutionType": "resolved",
                    "resolution": "Умови виправлено, вибір переможня буде розгянуто повторно"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint6_id, complaint6_token),
                {'data': {
                    "satisfied": True,
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_id, bid_token), claim_data)
        self.assertEqual(response.status, '201 Created')
        complaint7_token = response.json['access']['token']
        complaint7_id = response.json['data']['id']

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, award_id, complaint7_id, owner_token),
            {'data': {
                "status": "answered",
                "resolutionType": "invalid",
                "resolution": "Вимога не відповідає предмету закупівлі"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint-unsatisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint7_id, complaint7_token),
                {'data': {
                    "satisfied": False,
                }})
            self.assertEqual(response.status, '200 OK')

        complaint_url = "/tenders/{}/awards/{}/complaints".format(self.tender_id, award_id)
        complaint8_id, complaint8_token = complaint_create_pending(self, complaint_url, complaint_data, bid_token)

        self.app.authorization = ('Basic', ('reviewer', ''))

        with open(TARGET_DIR + 'complaints/award-complaint-post-reviewer-complaint-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints/{}/posts'.format(
                    self.tender_id, award_id, complaint8_id),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Відсутній документ",
                    "recipient": "complaint_owner",
                }})
            self.assertEqual(response.status, '201 Created')

        post1_id = response.json['data']['id']

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'complaints/award-complaint-post-complaint-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints/{}/posts?acc_token={}'.format(
                    self.tender_id, award_id, complaint8_id, complaint8_token),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Додано документ",
                    "recipient": "aboveThresholdReviewers",
                    "relatedPost": post1_id,
                    "documents": [{
                        'title': u'post_document_complaint.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf'
                    }]
                }})
            self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('reviewer', ''))

        with open(TARGET_DIR + 'complaints/award-complaint-post-reviewer-tender-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints/{}/posts'.format(
                    self.tender_id, award_id, complaint8_id),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Відсутній документ",
                    "recipient": "tender_owner",
                }})
            self.assertEqual(response.status, '201 Created')

        post2_id = response.json['data']['id']

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'complaints/award-complaint-post-tender-owner.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints/{}/posts?acc_token={}'.format(
                    self.tender_id, award_id, complaint8_id, owner_token),
                {"data": {
                    "title": "Уточнення по вимозі",
                    "description": "Додано документ",
                    "recipient": "aboveThresholdReviewers",
                    "relatedPost": post2_id,
                    "documents": [{
                        'title': u'post_document_tender.pdf',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'application/pdf'
                    }]
                }})
            self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_id, bid_token),
            {'data': claim})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/award-complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id,
                    response.json['data']['id'], response.json['access']['token']),
                {'data': {
                    "status": "claim"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaints/award-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint2_id),
                {'data': {
                    "status": "invalid",
                    "rejectReason": "alreadyExists"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id),
                {'data': {
                    "status": "accepted",
                    "reviewDate": get_now().isoformat(),
                    "reviewPlace": "Place of review"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint3_id),
            {'data': {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "Place of review"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint4_id),
            {'data': {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "Place of review"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint5_id),
            {'data': {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "Place of review"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/awards/{}/complaints/{}/documents'.format(
                    self.tender_id, award_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/award-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id),
                {'data': {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint3_id),
                {'data': {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint5_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped",
                    "rejectReason": "tenderCancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'complaints/award-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint1_id, owner_token),
                {'data': {
                    "tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно",
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint4_id, complaint4_token),
                {'data': {
                    "cancellationReason": "Тендер скасовується замовником",
                    "status": "stopping"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaints/award-complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint4_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped",
                    "rejectReason": "tenderCancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'complaints/award-complaint-satisfied-resolving.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {'data': {
                    "status": "cancelled"
                }})
            self.assertEqual(response.status, '200 OK')
            new_award_id = response.headers['Location'][-32:]

        award_id = new_award_id
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
            {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/award-complaint-submit.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                    self.tender_id, award_id, bid_token),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/award-complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id,
                    response.json['data']['id'], response.json['access']['token']),
                {'data': {
                    "cancellationReason": "Умови виправлено",
                    "status": "cancelled"
                }})
            self.assertEqual(response.status, '200 OK')

    def test_cancellation_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        # Cancellation turn to complaint_period
        response = self.app.post_json(
            '/tenders/{}/cancellations?acc_token={}'.format(
                self.tender_id, owner_token),
            {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
        cancellation_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.post(
            '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
            upload_files=[('file', u'Notice.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
            {'data': {"status": "pending"}})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/cancellation-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/complaints'.format(
                    self.tender_id, cancellation_id),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'complaints/cancellation-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/cancellations/{}/complaints/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'

        complaint_url = "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation_id)
        complaint3_id, complaint3_token = complaint_create_pending(self, complaint_url, complaint_data)

        complaint4_id, complaint4_token = complaint_create_pending(self, complaint_url, complaint_data)

        with open(TARGET_DIR + 'complaints/cancellation-complaint-complaint.http', 'w') as self.app.file_obj:
            if get_now() < RELEASE_2020_04_19:
                response = self.app.patch_json(
                    '/tenders/{}/cancellations/{}/complaints/{}?acc_token={}'.format(
                        self.tender_id, cancellation_id, complaint1_id, complaint1_token),
                    {"data": {"status": "pending"}})
            else:
                with change_auth(self.app, ("Basic", ("bot", ""))):
                    response = self.app.patch_json(
                        '/tenders/{}/cancellations/{}/complaints/{}'.format(
                            self.tender_id, cancellation_id, complaint1_id),
                        {"data": {"status": "pending"}})

            self.assertEqual(response.status, '200 OK')

        complaint5_id, complaint5_token = complaint_create_pending(self, complaint_url, complaint_data)
        complaint6_id, complaint6_token = complaint_create_pending(self, complaint_url, complaint_data)

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaints/cancellation-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint4_id),
                {'data': {
                    "status": "invalid",
                    "rejectReason": "tenderCancelled",
                    "rejectReasonDescription": "reject reason description",
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/cancellation-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint1_id),
                {'data': {
                    "status": "accepted",
                    "reviewDate": get_now().isoformat(),
                    "reviewPlace": "some",
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint3_id),
            {'data': {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "some",
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint5_id),
            {'data': {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "some",
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint6_id),
            {'data': {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "some",
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/cancellation-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/cancellations/{}/complaints/{}/documents'.format
                (self.tender_id, cancellation_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/cancellation-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint1_id),
                {'data': {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/cancellation-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint3_id),
                {'data': {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/cancellation-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint5_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped",
                    "rejectReason": "tenderCancelled",
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
            {'data': {'status': 'unsuccessful'}}
        )
        self.assertEqual(response.status_code, 200)

        with open(TARGET_DIR + 'complaints/cancellation-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, complaint1_id, owner_token),
                {'data': {
                    "tendererAction": "Умови виправлено",
                    "status": "resolved",
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaints/cancellation-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint6_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped",
                    "rejectReason": "tenderCancelled",
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        # Create new cancellations
        response = self.app.post_json(
            '/tenders/{}/cancellations?acc_token={}'.format(
                self.tender_id, owner_token),
            {'data': {'reason': 'cancellation reason', 'reasonType': 'unFixable'}})
        cancellation2_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.post(
            '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                self.tender_id, cancellation2_id, owner_token),
            upload_files=[('file', u'Notice.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}?acc_token={}'.format(
                self.tender_id, cancellation2_id, owner_token),
            {'data': {"status": "pending"}})
        self.assertEqual(response.status, '200 OK')


        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/complaints'.format(self.tender_id, cancellation2_id),
            {'data': complaint})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaints/cancellation-complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/cancellations/{}/complaints'.format(
                self.tender_id, cancellation_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints/cancellation-complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')