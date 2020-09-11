# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.models import get_now
from openprocurement.tender.esco.tests.base import BaseESCOWebTest

from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.data import (
    complaint, question, subcontracting, qualified,
    tender_esco, bid_draft, bid2, bid3_with_docs,
    bid_document, bid_document2, lots
)

test_tender_data = deepcopy(tender_esco)
test_lots = deepcopy(lots)
bid = deepcopy(bid_draft)
bid2 = deepcopy(bid2)
bid3 = deepcopy(bid3_with_docs)
bid_document2 = deepcopy(bid_document2)

bid.update(subcontracting)
bid.update(qualified)
bid2.update(qualified)
bid3.update(qualified)

bid.update({
    "value": {
        "annualCostsReduction": [500] + [1000] * 20,
        "yearlyPaymentsPercentage": 0.9,
        "contractDuration": {
            "years": 10,
            "days": 74
        }
    }
})

bid2.update({
    "value": {
        "annualCostsReduction": [400] + [900] * 20,
        "yearlyPaymentsPercentage": 0.85,
        "contractDuration": {
            "years": 12,
            "days": 200
        }
    }
})

bid3.update({
    "value": {
        "annualCostsReduction": [200] + [800] * 20,
        "yearlyPaymentsPercentage": 0.86,
        "contractDuration": {
            "years": 13,
            "days": 40
        }
    }
})

test_lots[0]['fundingKind'] = 'other'
test_lots[0]['minimalStepPercentage'] = test_tender_data['minimalStepPercentage']
test_lots[1]['fundingKind'] = 'other'
test_lots[1]['minimalStepPercentage'] = test_tender_data['minimalStepPercentage']

TARGET_DIR = 'docs/source/tendering/esco/tutorial/'
TARGET_DIR_MULTIPLE = 'docs/source/tendering/esco/multiple_lots_tutorial/'


class TenderResourceTest(BaseESCOWebTest, MockWebTestMixin):
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

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data})
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

        # have to make two equal requests, because after first we dont see tender list
        with open(TARGET_DIR + 'tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender

        tender_period_end_date = get_now() + timedelta(days=31)
        with open(TARGET_DIR + 'patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"tenderPeriod": {"endDate": tender_period_end_date.isoformat()}}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        # Setting Bid guarantee

        with open(TARGET_DIR + 'set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(
                    self.tender_id, owner_token),
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
            response = self.app.get(
                '/tenders/{}/documents?acc_token={}'.format(
                    self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token),
                upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(
                self.tender_id))
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
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender['id'], owner_token))
            self.assertEqual(response.status, '200 OK')
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"minValue": {'amount': 501.0}}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'update-tender-after-enqiery-with-update-periods.http', 'w') as self.app.file_obj:
            tender_period_end_date = get_now() + timedelta(days=8)
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {
                    "minValue": {
                        "amount": 501,
                        "currency": u"UAH"
                    },
                    "tenderPeriod": {
                        "endDate": tender_period_end_date.isoformat()
                    }
                }})
            self.assertEqual(response.status, '200 OK')

        ### Registering bid

        bids_access = {}
        with open(TARGET_DIR + 'register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        #### Proposal Uploading

        with open(TARGET_DIR + 'upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'upload-bid-private-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
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

        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
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

        with open(TARGET_DIR + 'bidder-view-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
            {'data': {"minValue": {'amount': 501.0}}})
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
                {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'register-2nd-bidder.http', 'w') as self.app.file_obj:
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

        with open(TARGET_DIR + 'qualifications-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, "200 OK")
            qualifications = response.json['data']['qualifications']
            self.assertEqual(len(qualifications), 3)
            self.assertEqual(qualifications[0]['bidID'], bid1_id)
            self.assertEqual(qualifications[1]['bidID'], bid2_id)
            self.assertEqual(qualifications[2]['bidID'], bid3_id)

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

        with open(TARGET_DIR + 'reject-qualification3.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[2]['id'], owner_token),
                {'data': {"status": "unsuccessful"}})
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
            }, {
                "id": bid3_id
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

        self.tick()

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open(TARGET_DIR + 'tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {"data": {
                    "contractNumber": "contract#1",
                    "value": {"amountNet": response.json['data'][0]['value']['amount'] - 1}
                }})
            self.assertEqual(response.status, '200 OK')
        self.assertEqual(
            response.json['data']['value']['amountNet'],
            response.json['data']['value']['amount'] - 1)

        with open(TARGET_DIR + 'tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {"period": {
            "startDate": (get_now()).isoformat(),
            "endDate": (get_now() + timedelta(days=365)).isoformat()
        }}
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
                upload_files=[('file', 'contract_first_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tender-contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(
                self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_second_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open(TARGET_DIR + 'tender-contract-patch-document.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, self.document_id, owner_token),
                {'data': {
                    "language": 'en',
                    'title_en': 'Title of Document',
                    'description_en': 'Description of Document'
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(
                self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        tender_contract_separate_id = response.json['data'][0]['id']

        with open(TARGET_DIR + 'tender-contract-get-separate.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, tender_contract_separate_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request

        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'unFixable'}})
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {'reasonType': 'expensesCut'}})
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation

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

        with open(TARGET_DIR + 'tender-cancelled.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(
                self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

    def test_multiple_lots(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules

        with  open(TARGET_DIR_MULTIPLE + 'tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        #### Creating tender
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR_MULTIPLE + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add lots
        with open(TARGET_DIR_MULTIPLE + 'tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
            {'data': test_lots[1]})
        self.assertEqual(response.status, '201 Created')
        lot_id2 = response.json['data']['id']

        # add relatedLot for item
        with open(TARGET_DIR_MULTIPLE + 'tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {"data": {"items": [{'relatedLot': lot_id1}, {'relatedLot': lot_id2}]}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR_MULTIPLE + 'bid-lot1.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(tender_id),
                {'data': {
                    'selfQualified': True,
                    'tenderers': bid["tenderers"],
                    'lotValues': [{
                        "subcontractingDetails": "ДКП «Орфей», Україна",
                        "value": {
                            'annualCostsReduction': [200] + [1000] * 20,
                            'yearlyPaymentsPercentage': 0.87,
                            'contractDuration': {"years": 7}
                        },
                        'relatedLot': lot_id1
                    }]
                }})
            self.assertEqual(response.status, '201 Created')
            bid1_token = response.json['access']['token']
            bid1_id = response.json['data']['id']

        with open(TARGET_DIR_MULTIPLE + 'bid-lot2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(tender_id),
                {'data': {
                    'selfQualified': True,
                    'tenderers': bid2["tenderers"],
                    'lotValues': [{
                        "value": {
                            'annualCostsReduction': [700] + [1600] * 20,
                            'yearlyPaymentsPercentage': 0.9,
                            'contractDuration': {"years": 7}
                        },
                        'relatedLot': lot_id1
                    }, {
                        "subcontractingDetails": "ДКП «Укр Прінт», Україна",
                        "value": {
                            'annualCostsReduction': [600] + [1200] * 20,
                            'yearlyPaymentsPercentage': 0.96,
                            'contractDuration': {"years": 9}
                        },
                        'relatedLot': lot_id2
                    }]
                }})
            self.assertEqual(response.status, '201 Created')
            bid2_id = response.json['data']['id']
            bid2_token = response.json['access']['token']

        with open(TARGET_DIR_MULTIPLE + 'tender-invalid-all-bids.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lot_id2, owner_token),
                {'data': {'minValue': {'amount': 400}}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'bid-lot1-invalid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'bid-lot1-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token),
                {'data': {
                    'lotValues': [{
                        "subcontractingDetails": "ДКП «Орфей»",
                        "value": {"amount": 500},
                        'relatedLot': lot_id1
                    }],
                    'status': 'pending'
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'bid-lot2-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid2_id, bid2_token),
                {'data': {
                    'lotValues': [{
                        "value": {"amount": 500},
                        'relatedLot': lot_id1
                    }],
                    'status': 'pending'
                }})
            self.assertEqual(response.status, '200 OK')
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        with open(TARGET_DIR_MULTIPLE + 'tender-view-pre-qualification.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'qualifications-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.content_type, 'application/json')
            qualifications = response.json['data']

        with open(TARGET_DIR_MULTIPLE + 'tender-activate-qualifications.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[0]['id'], owner_token),
                {"data": {
                    'status': 'active',
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualifications[1]['id'], owner_token),
            {"data": {
                'status': 'active',
                "qualified": True,
                "eligible": True
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        with open(TARGET_DIR_MULTIPLE + 'tender-view-pre-qualification-stand-still.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {"data": {"status": "active.pre-qualification.stand-still"}})
            self.assertEqual(response.status, "200 OK")
