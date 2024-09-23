import os
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import (
    test_docs_bid_document,
    test_docs_bid_document2,
    test_docs_bid_draft,
    test_docs_lot_bid,
    test_docs_lot_bid2,
    test_docs_lot_bid3_with_docs,
    test_docs_lots,
    test_docs_qualified,
    test_docs_question,
    test_docs_subcontracting,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

from openprocurement.api.utils import get_now
from openprocurement.tender.cfaua.constants import CLARIFICATIONS_UNTIL_PERIOD
from openprocurement.tender.cfaua.tests.base import test_tender_cfaua_data
from openprocurement.tender.cfaua.tests.tender import BaseTenderWebTest
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.tender.core.tests.criteria_utils import generate_responses

bid = deepcopy(test_docs_lot_bid)
bid2 = deepcopy(test_docs_lot_bid2)
bid3 = deepcopy(test_docs_lot_bid3_with_docs)
bid_document = deepcopy(test_docs_bid_document)
bid_document2 = deepcopy(test_docs_bid_document2)
test_tender_data = deepcopy(test_tender_cfaua_data)
test_lots = deepcopy(test_docs_lots)

bid.update(test_docs_subcontracting)
bid.update(test_docs_qualified)
bid2.update(test_docs_qualified)
bid3.update(test_docs_qualified)

TARGET_DIR = 'docs/source/tendering/cfaua/tutorial/'
TARGET_CSV_DIR = 'docs/source/tendering/cfaua/csv/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="closeFrameworkAgreementUA",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        self.app.authorization = ('Basic', ('broker', ''))

        # Creating tender

        lot = deepcopy(test_lots[0])
        lot['id'] = uuid4().hex
        lot['value'] = test_tender_cfaua_data['value']
        lot['minimalStep'] = test_tender_cfaua_data['minimalStep']
        second_item = deepcopy(test_tender_cfaua_data['items'][0])
        second_item['unit']['code'] = 'GRM'
        test_tender_cfaua_data['items'] = [test_tender_cfaua_data['items'][0], second_item]
        test_tender_cfaua_data['lots'] = [lot]
        for item in test_tender_cfaua_data['items']:
            item['relatedLot'] = lot['id']

        test_tender_cfaua_data.update({"tenderPeriod": {"endDate": (get_now() + timedelta(days=31)).isoformat()}})

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': test_tender_cfaua_data, 'config': self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        #### Tender activating
        test_criteria_data = deepcopy(test_exclusion_criteria)
        test_criteria_data.extend(test_language_criteria)

        with open(TARGET_DIR + 'add-exclusion-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/criteria?acc_token={}'.format(tender['id'], owner_token), {'data': test_criteria_data}
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tender-activating.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'active-tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.set_status('active.tendering', startend="enquiry_end")

        with open(TARGET_DIR + 'blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        tender = response.json["data"]

        with open(TARGET_DIR + 'initial-tender-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Modifying tender

        tender_period_end_date = get_now() + timedelta(days=30, seconds=10)
        with open(TARGET_DIR + 'patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {
                    'data': {
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        }
                    }
                },
            )

        with open(TARGET_DIR + 'tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Setting Bid guarantee

        with open(TARGET_DIR + 'set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], owner_token),
                {"data": {"guarantee": {"amount": 8, "currency": "USD"}}},
            )
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        # Uploading documentation

        with open(TARGET_DIR + 'upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {
                    "data": {
                        "title": "Notice.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {
                    "data": {
                        "title": "AwardCriteria.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                {
                    "data": {
                        "title": "AwardCriteria.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # Enquiries

        with open(TARGET_DIR + 'ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id), {'data': test_docs_question}, status=201
            )
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id, question_id, owner_token),
                {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
                status=200,
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        self.set_enquiry_period_end()

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]

        with open(TARGET_DIR + 'ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id), {'data': test_docs_question}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'update-tender-after-enqiery-with-update-periods.http', 'w') as self.app.file_obj:
            tender_period_end_date = get_now() + timedelta(days=8)
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {
                    'data': {
                        "value": {"amount": 501, "currency": "UAH"},
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        },
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        # Registering bid

        bids_access = {}
        with open(TARGET_DIR + 'register-bidder.http', 'w') as self.app.file_obj:
            bid['lotValues'][0]['relatedLot'] = lot['id']
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        requirementResponses = generate_responses(self)
        with open(TARGET_DIR + 'add-requirement-responses-to-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"requirementResponses": requirementResponses}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'activate-bidder-without-proposal.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}},
                status=422,
            )

        with open(TARGET_DIR + 'upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {
                    'data': {
                        'title': 'Proposal.p7s',
                        'url': self.generate_docservice_url(),
                        'hash': 'md5:' + '0' * 32,
                        'format': 'sign/p7s',
                        'documentType': 'proposal',
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
            doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, '200 OK')

        tenderers = deepcopy(test_docs_bid_draft["tenderers"])
        tenderers[0]["name"] = "Школяр"
        with open(TARGET_DIR + 'patch-pending-bid.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {'tenderers': tenderers}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'activate-bidder-without-sign.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}},
                status=422,
            )

        # Confidentiality

        with open(TARGET_DIR + 'upload-bid-private-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {
                    "data": {
                        "title": "Proposal_top_secrets.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
            priv_doc_id = response.json['data']['id']

        # set confidentiality properties
        with open(TARGET_DIR + 'mark-bid-doc-private.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, priv_doc_id, bids_access[bid1_id]
                ),
                {
                    'data': {
                        'confidentiality': 'buyerOnly',
                        'confidentialityRationale': 'Only our company sells badgers with pink hair.',
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )

        with open(TARGET_DIR + 'upload-bid-financial-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                ),
                {
                    "data": {
                        "title": "financial_doc.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]
            ),
            {
                "data": {
                    "title": "financial_doc2.pdf",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }
            },
        )
        self.assertEqual(response.status, '201 Created')
        # financial_doc_id = response.json['data']['id']

        with open(TARGET_DIR + 'bidder-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                )
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-bid-eligibility-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/eligibility_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                ),
                {
                    "data": {
                        "title": "eligibility_doc.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'upload-bid-qualification-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/qualification_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                ),
                {
                    "data": {
                        "title": "qualification_document.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
            self.qualification_doc_id = response.json['data']['id']
        #  patch bid document by user
        with open(TARGET_DIR + 'upload-bid-qualification-document-proposal-updated.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/bids/{}/qualification_documents/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, self.qualification_doc_id, bids_access[bid1_id]
                ),
                {
                    "data": {
                        "title": "qualification_document.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        self.tick_delta = None
        self.tick(timedelta(minutes=1))
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid1_id],
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
            doc_id=doc_id,
        )
        self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
            {'data': {"status": "pending"}},
        )

        with open(TARGET_DIR + 'bidder-view-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {"value": {'amount': 501.0}}}
        )
        self.assertEqual(response.status, '200 OK')

        # Bid invalidation

        with open(TARGET_DIR + 'bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        # Bid confirmation

        self.tick()
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid1_id],
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
            doc_id=doc_id,
        )
        with open(TARGET_DIR + 'bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'register-2nd-bidder.http', 'w') as self.app.file_obj:
            bid2['lotValues'][0]['relatedLot'] = lot['id']
            bid2['status'] = 'draft'
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid2})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        self.add_sign_doc(
            self.tender_id,
            bids_access[bid2_id],
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, 'pending')

        test_docs_bid_document2.update(
            {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }
        )
        bid3["documents"] = [test_docs_bid_document, test_docs_bid_document2]
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
            bid3['status'] = 'draft'
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid3})
            bid3_id = response.json['data']['id']
            bids_access[bid3_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid3_id],
            docs_url=f"/bids/{bid3_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, 'pending')

        with open(TARGET_DIR + 'register-4rd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid3})
            bid4_id = response.json['data']['id']
            bids_access[bid4_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid4_id],
            docs_url=f"/bids/{bid4_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, 'pending')

        # Pre-qualification

        self.set_status('active.pre-qualification')
        response = self.check_chronograph()

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
                    self.tender_id, qualifications[0]['id'], owner_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
        with open(TARGET_DIR + 'approve-qualification2.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[1]['id'], owner_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'approve-qualification4.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[3]['id'], owner_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'reject-qualification3.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[2]['id'], owner_token
                ),
                {"data": {"status": "unsuccessful"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'qualificated-bids-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'rejected-bid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid3_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still
        with open(TARGET_DIR + 'pre-qualification-sign-doc-is-required.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'status': 'active.pre-qualification.stand-still'}},
                status=422,
            )
        with open(TARGET_DIR + 'upload-evaluation-reports-doc.http', 'w') as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, document_type="evaluationReports")
        with open(TARGET_DIR + 'pre-qualification-confirmation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {"data": {"status": "active.pre-qualification.stand-still"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        # Auction

        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = '{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot['id'])
        patch_data = {
            'lots': [
                {
                    'auctionUrl': auction_url,
                }
            ],
            'bids': [
                {"id": bid1_id, "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid1_id)}]},
                {"id": bid2_id, "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid2_id)}]},
                {
                    "id": bid3_id,
                },
                {"id": bid4_id, "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid4_id)}]},
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot['id'], owner_token), {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id])
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder4-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid4_id, bids_access[bid4_id])
            )
            self.assertEqual(response.status, '200 OK')

        # Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot['id']),
            {
                'data': {
                    'bids': [
                        {"id": b["id"], "lotValues": [{"value": b["lotValues"][0]["value"]}]} for b in auction_bids_data
                    ]
                }
            },
        )

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'qualifications-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_ids = [i['id'] for i in response.json['data'] if i['status'] == 'pending']

        with open(TARGET_DIR + 'unsuccessful-qualified-award.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}},
                status=422,
            )

        with open(TARGET_DIR + 'activate-non-qualified-award.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {"data": {"status": "active", "qualified": False, "eligible": True}},
                status=422,
            )

        with open(TARGET_DIR + 'award-notice-document-required.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=422,
            )
        with open(TARGET_DIR + 'award-unsuccessful-notice-document-required.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
                status=422,
            )
        with open(TARGET_DIR + 'award-add-notice-document.http', 'w') as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_ids[0]}/documents")

        with open(TARGET_DIR + 'confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, '200 OK')

        # Fill Agreement unit prices

        for award_id in award_ids[1:]:
            self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )

        #  patch award to cancelled
        with open(TARGET_DIR + 'patch-award-cancelled.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {'data': {"status": "cancelled"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualifications-list2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_ids = [i['id'] for i in response.json['data'] if i['status'] == 'pending']

        #  patch pending award to unsuccessful
        self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_ids[0]}/documents")
        with open(TARGET_DIR + 'patch-award-unsuccessful.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
            )
            self.assertEqual(response.status, '200 OK')

        #  patch unsuccessful award to cancelled
        with open(TARGET_DIR + 'patch-award-unsuccessful-cancelled.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {'data': {"status": "cancelled"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualifications-list3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_ids = [i['id'] for i in response.json['data'] if i['status'] == 'pending']

        self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_ids[0]}/documents")
        with open(TARGET_DIR + 'confirm-qualification2.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_ids[0], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, '200 OK')

        for award_id in award_ids[1:]:
            self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )

        self.set_status('active.awarded')

        with open(TARGET_DIR + 'upload-prices-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                ),
                {
                    "data": {
                        "title": "prices.xls",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/exl",
                    }
                },
            )

        with open(TARGET_DIR + 'agreements-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements'.format(self.tender_id))
        agreement_id = response.json['data'][0]['id']

        with open(TARGET_DIR + 'agreement-contracts-list.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/agreements/{}/contracts?acc_token={}'.format(self.tender_id, agreement_id, owner_token)
            )

        contracts = response.json['data']
        i = 1
        for contract in contracts:
            j = 0.5
            unit_prices = []
            for unit_price in contract['unitPrices']:
                unit_prices.append(
                    {
                        'relatedItem': unit_price['relatedItem'],
                        'value': {'amount': j, "currency": "UAH", "valueAddedTaxIncluded": True},
                    }
                )
            with open(TARGET_DIR + 'agreement-contract-unitprices{}.http'.format(i), 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/tenders/{}/agreements/{}/contracts/{}?acc_token={}'.format(
                        self.tender_id, agreement_id, contract['id'], owner_token
                    ),
                    {'data': {'unitPrices': unit_prices}},
                )
            i += 1

        # Time travel to agreement.contractPeriod.clarificationsUntil
        tender = self.mongodb.tenders.get(self.tender_id)
        tender['contractPeriod']['startDate'] = (
            get_now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)
        ).isoformat()
        tender['contractPeriod']['clarificationsUntil'] = (get_now() - timedelta(days=1)).isoformat()
        self.mongodb.tenders.save(tender)

        # Uploading contract documentation

        with open(TARGET_DIR + 'tender-agreement-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                {
                    "data": {
                        "title": "agreement_first_document.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msdoc",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tender-agreement-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements/{}/documents'.format(self.tender_id, agreement_id))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-agreement-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/agreements/{}/documents?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                {
                    "data": {
                        "title": "agreement_second_document.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msdoc",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open(TARGET_DIR + 'tender-agreement-patch-document.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, agreement_id, self.document_id, owner_token
                ),
                {
                    'data': {
                        "language": 'en',
                        'title_en': 'Title of Document',
                        'description_en': 'Description of Document',
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-agreement-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements/{}/documents'.format(self.tender_id, agreement_id))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-agreement-get.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, owner_token)
            )
            self.assertEqual(response.status, '200 OK')

        # Agreement signing

        self.tick()

        with open(TARGET_DIR + 'tender-agreement-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                {"data": {"dateSigned": get_now().isoformat()}},
            )
        self.assertIn('dateSigned', response.json['data'])

        with open(TARGET_DIR + 'tender-agreement-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                {
                    "data": {
                        "status": "active",
                        "period": {
                            "startDate": get_now().isoformat(),
                            "endDate": (get_now() + timedelta(days=4 * 365)).isoformat(),
                        },
                    }
                },
            )
        self.assertEqual(response.json['data']['status'], 'active')

        with open(TARGET_DIR + 'tender-completed.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'complete')
        # self.contract_id = response.json['data'][0]['id']

        # Rollback agreement signing
        tender = self.mongodb.tenders.get(self.tender_id)
        tender['status'] = 'active.tendering'
        tender['agreements'][0]['status'] = 'pending'
        self.mongodb.tenders.save(tender)

        # Preparing the cancellation request
        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}},
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {"data": {'reasonType': 'unFixable'}},
            )
            self.assertEqual(response.status, '200 OK')

        # Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token
                ),
                {
                    "data": {
                        "title": "Notice.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {'data': {"description": 'Changed description'}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {
                    "data": {
                        "title": "Notice.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        # Activating the request and cancelling tender
        with open(TARGET_DIR + 'pending-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "pending"}},
            )
            self.assertEqual(response.status, '200 OK')

        self.tick(delta=timedelta(days=11))
        self.check_chronograph()

        with open(TARGET_DIR + 'active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token)
            )
            self.assertEqual(response.status, '200 OK')

        # transfer agreement to unsuccessful
        tender = self.mongodb.tenders.get(self.tender_id)
        tender['status'] = 'active.awarded'
        tender['agreements'][0]['status'] = 'pending'
        del tender['cancellations']
        self.mongodb.tenders.save(tender)

        with open(TARGET_DIR + 'agreement-unsuccessful.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/agreements/{}?acc_token={}'.format(self.tender_id, agreement_id, owner_token),
                {"data": {"status": "unsuccessful"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-unsuccessful.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
