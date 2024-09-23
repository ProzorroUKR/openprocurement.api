import os
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import (
    test_docs_bid2,
    test_docs_bid_draft,
    test_docs_complaint,
    test_docs_qualified,
    test_docs_question,
    test_docs_subcontracting,
    test_docs_tender_openua,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.tender.core.tests.criteria_utils import generate_responses
from openprocurement.tender.openua.tests.tender import BaseTenderUAWebTest

test_tender_ua_data = deepcopy(test_docs_tender_openua)
bid = deepcopy(test_docs_bid_draft)
bid2 = deepcopy(test_docs_bid2)

bid2.update(test_docs_qualified)
bid.update(test_docs_subcontracting)
bid.update(test_docs_qualified)

TARGET_DIR = 'docs/source/tendering/openua/http/'
TARGET_CSV_DIR = 'docs/source/tendering/openua/csv/'


class TenderUAResourceTest(BaseTenderUAWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_ua_data
    initial_lots = test_tender_below_lots
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
            pmt="aboveThresholdUA",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        self.app.authorization = ('Basic', ('broker', ''))

        #### Creating tender

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': test_tender_ua_data, 'config': self.initial_config}
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

        tender_period_end_date = get_now() + timedelta(days=16)
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

        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id])
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

        bid2_data = deepcopy(bid2)
        bid2_data["status"] = "draft"
        set_bid_lotvalues(bid2_data, self.initial_lots)
        with open(TARGET_DIR + 'register-2nd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid2_data})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        self.add_sign_doc(
            self.tender_id,
            bids_access[bid2_id],
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json)

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
        auction_bids_data[0]["lotValues"][0]["value"]["amount"] = 250  # too low price

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

        # get pending award
        with open(TARGET_DIR + 'get-awards-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))

        award = response.json["data"][0]
        award_id = award["id"]
        award_bid_id = award["bid_id"]
        self.assertEqual(len(award.get("milestones", "")), 1)

        with open(TARGET_DIR + 'fail-disqualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {
                    "data": {
                        "status": "unsuccessful",
                        "qualified": False,
                        "eligible": False,
                    }
                },
                status=403,
            )

        with open(TARGET_DIR + 'post-evidence-document.http', 'w') as self.app.file_obj:
            self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(
                    self.tender_id, award_bid_id, bids_access[award_bid_id]
                ),
                {
                    "data": {
                        "title": "lorem.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": "evidence",
                    }
                },
                status=201,
            )

        tender = self.mongodb.tenders.get(self.tender_id)
        tender["awards"][0]["milestones"][0]["dueDate"] = (get_now() - timedelta(days=1)).isoformat()
        self.mongodb.tenders.save(tender)

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
                status=200,
            )

        #### Preparing the cancellation request

        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'unFixable'}},
            )
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {'data': {'reasonType': 'forceMajeure'}},
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

        #### Creating tender

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': test_tender_ua_data, 'config': self.initial_config}
            )

            self.assertEqual(response.status, '201 Created')


TARGET_DIR_DOCS = 'docs/source/tendering/basic-actions/http/confidential-documents/'


class TenderConfidentialDocumentsTest(BaseTenderUAWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_ua_data
    initial_lots = deepcopy(test_tender_below_lots)
    initial_bids = [bid]
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL
    initial_status = "active.tendering"

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs(self):
        # Create tender
        response = self.app.post_json(
            '/tenders?opt_pretty=1', {'data': self.initial_data, 'config': self.initial_config}
        )
        self.assertEqual(response.status, '201 Created')
        self.tender_id = tender_id = response.json["data"]["id"]
        self.tender_token = tender_token = response.json["access"]["token"]
        self.set_status("active.tendering")

        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(tender_id),
            {"data": self.initial_bids[0]},
        )
        bid_id = response.json["data"]["id"]
        bid_token = response.json["access"]["token"]

        # create private document
        with open(TARGET_DIR_DOCS + 'create-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(tender_id, bid_id, bid_token),
                {
                    "data": {
                        "title": "private.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "confidentiality": "buyerOnly",
                        "confidentialityRationale": "This document contains some secret data that shouldn't be public",
                    }
                },
                status=201,
            )
            private_doc_id = response.json["data"]["id"]

        response = self.app.post_json(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(tender_id, bid_id, bid_token),
            {
                "data": {
                    "title": "public-to-private.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
            status=201,
        )
        public_to_private_doc_id = response.json["data"]["id"]

        # change to private
        with open(TARGET_DIR_DOCS + 'patch-public-document.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                    tender_id, bid_id, public_to_private_doc_id, bid_token
                ),
                {
                    "data": {
                        "confidentiality": "buyerOnly",
                        "confidentialityRationale": "Lol, this document contains some secret data "
                        "that shouldn't be public, I'm changing it's confidentiality",
                    }
                },
                status=200,
            )

        # just public for ex.
        self.app.post_json(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(tender_id, bid_id, bid_token),
            {
                "data": {
                    "title": "public.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
            status=201,
        )

        # switch to active.qualification
        tender = self.mongodb.tenders.get(tender_id)
        tender["status"] = "active.qualification"
        tender["awards"] = [
            {
                "id": "0" * 32,
                "bid_id": bid_id,
                "status": "pending",
            }
        ]
        self.mongodb.tenders.save(tender)

        # get list as tender owner
        with open(TARGET_DIR_DOCS + 'document-list-private.http', 'w') as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(tender_id, bid_id, tender_token)
            )
        self.assertEqual(len(response.json["data"]), 3)
        for index in range(len(response.json['data'])):
            self.assertIn("url", response.json["data"][index])

        # get list as public
        with open(TARGET_DIR_DOCS + 'document-list-public.http', 'w') as self.app.file_obj:
            response = self.app.get("/tenders/{}/bids/{}/documents".format(tender_id, bid_id))
        self.assertEqual(len(response.json["data"]), 3)
        self.assertNotIn("url", response.json["data"][0])
        self.assertNotIn("url", response.json["data"][1])
        self.assertIn("url", response.json["data"][2])


TARGET_VALUE_DIR = 'docs/source/tendering/basic-actions/http/complaints-value/'


class ComplaintsValueResourceTest(BaseTenderUAWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    initial_data = deepcopy(test_tender_ua_data)
    initial_lots = deepcopy(test_tender_below_lots)

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_complaint_value(self):
        for item in self.initial_data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat(),
            }

        self.initial_data.update(
            {
                "enquiryPeriod": {"endDate": (get_now() + timedelta(days=8)).isoformat()},
                "tenderPeriod": {"endDate": (get_now() + timedelta(days=16)).isoformat()},
            }
        )

        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.set_initial_status(response.json, "active.tendering")

        with open(TARGET_VALUE_DIR + 'complaint-creation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/complaints'.format(response.json["data"]["id"]), {'data': test_docs_complaint}
            )
            self.assertEqual(response.status, '201 Created')

        self.initial_data["value"]["currency"] = self.initial_data["minimalStep"]["currency"] = "USD"

        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.set_initial_status(response.json, "active.tendering")

        with open(TARGET_VALUE_DIR + 'complaint-creation-decoding.http', 'w') as self.app.file_obj:

            def mock_get_uah_amount_from_value(r, *_):
                raise raise_operation_error(r, "Failure of decoding data from bank.gov.ua", status=409)

            with patch(
                "openprocurement.tender.core.procedure.state.complaint.get_uah_amount_from_value",
                mock_get_uah_amount_from_value,
            ):
                self.app.post_json(
                    '/tenders/{}/complaints'.format(response.json["data"]["id"]),
                    {'data': test_docs_complaint},
                    status=409,
                )

        with open(TARGET_VALUE_DIR + 'complaint-creation-connection.http', 'w') as self.app.file_obj:

            def mock_get_uah_amount_from_value(r, *_):
                raise raise_operation_error(
                    r, "Error while getting data from bank.gov.ua: Connection closed", status=409
                )

            with patch(
                "openprocurement.tender.core.procedure.state.complaint.get_uah_amount_from_value",
                mock_get_uah_amount_from_value,
            ):
                self.app.post_json(
                    '/tenders/{}/complaints'.format(response.json["data"]["id"]),
                    {'data': test_docs_complaint},
                    status=409,
                )

        with open(TARGET_VALUE_DIR + 'complaint-creation-rur.http', 'w') as self.app.file_obj:

            def mock_get_uah_amount_from_value(r, *_):
                raise raise_operation_error(r, "Couldn't find currency RUR on bank.gov.ua", status=422)

            with patch(
                "openprocurement.tender.core.procedure.state.complaint.get_uah_amount_from_value",
                mock_get_uah_amount_from_value,
            ):
                self.app.post_json(
                    '/tenders/{}/complaints'.format(response.json["data"]["id"]),
                    {'data': test_docs_complaint},
                    status=422,
                )
