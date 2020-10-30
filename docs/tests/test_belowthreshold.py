# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from uuid import uuid4

import jmespath
from datetime import timedelta

from openprocurement.api.models import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest, test_tender_data, test_bids, test_lots
)
from openprocurement.tender.core.tests.base import change_auth

from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.data import (
    bid_draft, bid2_with_docs, question,
    tender_below_maximum, funder, complaint, claim,
)

test_tender_data = deepcopy(test_tender_data)

TARGET_DIR = 'docs/source/tendering/http/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_bids = test_bids
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(TenderResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderResourceTest, self).tearDown()

    def test_docs_2pc(self):
        self.app.authorization = ('Basic', ('broker', ''))

        # Creating tender in draft status

        for item in test_tender_data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat()
            }

        test_tender_data.update({
            "enquiryPeriod": {"endDate": (get_now() + timedelta(days=7)).isoformat()},
            "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()}
        })

        data = test_tender_data.copy()
        data['status'] = 'draft'

        with open(TARGET_DIR + 'tutorial/tender-post-2pc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # switch to 'active.enquiries'

        with open(TARGET_DIR + 'tutorial/tender-patch-2pc.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"status": 'active.enquiries'}})
            self.assertEqual(response.status, '200 OK')

    def test_docs_tutorial(self):

        request_path = '/tenders?opt_pretty=1'

        # Exploring basic rules

        with open(TARGET_DIR + 'tutorial/tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with open(TARGET_DIR + 'tutorial/tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tutorial/tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(
                request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        # Creating tender

        for item in test_tender_data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat()
            }

        test_tender_data.update({
            "enquiryPeriod": {"endDate": (get_now() + timedelta(days=7)).isoformat()},
            "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()}
        })

        with open(TARGET_DIR + 'tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        # register proforma
        with open(TARGET_DIR + 'tutorial/upload-proforma-with-templateId.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {
                    'data': {
                        'documentType': 'contractProforma',
                        'title': u'contractProforma',
                        'templateId': "paper0000001"
                    }
                }
            )
            self.assertEqual(response.status, "201 Created")

        docs = self.app.get('/tenders/{}/documents'.format(self.tender_id)).json['data']
        self.assertIn('contractProforma', [doc['documentType'] for doc in docs])
        for doc in docs:
            if doc['documentType'] == 'contractProforma':
                proforma_id = doc['id']

        self.set_status('active.enquiries')

        with open(TARGET_DIR + 'tutorial/blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/initial-tender-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        tender_below_maximum['items'][0]['id'] = uuid4().hex
        for feature in tender_below_maximum['features']:
            if feature['featureOf'] == 'item':
                feature['relatedItem'] = tender_below_maximum['items'][0]['id']

        with open(TARGET_DIR + 'tutorial/create-tender-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': tender_below_maximum})
            self.assertEqual(response.status, '201 Created')

        test_tender_funders_data = deepcopy(test_tender_data)
        test_tender_funders_data['funders'] = [funder]
        with open(TARGET_DIR + 'tutorial/create-tender-funders.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_funders_data})
            self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/tender-listing-after-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Modifying tender

        self.tick()

        tender_period_end_date = get_now() + timedelta(days=15, seconds=10)
        with open(TARGET_DIR + 'tutorial/patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"tenderPeriod": {"endDate": tender_period_end_date.isoformat()}}})

        with open(TARGET_DIR + 'tutorial/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Setting funders

        with open(TARGET_DIR + 'tutorial/patch-tender-funders.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"funders": [funder]}})
            self.assertIn('funders', response.json['data'])
            self.assertEqual(response.status, '200 OK')

        # Setting Bid guarantee

        with open(TARGET_DIR + 'tutorial/set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {"guarantee": {"amount": 8, "currency": "USD"}}})
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        # Uploading documentation

        with open(TARGET_DIR + 'tutorial/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {
                    'title': u'Notice.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'tutorial/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}'.format(
                self.tender_id, doc_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-document-add-documentType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token),
                {'data': {"documentType": "technicalSpecifications"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-document-edit-docType-desc.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token),
                {'data': {"description": "document description modified"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {
                    'title': u'AwardCriteria.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tutorial/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                {'data': {
                    'title': u'AwardCriteria-2.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # Enquiries

        with open(TARGET_DIR + 'tutorial/ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {"data": question}, status=201)
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/questions/{}?acc_token={}'.format(
                    self.tender_id, question_id, owner_token),
                {"data": {
                    "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                }}, status=200)
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(
                self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        # rg bot upload documents
        doc_types = {
            "contractTemplate": {
                "title": "paper0000001.docx",
                "documentType": "contractTemplate",
                "format": "application/msword"
            },
            "contractForm": {
                "title": "paper0000001-form.json",
                "documentType": "contractForm",
                "format": "application/json"
            },
            "contractSchema": {
                "title": "paper0000001-schema.json",
                "documentType": "contractSchema",
                "format": "application/json"
            }
        }
        with change_auth(self.app, ("Basic", ("trBot", ""))):
            for doc_type in doc_types:
                doc_data = {
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "relatedItem": proforma_id,
                    "documentOf": "document"
                }
                doc_data.update(doc_types[doc_type])
                response = self.app.post_json("/tenders/{}/documents".format(self.tender_id), {"data": doc_data})
                self.assertEqual(response.status, "201 Created")
                self.assertEqual(response.json["data"]["documentType"], doc_data["documentType"])
                self.assertEqual(response.json["data"]["relatedItem"], proforma_id)
                self.assertEqual(response.json["data"]["documentOf"], "document")

        with open(TARGET_DIR + 'tutorial/tender-documents-after-rg-bot.http', 'w') as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents".format(self.tender_id))
        docs = [doc for doc in response.json["data"] if doc.get("documentType", "") in doc_types]
        self.assertEqual(len(docs), 3)

        # upload owner contractData
        with open(TARGET_DIR + 'tutorial/upload-owner-contract-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/documents?acc_token={}".format(self.tender_id, owner_token),
                {
                    "data": {
                        "title": "ownerContractData.json",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/json",
                        "documentOf": "document",
                        "documentType": "contractData",
                        "relatedItem": proforma_id,
                    }
                }
            )
            self.assertEqual(response.status, "201 Created")

        # renderer bot upload rendered contract proforma
        with change_auth(self.app, ("Basic", ("rBot", ""))):
            response = self.app.put(
                "/tenders/{}/documents/{}".format(self.tender_id, proforma_id),
                upload_files=[("file", "contractProforma.pdf", "contentRenderedPDF")],
            )
            self.assertEqual(response.status, "200 OK")

        # get documents list after rBot uploading contract proforma
        with open(TARGET_DIR + 'tutorial/get-tender-documents-after-rbot.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}'.format(self.tender_id, proforma_id))
            self.assertEqual(response.json['data']['title'], "contractProforma.pdf")

        # Registering bid

        self.set_status('active.tendering')

        self.app.authorization = ('Basic', ('broker', ''))
        bids_access = {}
        with open(TARGET_DIR + 'tutorial/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid_draft})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

        # Proposal Uploading

        with open(TARGET_DIR + 'tutorial/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {
                    'title': u'Proposal.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        # upload bidder contractData
        with open(TARGET_DIR + 'tutorial/upload-bidder-contract-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {
                    "title": "bidderContractData.json",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/json",
                    "documentOf": "document",
                    "documentType": "contractData",
                    "relatedItem": proforma_id,
                }}
            )
            self.assertEqual(response.status, '201 Created')

        # Second bid registration with documents

        with open(TARGET_DIR + 'tutorial/register-2nd-bidder.http', 'w') as self.app.file_obj:
            for document in bid2_with_docs['documents']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid2_with_docs})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        # Auction

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

        with open(TARGET_DIR + 'tutorial/auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        # Confirming qualification

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction'.format(self.tender_id),
            {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))

        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'tutorial/confirm-qualification.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        with open(TARGET_DIR + 'tutorial/tender-contract-get-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}'.format(
                self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open(TARGET_DIR + 'tutorial/tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {"data": {
                    "contractNumber": "contract #13111",
                    "value": {"amount": 238, "amountNet": 230}
                }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)


        #### Setting contract signature date

        self.tick()

        with open(TARGET_DIR + 'tutorial/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {"period": {
            "startDate": get_now().isoformat(),
            "endDate": (get_now() + timedelta(days=365)).isoformat()
        }}
        with open(TARGET_DIR + 'tutorial/tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'period': period_dates["period"]}})
        self.assertEqual(response.status, '200 OK')

        #### Uploading contract documentation

        with change_auth(self.app, ('Basic', ('rBot', ''))):
            response = self.app.post_json(
                "/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id),
                {
                    "data": {
                        "title": "Contract.pdf",
                        "documentType": "contract",
                        "format": "application/pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "relatedItem": proforma_id,
                        "documentOf": "document"
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')
            self.contract_pdf_doc_id = response.json['data']['id']

            response = self.app.post_json(
                "/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id),
                {
                    "data": {
                        "title": "ContractData.json",
                        "documentType": "contractData",
                        "format": "application/json",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "relatedItem": self.contract_pdf_doc_id,
                        "documentOf": "document"
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')
            self.contract_contract_data_doc_id = response.json['data']['id']

        #### Get contract generated documents

        with open(TARGET_DIR + 'tutorial/tender-contract-with-generated-documents.http', 'w') as self.app.file_obj:
            response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']['documents']), 2)
            for index, doc_type in enumerate(('contract', 'contractData')):
                self.assertEqual(response.json['data']['documents'][index]['documentType'], doc_type)
                self.assertEqual(response.json['data']['documents'][index]['author'], 'renderer_bots')

        # buyer upload fixed contract data
        with open(TARGET_DIR + 'tutorial/tender-contract-fix-contract-data-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, owner_token),
                {
                    "data": {
                        "title": "fixed_finalContractData.json",
                        "documentType": "contractData",
                        "format": "application/json",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "relatedItem": proforma_id,
                        "documentOf": "document"
                    }
                }
            )
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.json['data']['title'], 'fixed_finalContractData.json')
            self.assertEqual(response.json['data']['author'], 'tender_owner')

        # bot regenerate and upload files

        with change_auth(self.app, ('Basic', ('rBot', ''))):
            response = self.app.put_json(
                "/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id,
                                                               self.contract_pdf_doc_id),
                {
                    "data": {
                        "title": "newContract.pdf",
                        "documentType": "contract",
                        "format": "application/pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "relatedItem": proforma_id,
                        "documentOf": "document"
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')
            self.contract_pdf_doc_id = response.json['data']['id']

            response = self.app.put_json(
                "/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id,
                                                               self.contract_contract_data_doc_id),
                {
                    "data": {
                        "title": "newContractData.json",
                        "documentType": "contractData",
                        "format": "application/json",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "relatedItem": self.contract_pdf_doc_id,
                        "documentOf": "document"
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')
            self.contract_contract_data_doc_id = response.json['data']['id']


        with open(TARGET_DIR + 'tutorial/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {
                    'title': u'contract_first_document.doc',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword',
                }})
            self.assertEqual(response.status, '201 Created')

            contract_first_document_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tutorial/tender-contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(
                self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {
                    'title': u'contract_second_document.doc',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword',
                }})
            self.assertEqual(response.status, '201 Created')
            contract_second_document_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tutorial/tender-contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(
                self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        #### Setting contract signature date

        with open(TARGET_DIR + 'tutorial/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

       #### Contract signing procedure
        # Checking if contract has the `pending` status

        with open(TARGET_DIR + 'tutorial/get-tender-contracts.http', 'w') as self.app.file_obj:
            response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
            self.assertEqual(response.json["data"]["status"], "pending")
            contract = response.json["data"]
            contract_id = contract["id"]


        # Contract preparation 

        # To identify a winner supplier we need to find a bid which owner won an auction.
        # Bid and award should be in the status `active`. 

        tender = self.db.get(self.tender_id)
        bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), tender)[0]
        bid_token = jmespath.search("bids[?id=='{}'].owner_token".format(bid_id), tender)[0]

        for bid in tender.get("bids", []):
            if bid["id"] == bid_id and bid["status"] == "pending":
                bid["status"] = "active"
        for i in tender.get("awards", []):
            if 'complaintPeriod' in i:
                i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
        if 'value' in tender['contracts'][0] and tender['contracts'][0]['value']['valueAddedTaxIncluded']:
            tender['contracts'][0]['value']['amountNet'] = str(float(tender['contracts'][0]['value']['amount']) - 1)
        self.db.save(tender)

        # Changing a contract status to `pending.winner-signing` by the tender owner

        with open(TARGET_DIR + 'tutorial/change-contract-status-to-pending-winner-signing-by-owner.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, owner_token),
                {"data": {"status": "pending.winner-signing"}}
            )
            self.assertEqual(response.status, "200 OK")
        
        # Uploading a sign document to the contract document by supplier 

        with open(TARGET_DIR + 'tutorial/tender-contract-upload-sign-file-by-supplier.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
                {
                        "data": {
                            "title": u"supplier_first_document_sign.pkcs7",
                            "url": self.generate_docservice_url(),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/pkcs7-signature",
                            "documentOf": "document",
                            "relatedItem": contract_first_document_id,
                        }
                    },
                    status=201
                )
            self.assertEqual(response.status, "201 Created")
            doc_id = response.json["data"]["id"]

        # Changing a contract status to `pending` by supplier

        with open(TARGET_DIR + 'tutorial/change-contract-status-to-pending-by-supplier.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
                {"data": {"status": "pending"}}
            )
        self.assertEqual(response.status, "200 OK")

        # Uploading a sign document to the contract document by owner 

        with open(TARGET_DIR + 'tutorial/tender-contract-upload-sign-file-by-owner.http', 'w') as self.app.file_obj:

            response = self.app.post_json(
                "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, owner_token),
                {
                        "data": {
                            "title": u"owner_first_document_sign.pkcs7",
                            "url": self.generate_docservice_url(),
                            "hash": "md5:" + "0" * 32,
                            "format": "application/pkcs7-signature",
                            "documentOf": "document",
                            "relatedItem": contract_first_document_id,
                        }
                    },
                    status=201
                )
            self.assertEqual(response.status, "201 Created")
            
        # Preparing the cancellation request

        self.set_status('active.awarded')
        with open(TARGET_DIR + 'tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        # Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'tutorial/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {
                    'title': u'Notice.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {"description": 'Changed description'}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {
                    'title': u'Notice-2.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '200 OK')

        # Activating the request and cancelling tender

        with open(TARGET_DIR + 'tutorial/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

    def test_docs_milestones(self):
        self.app.authorization = ('Basic', ('broker', ''))

        for item in test_tender_data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat()
            }

        test_tender_data.update({
            "enquiryPeriod": {"endDate": (get_now() + timedelta(days=7)).isoformat()},
            "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()}
        })

        data = dict(**test_tender_data)
        data["milestones"] = [
            {
                'title': "signingTheContract",
                'code': 'prepayment',
                'type': 'financing',
                'duration': {'days': 5, 'type': 'banking'},
                'sequenceNumber': 0,
                'percentage': 45.55,
            },
            {
                'title': "deliveryOfGoods",
                'code': 'postpayment',
                'type': 'financing',
                'duration': {'days': 7, 'type': 'calendar'},
                'sequenceNumber': 1,
                'percentage': 54.45,
            },
        ]
        with open(TARGET_DIR + 'milestones/tender-post-milestones.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders', {'data': data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'milestones/tender-patch-milestones.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender["id"], owner_token),
                {"data": {
                    "milestones": [
                        {},
                        {
                            "title": "anotherEvent",
                            "description": u"Підозрілий опис",
                        }
                    ]
                }}
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender["id"], owner_token),
            {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot = response.json["data"]

        with open(TARGET_DIR + 'milestones/tender-patch-lot-milestones.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender["id"], owner_token),
                {"data": {
                    "milestones": [
                        {"relatedLot": lot["id"]},
                        {"relatedLot": lot["id"]}
                    ]
                }}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'milestones/tender-delete-lot-milestones-error.http', 'w') as self.app.file_obj:
            response = self.app.delete(
                '/tenders/{}/lots/{}?acc_token={}'.format(tender["id"], lot['id'], owner_token),
                status=422
            )
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertIn(
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "relatedLot": [
                            "relatedLot should be one of the lots."
                        ]
                    },
                    {
                        "relatedLot": [
                            "relatedLot should be one of the lots."
                        ]
                    }
                ]
            },
            response.json['errors']
        )
