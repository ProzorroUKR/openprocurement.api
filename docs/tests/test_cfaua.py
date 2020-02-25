# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta
from openprocurement.api.utils import get_now
from time import sleep
from uuid import uuid4

from openprocurement.tender.cfaua.tests.base import test_tender_data
from openprocurement.tender.cfaua.constants import CLARIFICATIONS_UNTIL_PERIOD
from openprocurement.tender.cfaua.tests.tender import BaseTenderWebTest

from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.base.data import (
    lot_bid, question, complaint, lots, lot_bid2,
    subcontracting, qualified, lot_bid3_with_docs,
    bid_document, bid_document2
)

bid = deepcopy(lot_bid)
bid2 = deepcopy(lot_bid2)
bid3 = deepcopy(lot_bid3_with_docs)
bid_document = deepcopy(bid_document)
bid_document2 = deepcopy(bid_document2)
test_tender_data = deepcopy(test_tender_data)
test_lots = deepcopy(lots)

bid.update(subcontracting)
bid.update(qualified)
bid2.update(qualified)
bid3.update(qualified)

TARGET_DIR = 'docs/source/tendering/cfaua/tutorial/'


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

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        # Exploring basic rules

        with open(TARGET_DIR + 'tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with open(TARGET_DIR + 'tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        with open(TARGET_DIR + 'tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        # Creating tender

        lot = deepcopy(test_lots[0])
        lot['id'] = uuid4().hex
        lot['value'] = test_tender_data['value']
        lot['minimalStep'] = test_tender_data['minimalStep']
        second_item = deepcopy(test_tender_data['items'][0])
        second_item['unit']['code'] = '44617100-8'
        test_tender_data['items'] = [test_tender_data['items'][0], second_item]
        test_tender_data['lots'] = [lot]
        for item in test_tender_data['items']:
            item['relatedLot'] = lot['id']

        test_tender_data.update({
            "tenderPeriod": {"endDate": (get_now() + timedelta(days=31)).isoformat()}
        })

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        self.set_status('active.enquiries')

        with open(TARGET_DIR + 'blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        # Let DB index new tender
        self.app.get('/tenders')
        sleep(2)

        with open(TARGET_DIR + 'initial-tender-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Modifying tender

        tenderPeriod_endDate = get_now() + timedelta(days=30, seconds=10)
        with open(TARGET_DIR + 'patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"tenderPeriod": {"endDate": tenderPeriod_endDate.isoformat()}}})

        with open(TARGET_DIR + 'tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Setting Bid guarantee

        with open(TARGET_DIR + 'set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], owner_token),
                {"data": {"guarantee": {"amount": 8, "currency": "USD"}}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        # Uploading documentation

        with open(TARGET_DIR + 'upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                                    upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # Enquiries

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

        self.time_shift('enquiryPeriod_ends')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender['id'], owner_token))
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"value": {'amount': 501.0}}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'update-tender-after-enqiery-with-update-periods.http',
                  'w') as self.app.file_obj:
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

        # Registering bid

        bids_access = {}
        with open(TARGET_DIR + 'register-bidder.http', 'w') as self.app.file_obj:
            bid['lotValues'][0]['relatedLot'] = lot['id']
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}}
            )
            self.assertEqual(response.status, '200 OK')

        # Proposal Uploading

        with open(TARGET_DIR + 'upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'upload-bid-private-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal_top_secrets.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')
            priv_doc_id = response.json['data']['id']

        # set confidentiality properties
        with open(TARGET_DIR + 'mark-bid-doc-private.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, priv_doc_id, bids_access[bid1_id]),
                {'data': {
                    'confidentiality': 'buyerOnly',
                    'confidentialityRationale': 'Only our company sells badgers with pink hair.',
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))

        with open(TARGET_DIR + 'upload-bid-financial-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'financial_doc.pdf', '1000$')])
            self.assertEqual(response.status, '201 Created')

        response = self.app.post(
            '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
            upload_files=[('file', 'financial_doc2.pdf', '1000$')])
        self.assertEqual(response.status, '201 Created')
        # financial_doc_id = response.json['data']['id']

        with open(TARGET_DIR + 'bidder-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-bid-eligibility-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/eligibility_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'eligibility_doc.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'upload-bid-qualification-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/qualification_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'qualification_document.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.qualification_doc_id = response.json['data']['id']
        #  patch bid document by user
        with open(TARGET_DIR + 'upload-bid-qualification-document-proposal-updated.http',
                  'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/bids/{}/qualification_documents/{}?acc_token={}'.format(
                self.tender_id, bid1_id, self.qualification_doc_id, bids_access[bid1_id]),
                upload_files=[('file', 'qualification_document2.pdf', 'content')])
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-view-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
            {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        # Bid invalidation

        with open(TARGET_DIR + 'bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        # Bid confirmation

        with open(TARGET_DIR + 'bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'register-2nd-bidder.http', 'w') as self.app.file_obj:
            bid2['lotValues'][0]['relatedLot'] = lot['id']
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid2})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        bid_document2.update({
            'confidentiality': 'buyerOnly',
            'confidentialityRationale': 'Only our company sells badgers with pink hair.'
        })
        bid3["documents"] = [bid_document, bid_document2]
        bid3['lotValues'][0]['relatedLot'] = lot['id']
        for document in bid3['documents']:
            document['url'] = self.generate_docservice_url()
        for document in bid3['eligibilityDocuments']:
            document['url'] = self.generate_docservice_url()
        for document in bid3['financialDocuments']:
            document['url'] = self.generate_docservice_url()
        for document in bid3['qualificationDocuments']:
            document['url'] = self.generate_docservice_url()

        with open(TARGET_DIR + 'register-3rd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid3})
            bid3_id = response.json['data']['id']
            bids_access[bid3_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'register-4rd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid3})
            bid4_id = response.json['data']['id']
            bids_access[bid4_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        # Pre-qualification

        self.set_status('active.pre-qualification')
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json(
            '/tenders/{}'.format(self.tender_id),
            {'data': {"id": self.tender_id}})
        self.app.authorization = auth

        with open(TARGET_DIR + 'qualifications-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
            self.assertEqual(response.status, "200 OK")
            qualifications = response.json['data']
            self.assertEqual(len(qualifications), 4)
            self.assertEqual(qualifications[0]['bidID'], bid1_id)
            self.assertEqual(qualifications[1]['bidID'], bid2_id)
            self.assertEqual(qualifications[2]['bidID'], bid3_id)
            self.assertEqual(qualifications[3]['bidID'], bid4_id)

        with open(TARGET_DIR + 'approve-qualification1.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[0]['id'], owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, "200 OK")
        with open(TARGET_DIR + 'approve-qualification2.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[1]['id'], owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'approve-qualification4.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[3]['id'], owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'reject-qualification3.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[2]['id'], owner_token),
                {"data": {"status": "unsuccessful"}})
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'qualificated-bids-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids?acc_token={}'.format(
                self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'rejected-bid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid3_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still

        with open(TARGET_DIR + 'pre-qualification-confirmation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {"data": {"status": "active.pre-qualification.stand-still"}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        # Auction

        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = u'{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot['id'])
        patch_data = {
            'lots': [{
                'auctionUrl': auction_url,
            }],
            'bids': [{
                "id": bid1_id,
                "lotValues": [{"participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid1_id)}]
            }, {
                "id": bid2_id,
                "lotValues": [{"participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid2_id)}]
            }, {
                "id": bid3_id,
            }, {
                "id": bid4_id,
                "lotValues": [{"participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid4_id)}]
            }]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot['id'], owner_token),
            {'data': patch_data})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder4-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid4_id, bids_access[bid4_id]))
            self.assertEqual(response.status, '200 OK')

        # Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot['id']),
            {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'qualifications-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_ids = [i['id'] for i in response.json['data'] if i['status'] == 'pending']

        with open(TARGET_DIR + 'confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, '200 OK')

        # Fill Agreement unit prices

        for award_id in award_ids[1:]:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})

        #  patch award to cancelled
        with open(TARGET_DIR + 'patch-award-cancelled.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, award_ids[0], owner_token),
                {'data': {"status": "cancelled"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualifications-list2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_ids = [i['id'] for i in response.json['data'] if i['status'] == 'pending']

        #  patch pending award to unsuccessful
        with open(TARGET_DIR + 'patch-award-unsuccessful.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, award_ids[0], owner_token),
                {'data': {"status": "unsuccessful"}})
            self.assertEqual(response.status, '200 OK')

        #  patch unsuccessful award to cancelled
        with open(TARGET_DIR + 'patch-award-unsuccessful-cancelled.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, award_ids[0], owner_token),
                {'data': {"status": "cancelled"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualifications-list3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_ids = [i['id'] for i in response.json['data'] if i['status'] == 'pending']

        with open(TARGET_DIR + 'confirm-qualification2.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, award_ids[0], owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, '200 OK')

        for award_id in award_ids[1:]:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})

        self.set_status('active.awarded')

        with open(TARGET_DIR + 'upload-prices-document.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'prices.xlsx', '<raw_file_data>')])

        with open(TARGET_DIR + 'agreements-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
        agreement_id = response.json['data'][0]['id']

        with open(TARGET_DIR + 'agreement-contracts-list.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/agreements/{}/contracts?acc_token={}'.format(
                    self.tender_id, agreement_id, owner_token))

        contracts = response.json['data']
        i = 1
        for contract in contracts:
            j = 0.5
            unit_prices = []
            for unit_price in contract['unitPrices']:
                unit_prices.append({'relatedItem': unit_price['relatedItem'], 'value': {'amount': j}})
            with open(TARGET_DIR + 'agreement-contract-unitprices{}.http'.format(i), 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(
                        self.tender_id, agreement_id, contract['id'], owner_token),
                    {'data': {'unitPrices': unit_prices}}
                )
            i += 1

        # Time travel to agreement.contractPeriod.clarificationsUntil
        tender = self.db.get(self.tender_id)
        tender['contractPeriod']['startDate'] = (
                get_now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)).isoformat()
        tender['contractPeriod']['clarificationsUntil'] = (get_now() - timedelta(days=1)).isoformat()
        self.db.save(tender)

        # Uploading contract documentation

        with open(TARGET_DIR + 'tender-agreement-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/agreements/{}/documents?acc_token={}'.format(
                    self.tender_id, agreement_id, owner_token),
                upload_files=[('file', 'agreement_first_document.doc', 'content')]
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tender-agreement-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements/{}/documents'.format(
                self.tender_id, agreement_id))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-agreement-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/agreements/{}/documents?acc_token={}'.format(
                    self.tender_id, agreement_id, owner_token),
                upload_files=[('file', 'agreement_second_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open(TARGET_DIR + 'tender-agreement-patch-document.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, agreement_id, self.document_id, owner_token),
                {'data': {
                    "language": 'en',
                    'title_en': 'Title of Document',
                    'description_en': 'Description of Document'
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-agreement-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements/{}/documents'.format(self.tender_id, agreement_id))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-agreement-get.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/agreements/{}?acc_token={}'.format(
                    self.tender_id, agreement_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        # Agreement signing

        self.tick()

        with open(TARGET_DIR + 'tender-agreement-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                {"data": {"dateSigned": get_now().isoformat()}})
        self.assertIn('dateSigned', response.json['data'])

        with open(TARGET_DIR + 'tender-agreement-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                {"data": {"status": "active", "period": {
                    "startDate": get_now().isoformat(),
                    "endDate": (get_now() + timedelta(days=4 * 365)).isoformat()
                }}})
        self.assertEqual(response.json['data']['status'], 'active')

        with open(TARGET_DIR + 'tender-completed.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'complete')
        # self.contract_id = response.json['data'][0]['id']

        # Rollback agreement signing
        tender = self.db.get(self.tender_id)
        tender['status'] = 'active.tendering'
        tender['agreements'][0]['status'] = 'pending'
        self.db.save(tender)

        # Preparing the cancellation request
        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {"data": {'reasonType': 'unFixable'}})
            self.assertEqual(response.status, '200 OK')

        # Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
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
            response = self.app.put(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        # Activating the request and cancelling tender

        with open(TARGET_DIR + 'active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

        # transfer agreement to unsuccessful
        tender = self.db.get(self.tender_id)
        tender['status'] = 'active.awarded'
        tender['agreements'][0]['status'] = 'pending'
        del tender['cancellations']
        self.db.save(tender)

        with open(TARGET_DIR + 'agreement-unsuccessful.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}?acc_token={}'.format(
                    self.tender_id, agreement_id, owner_token),
                {"data": {"status": "unsuccessful"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-unsuccessful.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

    def test_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        lot = deepcopy(test_lots[0])
        lot['id'] = uuid4().hex
        lot['value'] = test_tender_data['value']
        lot['minimalStep'] = test_tender_data['minimalStep']
        second_item = deepcopy(test_tender_data['items'][0])
        second_item['unit']['code'] = '44617100-8'
        test_tender_data['items'] = [test_tender_data['items'][0], second_item]
        test_tender_data['lots'] = [lot]
        for item in test_tender_data['items']:
            item['relatedLot'] = lot['id']

        test_tender_data.update({
            "tenderPeriod": {"endDate": (get_now() + timedelta(days=31)).isoformat()}
        })

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data})
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
                '/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id, complaint1_id, complaint1_token),
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

        with open(TARGET_DIR + 'complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/complaints/{}/documents'.format(self.tender_id, complaint1_id),
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
                '/tenders/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, complaint6_id, complaint6_token),
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
                '/tenders/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, complaint7_id, complaint7_token),
                {"data": {
                    "cancellationReason": "Умови виправлено",
                    "status": "cancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/complaints'.format(self.tender_id), complaint_data)
        self.assertEqual(response.status, '201 Created')

        complaint8_id = response.json['data']['id']
        complaint8_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('reviewer', ''))

        with open(TARGET_DIR + 'complaint-post-reviewer-complaint-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'complaint-post-complaint-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'complaint-post-reviewer-tender-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'complaint-post-tender-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

    def test_qualification_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        lot = deepcopy(test_lots[0])
        lot['id'] = uuid4().hex
        lot['value'] = test_tender_data['value']
        lot['minimalStep'] = test_tender_data['minimalStep']
        second_item = deepcopy(test_tender_data['items'][0])
        second_item['unit']['code'] = '44617100-8'
        test_tender_data['items'] = [test_tender_data['items'][0], second_item]
        test_tender_data['lots'] = [lot]
        for item in test_tender_data['items']:
            item['relatedLot'] = lot['id']

        test_tender_data.update({
            "tenderPeriod": {"endDate": (get_now() + timedelta(days=31)).isoformat()}
        })
        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        bid['lotValues'][0]['relatedLot'] = lot['id']
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid})
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid_id, bid_token),
            {'data': {"status": "pending"}})

        # create second and third bid
        bid2['lotValues'][0]['relatedLot'] = lot['id']
        self.app.authorization = ('Basic', ('broker', ''))
        for _ in range(2):
            self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid2})

        # Pre-qualification
        self.set_status('active.pre-qualification')
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

        self.tick()

        # active.pre-qualification.stand-still
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
            {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        qualification_id = qualifications[0]['id']

        with open(TARGET_DIR + 'qualification-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                    self.tender_id, qualification_id, bid_token),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'qualification-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'qualification-complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint1_id, complaint1_token),
                {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'
        with open(TARGET_DIR + 'qualification-complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                    self.tender_id, qualification_id, bid_token), complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint2_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token),
            complaint_data)
        self.assertEqual(response.status, '201 Created')

        complaint3_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token),
            complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint4_token = response.json['access']['token']
        complaint4_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token),
            complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_id = response.json['data']['id']

        claim = {'data': complaint.copy()}
        claim['data']['status'] = 'claim'
        with open(TARGET_DIR + 'qualification-complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                    self.tender_id, qualification_id, bid_token), claim)
            self.assertEqual(response.status, '201 Created')

        complaint6_token = response.json['access']['token']
        complaint6_id = response.json['data']['id']

        with open(TARGET_DIR + 'qualification-complaint-answer.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint6_id, owner_token),
                {"data": {
                    "status": "answered",
                    "resolutionType": "resolved",
                    "resolution": "Умови виправлено, вибір переможня буде розгянуто повторно"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualification-complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint6_id, complaint6_token),
                {"data": {
                    "satisfied": True,
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token),
            claim)
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

        with open(TARGET_DIR + 'qualification-complaint-unsatisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint7_id, complaint7_token),
                {"data": {
                    "satisfied": False,
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')

        complaint8_id = response.json['data']['id']
        complaint8_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('reviewer', ''))

        with open(TARGET_DIR + 'qualification-complaint-post-reviewer-complaint-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'qualification-complaint-post-complaint-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'qualification-complaint-post-reviewer-tender-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'qualification-complaint-post-tender-owner.http', 'w') as self.app.file_obj:
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
            {'data': complaint})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'qualification-complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id,
                    response.json['data']['id'], response.json['access']['token']),
                {"data": {
                    "status": "claim"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token),
            {'data': complaint})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'qualification-complaint-cancel.http', 'w') as self.app.file_obj:
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
        with open(TARGET_DIR + 'qualification-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint2_id),
                {"data": {
                    "status": "invalid"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualification-complaint-accept.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'qualification-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/qualifications/{}/complaints/{}/documents'.format(
                    self.tender_id, qualification_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'qualification-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint1_id),
                {"data": {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualification-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint3_id),
                {"data": {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualification-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint5_id),
                {"data": {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'qualification-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint1_id, owner_token),
                {"data": {
                    "tendererAction": "Умови виправлено",
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualification-complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, qualification_id, complaint4_id, complaint4_token),
                {"data": {
                    "cancellationReason": "Тендер скасовується замовником",
                    "status": "stopping"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'qualification-complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint4_id),
                {"data": {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = None
        with open(TARGET_DIR + 'qualification-complaints-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications/{}/complaints'.format(
                self.tender_id, qualification_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualification-complaint.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/qualifications/{}/complaints/{}'.format(
                    self.tender_id, qualification_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

    def test_award_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        lot = deepcopy(test_lots[0])
        lot['id'] = uuid4().hex
        lot['value'] = test_tender_data['value']
        lot['minimalStep'] = test_tender_data['minimalStep']
        second_item = deepcopy(test_tender_data['items'][0])
        second_item['unit']['code'] = '44617100-8'
        test_tender_data['items'] = [test_tender_data['items'][0], second_item]
        test_tender_data['lots'] = [lot]
        for item in test_tender_data['items']:
            item['relatedLot'] = lot['id']

        test_tender_data.update({
            "tenderPeriod": {"endDate": (get_now() + timedelta(days=31)).isoformat()}
        })
        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        bid['lotValues'][0]['relatedLot'] = lot['id']
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid})
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid_id, bid_token),
            {'data': {"status": "pending"}})
        # create second and third bid
        self.app.authorization = ('Basic', ('broker', ''))
        bid2['lotValues'][0]['relatedLot'] = lot['id']
        for _ in range(2):
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid2})

        # Pre-qualification
        self.set_status('active.pre-qualification')
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
            '/tenders/{}/auction/{}'.format(self.tender_id, lot['id']),
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

        self.set_status('active.qualification.stand-still')

        self.tick()

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
                '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                    self.tender_id, award_id, bid_token),
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
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')

        complaint8_id = response.json['data']['id']
        complaint8_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('reviewer', ''))

        with open(TARGET_DIR + 'award-complaint-post-reviewer-complaint-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'award-complaint-post-complaint-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'award-complaint-post-reviewer-tender-owner.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'award-complaint-post-tender-owner.http', 'w') as self.app.file_obj:
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
                '/tenders/{}/awards/{}/complaints/{}'.format(
                    self.tender_id, award_id, complaint2_id),
                {'data': {
                    "status": "invalid"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'award-complaint-accept.http', 'w') as self.app.file_obj:
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
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint4_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        awards_len = len(response.json['data'])

        with open(TARGET_DIR + 'award-complaint-satisfied-resolving.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {'data': {
                    "status": "cancelled"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        get_response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = get_response.json['data'][awards_len]['id']
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
            {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        self.set_status('active.qualification.stand-still')

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
