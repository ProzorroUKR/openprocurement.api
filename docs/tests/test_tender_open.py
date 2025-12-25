import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.criteria_utils import generate_responses
from openprocurement.tender.core.tests.utils import set_tender_criteria
from openprocurement.tender.open.tests.base import test_tender_open_criteria
from openprocurement.tender.open.tests.tender import BaseTenderUAWebTest
from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import (
    test_docs_bid2,
    test_docs_bid_draft,
    test_docs_lots,
    test_docs_qualified,
    test_docs_question,
    test_docs_subcontracting,
    test_docs_tender_open,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

test_tender_data = deepcopy(test_docs_tender_open)
test_lots = deepcopy(test_docs_lots)
bid = deepcopy(test_docs_bid_draft)
bid2 = deepcopy(test_docs_bid2)

bid2.update(test_docs_qualified)
bid.update(test_docs_subcontracting)
bid.update(test_docs_qualified)

test_lots[0]["value"] = test_tender_data["value"]
test_lots[0]["minimalStep"] = {"amount": 5, "currency": "UAH"}
test_lots[1]["value"] = test_tender_data["value"]
test_lots[1]["minimalStep"] = {"amount": 5, "currency": "UAH"}

BASE_DIR = "docs/source/tendering/open/"
TARGET_DIR = BASE_DIR + "http/"
TARGET_CSV_DIR = BASE_DIR + "csv/"


class TenderResourceTest(BaseTenderUAWebTest, MockWebTestMixin, TenderConfigCSVMixin):
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
            pmt="aboveThreshold",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def test_docs_allowed_kind_csv(self):
        self.write_allowed_kind_csv(
            pmt="aboveThreshold",
            file_path=TARGET_CSV_DIR + "kind.csv",
        )

    def test_docs(self):
        request_path = "/tenders?opt_pretty=1"

        self.app.authorization = ("Basic", ("broker", ""))

        #### Creating tender

        with open(TARGET_DIR + "tender-post-attempt-json-data.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1", {"data": test_tender_data, "config": self.initial_config}
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        tender_id = self.tender_id = tender["id"]
        owner_token = response.json["access"]["token"]

        with open(TARGET_DIR + "blank-tender-view.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}".format(tender["id"]))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "tender-listing-no-auth.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        # add lots
        with open(TARGET_DIR + "tender-add-lot.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": test_lots[0]}
            )
            self.assertEqual(response.status, "201 Created")
            lot_id1 = response.json["data"]["id"]

        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": test_lots[1]}
        )
        self.assertEqual(response.status, "201 Created")
        lot2 = response.json["data"]
        lot_id2 = lot2["id"]

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2
        with open(TARGET_DIR + "tender-add-relatedLot-to-item.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, "200 OK")

        # add criteria
        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]

        test_criteria_data = deepcopy(test_tender_open_criteria)
        set_tender_criteria(test_criteria_data, tender["lots"], tender["items"])

        with open(TARGET_DIR + "add-exclusion-criteria.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(tender_id, owner_token), {"data": test_criteria_data}
            )
            self.assertEqual(response.status, "201 Created")

        # Tender activating
        with open(TARGET_DIR + "notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token),
                {"data": {"status": "active.tendering"}},
                status=422,
            )

        with open(TARGET_DIR + "add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(tender_id, owner_token)
        with open(TARGET_DIR + "tender-activating.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "active-tender-listing-no-auth.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, "200 OK")

        #### Modifying tender

        self.app.authorization = ("Basic", ("broker", ""))
        tender_period_end_date = get_now() + timedelta(days=16)
        with open(TARGET_DIR + "patch-items-value-periods.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token),
                {
                    "data": {
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        }
                    }
                },
            )

        with open(TARGET_DIR + "tender-listing-after-patch.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))
        self.tender_id = tender["id"]

        # Setting Bid guarantee

        with open(TARGET_DIR + "set-bid-guarantee.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"guarantee": {"amount": 8, "currency": "USD"}}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("guarantee", response.json["data"])

        #### Uploading documentation

        with open(TARGET_DIR + "upload-tender-notice.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/documents?acc_token={}".format(self.tender_id, owner_token),
                {
                    "data": {
                        "title": "Notice.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + "tender-documents.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "upload-award-criteria.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/documents?acc_token={}".format(self.tender_id, owner_token),
                {
                    "data": {
                        "title": "AwardCriteria.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + "tender-documents-2.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents?acc_token={}".format(self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "update-award-criteria.http", "w") as self.app.file_obj:
            response = self.app.put_json(
                "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, owner_token),
                {
                    "data": {
                        "title": "AwardCriteria.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "tender-documents-3.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        #### Enquiries

        with open(TARGET_DIR + "ask-question.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/questions".format(self.tender_id), {"data": test_docs_question}, status=201
            )
            question_id = response.json["data"]["id"]
            self.assertEqual(response.status, "201 Created")

        with open(TARGET_DIR + "answer-question.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question_id, owner_token),
                {"data": {"answer": 'Таблицю додано в файлі "Kalorijnist.xslx"'}},
                status=200,
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "list-question.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/questions".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "get-answer.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/questions/{}".format(self.tender_id, question_id))
            self.assertEqual(response.status, "200 OK")

        self.set_enquiry_period_end()
        self.app.authorization = ("Basic", ("broker", ""))

        with open(TARGET_DIR + "update-tender-after-enqiery.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
                {"data": {"value": {"amount": 501.0}}},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")

        with open(TARGET_DIR + "ask-question-after-enquiry-period.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/questions".format(self.tender_id), {"data": test_docs_question}, status=403
            )
            self.assertEqual(response.status, "403 Forbidden")

        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]
        with open(TARGET_DIR + "update-tender-after-enqiery-with-update-periods.http", "w") as self.app.file_obj:
            tender_period_end_date = get_now() + timedelta(days=8)
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
                {
                    "data": {
                        "value": {"amount": 501, "currency": "UAH"},
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        },
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")

        #### Registering bid
        self.app.authorization = ("Basic", ("broker", ""))
        with open(TARGET_DIR + "bid-lot1.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                f"/tenders/{tender_id}/bids",
                {
                    "data": {
                        "selfQualified": True,
                        "status": "draft",
                        "tenderers": bid["tenderers"],
                        "lotValues": [
                            {
                                "subcontractingDetails": "ДКП «Орфей», Україна",
                                "value": {"amount": 500},
                                "relatedLot": lot_id1,
                            }
                        ],
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            bid1_token = response.json["access"]["token"]
            bid1_id = response.json["data"]["id"]

        requirementResponses = generate_responses(self)
        with open(TARGET_DIR + "add-requirement-responses-to-bidder.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bid1_token),
                {"data": {"requirementResponses": requirementResponses}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "activate-bidder-without-proposal.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bid1_token),
                {"data": {"status": "pending"}},
                status=422,
            )

        with open(TARGET_DIR + "upload-bid-proposal.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid1_id, bid1_token),
                {
                    "data": {
                        "title": "Proposal.p7s",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "sign/p7s",
                        "documentType": "proposal",
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + "activate-bidder.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bid1_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "bidder-documents.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid1_id, bid1_token)
            )
            self.assertEqual(response.status, "200 OK")

        tenderers = deepcopy(test_docs_bid_draft["tenderers"])
        tenderers[0]["name"] = "Школяр"
        with open(TARGET_DIR + "patch-pending-bid.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bid1_token),
                {"data": {"tenderers": tenderers}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "activate-bidder-without-sign.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bid1_token),
                {"data": {"status": "pending"}},
                status=422,
            )

        self.tick_delta = None
        self.tick(timedelta(minutes=1))
        self.add_sign_doc(
            self.tender_id,
            bid1_token,
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
            doc_id=doc_id,
        )
        self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bid1_token),
            {"data": {"status": "pending"}},
        )

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"value": {"amount": 501.0}}}
        )
        self.assertEqual(response.status, "200 OK")

        #### Registering bid 2
        with open(TARGET_DIR + "bid-lot2.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                f"/tenders/{tender_id}/bids",
                {
                    "data": {
                        "selfQualified": True,
                        "status": "draft",
                        "tenderers": test_docs_bid2["tenderers"],
                        "lotValues": [
                            {"value": {"amount": 500}, "relatedLot": lot_id1},
                            {
                                "subcontractingDetails": "ДКП «Укр Прінт», Україна",
                                "value": {"amount": 500},
                                "relatedLot": lot_id2,
                            },
                        ],
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            bid2_id = response.json["data"]["id"]
            bid2_token = response.json["access"]["token"]
        doc2_id = self.add_sign_doc(
            self.tender_id,
            bid2_token,
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        ).json["data"]["id"]
        self.set_responses(tender_id, response.json, "pending")

        lot_values = response.json["data"]["lotValues"]

        #### Bids invalidation
        with open(TARGET_DIR + "tender-invalid-all-bids.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                f"/tenders/{tender_id}/lots/{lot_id2}?acc_token={owner_token}",
                {"data": {"value": {**lot2["value"], "amount": 400}}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "bid-lot1-invalid-view.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid1_id, bid1_token))
            self.assertEqual(response.status, "200 OK")

        #### Bids confirmation
        self.tick(timedelta(minutes=1))
        self.add_sign_doc(
            self.tender_id,
            bid1_token,
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
            doc_id=doc_id,
        )

        lot_values[0].update(
            {
                "subcontractingDetails": "ДКП «Орфей»",
                "value": {"amount": 500},
                "relatedLot": lot_id1,
            }
        )
        with open(TARGET_DIR + "bid-lot1-update-view.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid1_id, bid1_token),
                {
                    "data": {
                        "lotValues": [lot_values[0]],
                        "status": "pending",
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")

        self.tick(timedelta(minutes=1))
        self.add_sign_doc(
            self.tender_id,
            bid2_token,
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
            doc_id=doc2_id,
        )
        lot_values[0].update({"value": {"amount": 500}, "relatedLot": lot_id1})
        lot_values[1].update({"relatedLot": lot_id2})
        with open(TARGET_DIR + "bid-lot2-update-view.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                f"/tenders/{tender_id}/bids/{bid2_id}?acc_token={bid2_token}",
                {
                    "data": {
                        "lotValues": lot_values,
                        "status": "pending",
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")

        #### Auction
        self.set_status("active.auction")
        self.app.authorization = ("Basic", ("auction", ""))
        auction1_url = "{}/tenders/{}_{}".format(self.auctions_url, self.tender_id, lot_id1)
        patch_data = {
            "lots": [
                {
                    "id": lot_id1,
                    "auctionUrl": auction1_url,
                },
                {
                    "id": lot_id2,
                },
            ],
            "bids": [
                {"id": bid1_id, "lotValues": [{"participationUrl": "{}?key_for_bid={}".format(auction1_url, bid1_id)}]},
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": "{}?key_for_bid={}".format(auction1_url, bid2_id)},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            "/tenders/{}/auction/{}?acc_token={}".format(self.tender_id, lot_id1, owner_token), {"data": patch_data}
        )
        self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        with open(TARGET_DIR + "auction-url.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "bidder-participation-url.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bid1_token))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "bidder2-participation-url.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid2_id, bid2_token))
            self.assertEqual(response.status, "200 OK")

        #### Confirming qualification
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        auction_bids_data[0]["lotValues"][0]["value"]["amount"] = 250  # too low price

        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(self.tender_id, lot_id1),
            {
                "data": {
                    "bids": [
                        {
                            "id": bid["id"],
                            "lotValues": [
                                {"value": lot_value["value"], "relatedLot": lot_value["relatedLot"]}
                                for lot_value in bid["lotValues"]
                            ],
                        }
                        for bid in auction_bids_data
                    ]
                }
            },
        )

        self.app.authorization = ("Basic", ("broker", ""))

        # get pending award
        with open(TARGET_DIR + "get-awards-list.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, owner_token))

        award = response.json["data"][0]
        award_id = award["id"]
        award_bid_id = award["bid_id"]
        self.assertEqual(len(award.get("milestones", "")), 1)

        with open(TARGET_DIR + "fail-disqualification.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
                status=403,
            )

        with open(TARGET_DIR + "post-evidence-document.http", "w") as self.app.file_obj:
            self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, award_bid_id, bid1_token),
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

        with open(TARGET_DIR + "unsuccessful-qualified-award.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}},
                status=422,
            )

        with open(TARGET_DIR + "activate-non-qualified-award.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": False, "eligible": True}},
                status=422,
            )

        with open(TARGET_DIR + "award-notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=422,
            )
        with open(TARGET_DIR + "award-unsuccessful-notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
                status=422,
            )
        with open(TARGET_DIR + "award-add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")

        with open(TARGET_DIR + "confirm-qualification.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=200,
            )

        #### Preparing the cancellation request

        with open(TARGET_DIR + "prepare-cancellation.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"reason": "cancellation reason", "reasonType": "unFixable"}},
            )
            self.assertEqual(response.status, "201 Created")

        cancellation_id = response.json["data"]["id"]

        with open(TARGET_DIR + "update-cancellation-reasonType.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"reasonType": "forceMajeure"}},
            )
            self.assertEqual(response.status, "200 OK")

        #### Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + "upload-cancellation-doc.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
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
            cancellation_doc_id = response.json["data"]["id"]
            self.assertEqual(response.status, "201 Created")

        with open(TARGET_DIR + "patch-cancellation.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}/documents/{}?acc_token={}".format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {"data": {"description": "Changed description"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "update-cancellation-doc.http", "w") as self.app.file_obj:
            response = self.app.put_json(
                "/tenders/{}/cancellations/{}/documents/{}?acc_token={}".format(
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
            self.assertEqual(response.status, "200 OK")

        #### Activating the request and cancelling tender
        with open(TARGET_DIR + "pending-cancellation.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        self.tick(delta=timedelta(days=11))
        self.check_chronograph()

        with open(TARGET_DIR + "active-cancellation.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token)
            )
            self.assertEqual(response.status, "200 OK")
