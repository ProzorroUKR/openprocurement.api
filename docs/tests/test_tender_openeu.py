import os
from copy import deepcopy
from datetime import timedelta

from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import (
    test_docs_bid2,
    test_docs_bid3_with_docs,
    test_docs_bid_draft,
    test_docs_lots,
    test_docs_qualified,
    test_docs_question,
    test_docs_subcontracting,
    test_docs_tender_openeu,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.tender.core.tests.criteria_utils import generate_responses
from openprocurement.tender.openeu.tests.tender import BaseTenderWebTest

test_tender_data = deepcopy(test_docs_tender_openeu)
test_lots = deepcopy(test_docs_lots)
bid = deepcopy(test_docs_bid_draft)
bid2 = deepcopy(test_docs_bid2)
bid3 = deepcopy(test_docs_bid3_with_docs)

bid.update(test_docs_subcontracting)
bid.update(test_docs_qualified)
bid2.update(test_docs_qualified)
bid3.update(test_docs_qualified)

test_lots[0]['value'] = test_tender_data['value']
test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
test_lots[1]['value'] = test_tender_data['value']
test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

TARGET_DIR = 'docs/source/tendering/openeu/http/tutorial/'
TARGET_CSV_DIR = 'docs/source/tendering/openeu/csv/'

TARGET_DIR_MULTI = 'docs/source/tendering/openeu/http/multiple_lots_tutorial/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_lots = deepcopy(test_lots[:1])
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
            pmt="aboveThresholdEU",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        self.app.authorization = ('Basic', ('broker', ''))

        #### Creating tender

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {"data": test_tender_data, "config": self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender["id"]

        with open(TARGET_DIR + 'blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots
        with open(TARGET_DIR + 'tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(self.tender_id, owner_token), {'data': self.initial_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        items[1]["relatedLot"] = lot_id
        with open(TARGET_DIR + 'tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, '200 OK')

        # Tender activating

        test_criteria_data = deepcopy(test_exclusion_criteria)
        test_criteria_data.extend(test_language_criteria)

        with open(TARGET_DIR + 'add-exclusion-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/criteria?acc_token={}'.format(tender['id'], owner_token), {'data': test_criteria_data}
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'notice-document-required.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"status": "active.tendering"}},
                status=422,
            )

        with open(TARGET_DIR + 'add-notice-document.http', 'w') as self.app.file_obj:
            self.add_sign_doc(tender['id'], owner_token)

        with open(TARGET_DIR + 'tender-activating.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'active-tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender

        tender_period_end_date = get_now() + timedelta(days=31)
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
        self.tender_id = tender['id']

        # Setting Bid guarantee

        with open(TARGET_DIR + 'set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {"guarantee": {"amount": 8, "currency": "USD"}}},
            )
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        #### Uploading documentation

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

        #### Enquiries

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
        with open(TARGET_DIR + 'update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender['id'], owner_token))
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"value": {'amount': 501.0}}},
                status=403,
            )
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id), {'data': test_docs_question}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')

        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]

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

        #### Registering bid

        bids_access = {}
        bid_data = deepcopy(bid)
        set_bid_lotvalues(bid_data, self.initial_lots)
        with open(TARGET_DIR + 'register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_data})
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
                {'data': {"status": "pending"}},
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
            self.assertEqual(response.status, '200 OK')

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
            financial_doc_id = response.json['data']['id']

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
        financial_doc_id = response.json['data']['id']

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
            eligibility_doc_id = response.json['data']['id']

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

        #### Bid invalidation

        with open(TARGET_DIR + 'bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, '200 OK')

        #### Bid confirmation

        self.tick(timedelta(minutes=1))
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
            bid2_draft = deepcopy(bid2)
            bid2_draft["status"] = "draft"
            set_bid_lotvalues(bid2_draft, self.initial_lots)
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid2_draft})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid2_id],
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, "pending")

        for document in bid3['documents']:
            document['url'] = self.generate_docservice_url()
        for document in bid3['eligibilityDocuments']:
            document['url'] = self.generate_docservice_url()
        for document in bid3['financialDocuments']:
            document['url'] = self.generate_docservice_url()
        for document in bid3['qualificationDocuments']:
            document['url'] = self.generate_docservice_url()

        with open(TARGET_DIR + 'register-3rd-bidder.http', 'w') as self.app.file_obj:
            bid3_draft = deepcopy(bid3)
            bid3_draft["status"] = "draft"
            set_bid_lotvalues(bid3_draft, self.initial_lots)
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid3_draft})
            bid3_id = response.json['data']['id']
            bids_access[bid3_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid3_id],
            docs_url=f"/bids/{bid3_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, "pending")

        # Pre-qualification

        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.check_chronograph()

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

        with open(TARGET_DIR + 'reject-qualification3.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[2]['id'], owner_token
                ),
                {'data': {"status": "unsuccessful"}},
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

        #### Auction

        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = '{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot_id)
        patch_data = {
            'lots': [
                {
                    'id': lot_id,
                    'auctionUrl': auction_url,
                },
            ],
            'bids': [
                {"id": bid1_id, "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid1_id)}]},
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bid2_id)},
                    ],
                },
                {
                    "id": bid3_id,
                },
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id, owner_token), {'data': patch_data}
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

        #### Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"],
                            "lotValues": [
                                {"value": lot["value"], "relatedLot": lot["relatedLot"]} for lot in b["lotValues"]
                            ],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'unsuccessful-qualified-award.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}},
                status=422,
            )

        with open(TARGET_DIR + 'activate-non-qualified-award.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": False, "eligible": True}},
                status=422,
            )

        with open(TARGET_DIR + 'award-notice-document-required.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=422,
            )
        with open(TARGET_DIR + 'award-unsuccessful-notice-document-required.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful"}},
                status=422,
            )
        with open(TARGET_DIR + 'award-add-notice-document.http', 'w') as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")

        with open(TARGET_DIR + 'confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request

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
                {'data': {'reasonType': 'unFixable'}},
            )
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation

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

        #### Activating the request and cancelling tender
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

    def test_multiple_lots(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR_MULTI + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {"data": test_tender_data, "config": self.initial_config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add lots
        with open(TARGET_DIR_MULTI + 'tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lots[1]}
        )
        self.assertEqual(response.status, '201 Created')
        lot2 = response.json['data']
        lot_id2 = lot2['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2
        with open(TARGET_DIR_MULTI + 'tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, '200 OK')

        # Tender activating
        test_criteria_data = deepcopy(test_exclusion_criteria)
        test_criteria_data.extend(test_language_criteria)

        with open(TARGET_DIR_MULTI + 'tender-add-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{self.tender_id}/criteria?acc_token={owner_token}', {'data': test_criteria_data}
            )
            self.assertEqual(response.status, '201 Created')

        self.add_sign_doc(self.tender_id, owner_token)

        with open(TARGET_DIR_MULTI + 'activating-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{self.tender_id}?acc_token={owner_token}', {'data': {'status': 'active.tendering'}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTI + 'tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTI + 'tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR_MULTI + 'bid-lot1.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'selfQualified': True,
                        'status': 'draft',
                        'tenderers': bid["tenderers"],
                        'lotValues': [
                            {
                                "subcontractingDetails": "ДКП «Орфей», Україна",
                                "value": {"amount": 500},
                                'relatedLot': lot_id1,
                            }
                        ],
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
            bid1_token = response.json['access']['token']
            bid1_id = response.json['data']['id']
        doc1_id = self.add_sign_doc(
            self.tender_id,
            bid1_token,
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
        ).json["data"]["id"]
        self.set_responses(tender_id, response.json, "pending")

        with open(TARGET_DIR_MULTI + 'bid-lot2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'selfQualified': True,
                        'status': 'draft',
                        'tenderers': bid2["tenderers"],
                        'lotValues': [
                            {"value": {"amount": 500}, 'relatedLot': lot_id1},
                            {
                                "subcontractingDetails": "ДКП «Укр Прінт», Україна",
                                "value": {"amount": 500},
                                'relatedLot': lot_id2,
                            },
                        ],
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
            bid2_id = response.json['data']['id']
            bid2_token = response.json['access']['token']

        lot_values = response.json["data"]["lotValues"]
        doc2_id = self.add_sign_doc(
            self.tender_id,
            bid2_token,
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        ).json["data"]["id"]
        self.set_responses(tender_id, response.json, "pending")

        with open(TARGET_DIR_MULTI + 'tender-invalid-all-bids.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{tender_id}/lots/{lot_id2}?acc_token={owner_token}',
                {'data': {'value': {**lot2['value'], 'amount': 400}}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTI + 'bid-lot1-invalid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token))
            self.assertEqual(response.status, '200 OK')

        self.tick(timedelta(minutes=1))
        self.add_sign_doc(
            self.tender_id,
            bid1_token,
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
            doc_id=doc1_id,
        )

        lot_values[0].update(
            {
                "subcontractingDetails": "ДКП «Орфей»",
                "value": {"amount": 500},
                "relatedLot": lot_id1,
            }
        )

        with open(TARGET_DIR_MULTI + 'bid-lot1-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token),
                {
                    'data': {
                        'lotValues': [
                            {
                                **lot_values[0],
                                "subcontractingDetails": "ДКП «Орфей»",
                                "value": {"amount": 500},
                                "relatedLot": lot_id1,
                            }
                        ],
                        'status': 'pending',
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        lot_values[0].update(
            {
                "value": {"amount": 500},
                "relatedLot": lot_id1,
            }
        )
        self.add_sign_doc(
            self.tender_id,
            bid2_token,
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
            doc_id=doc2_id,
        )
        with open(TARGET_DIR_MULTI + 'bid-lot2-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{tender_id}/bids/{bid2_id}?acc_token={bid2_token}',
                {
                    'data': {
                        'lotValues': [
                            {
                                **lot_values[0],
                                "value": {"amount": 500},
                                "relatedLot": lot_id1,
                            }
                        ],
                        'status': 'pending',
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        with open(TARGET_DIR_MULTI + 'tender-view-pre-qualification.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTI + 'qualifications-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.content_type, 'application/json')
            qualifications = response.json['data']

        with open(TARGET_DIR_MULTI + 'tender-activate-qualifications.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[0]['id'], owner_token
                ),
                {"data": {'status': 'active', "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualifications[1]['id'], owner_token),
            {"data": {'status': 'active', "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')
        with open(TARGET_DIR_MULTI + 'pre-qualification-sign-doc-is-required.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'status': 'active.pre-qualification.stand-still'}},
                status=422,
            )
        with open(TARGET_DIR_MULTI + 'upload-evaluation-reports-doc.http', 'w') as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, document_type="evaluationReports")

        with open(TARGET_DIR_MULTI + 'tender-view-pre-qualification-stand-still.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {"data": {"status": "active.pre-qualification.stand-still"}},
            )
            self.assertEqual(response.status, "200 OK")
