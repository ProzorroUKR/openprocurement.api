# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.models import get_now
from openprocurement.tender.openuadefense.tests.tender import BaseTenderUAWebTest

from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.base.data import (
    question, complaint, tender_defense, subcontracting,
    qualified, bid, bid2
)

test_tender_ua_data = deepcopy(tender_defense)
bid = deepcopy(bid)
bid2 = deepcopy(bid2)

bid.update(subcontracting)
bid.update(qualified)
bid2.update(qualified)

TARGET_DIR = 'docs/source/tendering/defense/http/'


class TenderUAResourceTest(BaseTenderUAWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_ua_data
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(TenderUAResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderUAResourceTest, self).tearDown()

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules

        with  open(TARGET_DIR + 'tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with  open(TARGET_DIR + 'tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(
                request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        #### Creating tender

        test_tender_ua_data["procuringEntity"]["kind"] = "defense"

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_ua_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender

        tenderPeriod_endDate = get_now() + timedelta(days=15, seconds=10)
        with open(TARGET_DIR + 'patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"tenderPeriod": {"endDate": tenderPeriod_endDate.isoformat()}}})

        with open(TARGET_DIR + 'tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        # Setting Bid guarantee

        with open(TARGET_DIR + 'set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {"guarantee": {"amount": 8, "currency": "USD"}}})
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        #### Uploading documentation

        with open(TARGET_DIR + 'upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token),
                upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(
                self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token),
                upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        #### Enquiries

        with open(TARGET_DIR + 'ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=201)
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/questions/{}?acc_token={}'.format(
                    self.tender_id, question_id, owner_token),
                {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}}, status=200)
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(
                self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        self.set_enquiry_period_end()
        self.tick()
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"value": {'amount': 501.0}}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'update-tender-after-enqiery-with-update-periods.http', 'w') as self.app.file_obj:
            tenderPeriod_endDate = get_now() + timedelta(days=8)
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {
                    "value": {
                        "amount": 501,
                        "currency": u"UAH"
                    },
                    "tenderPeriod": {
                        "endDate": tenderPeriod_endDate.isoformat()
                    }
                }})
            self.assertEqual(response.status, '200 OK')

        #### Registering bid

        bids_access = {}
        with open(TARGET_DIR + 'register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        #### Proposal Uploading

        with open(TARGET_DIR + 'upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
            {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        #### Bid invalidation

        with open(TARGET_DIR + 'bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        #### Bid confirmation

        with open(TARGET_DIR + 'bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'register-2nd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid2})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        #### Auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = u'{}/tenders/{}'.format(self.auctions_url, self.tender_id)
        patch_data = {
            'auctionUrl': auction_url,
            'bids': [{
                "id": bid1_id,
                "participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid1_id)
            }, {
                "id": bid2_id,
                "participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid2_id)
            }]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction?acc_token={}'.format(self.tender_id, owner_token),
            {'data': patch_data})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        #### Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction'.format(self.tender_id),
            {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(
            self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open(TARGET_DIR + 'tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {"data": {"value": {"amount": 238, "amountNet": 230}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Setting contract signature date

        self.tick()

        with open(TARGET_DIR + 'tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {
            "period": {"startDate": (get_now()).isoformat(), "endDate": (get_now() + timedelta(days=365)).isoformat()}}
        with open(TARGET_DIR + 'tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'period': period_dates["period"]}})
        self.assertEqual(response.status, '200 OK')

        #### Uploading contract documentation

        with open(TARGET_DIR + 'tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open(TARGET_DIR + 'tender-contract-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request

        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {'reasonType': 'unFixable'}})
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')])
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {"description": 'Changed description'}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        with open(TARGET_DIR + 'pending-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        self.tick(delta=timedelta(days=11))
        self.check_chronograph()

        with open(TARGET_DIR + 'active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        #### Creating tender

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_ua_data})
            self.assertEqual(response.status, '201 Created')

    def test_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        test_tender_ua_data["procuringEntity"]["kind"] = "defense"

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_ua_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        with open(TARGET_DIR + 'complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints'.format(self.tender_id),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/complaints/{}/documents?acc_token={}'.format(
                    self.tender_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, complaint1_id, complaint1_token),
                {"data": {"status": "claim"}})
            self.assertEqual(response.status, '200 OK')

        claim = {'data': complaint.copy()}
        claim['data']['status'] = 'claim'
        with open(TARGET_DIR + 'complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints'.format(self.tender_id), claim)
            self.assertEqual(response.status, '201 Created')

        complaint2_token = response.json['access']['token']
        complaint2_id = response.json['data']['id']

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'
        with open(TARGET_DIR + 'complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints'.format(self.tender_id), complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint3_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/complaints'.format(self.tender_id), claim)
        self.assertEqual(response.status, '201 Created')
        complaint4_id = response.json['data']['id']
        complaint4_token = response.json['access']['token']

        with open(TARGET_DIR + 'complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint1_id, complaint1_token),
                {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaint-answer.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint2_id, complaint2_token),
                {"data": {
                    "satisfied": True,
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaint-escalate.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint4_id, complaint4_token),
                {"data": {
                    "satisfied": False,
                    "status": "pending"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/complaints'.format(self.tender_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/complaints'.format(self.tender_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint6_id = response.json['data']['id']
        complaint6_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint4_id),
                {'data': {
                    "status": "invalid"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id),
                {'data': {
                    "status": "accepted"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/complaints/{}'.format(self.tender_id, complaint3_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/complaints/{}'.format(self.tender_id, complaint5_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/complaints/{}'.format(self.tender_id, complaint6_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/complaints/{}/documents'.format(self.tender_id, complaint1_id),
                                     upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id),
                {'data': {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint3_id),
                {'data': {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint5_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint1_id, owner_token),
                {'data': {
                    "tendererAction": "Умови виправлено",
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint6_id, complaint6_token),
                {"data": {
                    "cancellationReason": "Тендер скасовується замовником",
                    "status": "stopping"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}'.format(self.tender_id, complaint6_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json(
            '/tenders/{}/complaints'.format(self.tender_id),
            {'data': complaint})
        self.assertEqual(response.status, '201 Created')
        complaint7_id = response.json['data']['id']
        complaint7_token = response.json['access']['token']

        with open(TARGET_DIR + 'complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint7_id, complaint7_token),
                {"data": {
                    "cancellationReason": "Умови виправлено",
                    "status": "cancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

    def test_award_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        test_tender_ua_data["procuringEntity"]["kind"] = "defense"

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_ua_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid})
        bid_token = response.json['access']['token']

        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid2})

        # switch to active.auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
            '/tenders/{}/auction'.format(self.tender_id),
            {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, owner_token))

        self.tick()

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

        with open(TARGET_DIR + 'award-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                    self.tender_id, award_id, bid_token),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'award-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
                    self.tender_id, award_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        self.tick()

        with open(TARGET_DIR + 'award-complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint1_id, complaint1_token),
                {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'
        with open(TARGET_DIR + 'award-complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token),
                complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint2_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint3_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint4_token = response.json['access']['token']
        complaint4_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_id = response.json['data']['id']

        claim = {'data': complaint.copy()}
        claim['data']['status'] = 'claim'
        with open(TARGET_DIR + 'award-complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                    self.tender_id, award_id, bid_token), claim)
            self.assertEqual(response.status, '201 Created')

        complaint6_token = response.json['access']['token']
        complaint6_id = response.json['data']['id']

        with open(TARGET_DIR + 'award-complaint-answer.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint6_id, owner_token),
                {'data': {
                    "status": "answered",
                    "resolutionType": "resolved",
                    "resolution": "Умови виправлено, вибір переможня буде розгянуто повторно"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint6_id, complaint6_token),
                {'data': {
                    "satisfied": True,
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_id, bid_token), claim)
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

        with open(TARGET_DIR + 'award-complaint-unsatisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint7_id, complaint7_token),
                {'data': {
                    "satisfied": False,
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_id, bid_token),
            {'data': complaint})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'award-complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id,
                    response.json['data']['id'], response.json['access']['token']),
                {'data': {
                    "status": "claim"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'award-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint2_id),
                {'data': {
                    "status": "invalid"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id),
                {'data': {
                    "status": "accepted"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint3_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint4_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint5_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/awards/{}/complaints/{}/documents'.format(
                    self.tender_id, award_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'award-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id),
                {'data': {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint3_id),
                {'data': {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint5_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'award-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint1_id, owner_token),
                {'data': {
                    "tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно",
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint4_id, complaint4_token),
                {'data': {
                    "cancellationReason": "Тендер скасовується замовником",
                    "status": "stopping"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'award-complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(
                    self.tender_id, award_id, complaint4_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'award-complaint-satisfied-resolving.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, award_id, owner_token),
                {'data': {
                    "status": "cancelled"
                }})
            self.assertEqual(response.status, '200 OK')
            new_award_id = response.headers['Location'][-32:]

        award_id = new_award_id
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
            {"data": {
                "status": "active",
                "qualified": True,
                "eligible": True
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaint-submit.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                    self.tender_id, award_id, bid_token),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'award-complaint-cancel.http', 'w') as self.app.file_obj:
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
            {'data': test_tender_ua_data})
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

        with open(TARGET_DIR + 'cancellation-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/complaints'.format(
                    self.tender_id, cancellation_id),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'cancellation-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/cancellations/{}/complaints/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'
        with open(TARGET_DIR + 'cancellation-complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/complaints'.format(
                    self.tender_id, cancellation_id), complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint3_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/complaints'.format(
                self.tender_id, cancellation_id), complaint_data)
        self.assertEqual(response.status, '201 Created')

        complaint4_id = response.json['data']['id']
        complaint4_token = response.json['access']['token']

        with open(TARGET_DIR + 'cancellation-complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, complaint1_id, complaint1_token),
                {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')


        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/complaints'.format(
                self.tender_id, cancellation_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/complaints'.format(
                self.tender_id, cancellation_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint6_id = response.json['data']['id']
        complaint6_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'cancellation-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint4_id),
                {'data': {
                    "status": "invalid"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint1_id),
                {'data': {
                    "status": "accepted"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint3_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint5_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint6_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/cancellations/{}/complaints/{}/documents'.format
                (self.tender_id, cancellation_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'cancellation-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint1_id),
                {'data': {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint3_id),
                {'data': {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint5_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
            {'data': {'status': 'unsuccessful'}}
        )
        self.assertEqual(response.status_code, 200)

        with open(TARGET_DIR + 'cancellation-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, complaint1_id, owner_token),
                {'data': {
                    "tendererAction": "Умови виправлено",
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'cancellation-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint6_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
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

        with open(TARGET_DIR + 'cancellation-complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/cancellations/{}/complaints'.format(
                self.tender_id, cancellation_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')
