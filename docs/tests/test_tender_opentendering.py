import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import calculate_date, get_now
from openprocurement.tender.core.tests.criteria_utils import generate_responses
from openprocurement.tender.core.tests.utils import (
    set_bid_items,
    set_bid_lotvalues,
    set_tender_criteria,
)
from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_lots
from openprocurement.tender.open.tests.open_tendering.eu.base import (
    BaseTenderWebTest as BaseTenderOpenTenderingEUWebTest,
)
from openprocurement.tender.open.tests.open_tendering.eu.base import (
    test_tender_open_tendering_eu_criteria,
)
from openprocurement.tender.open.tests.open_tendering.ua.base import (
    BaseTenderOpenTenderingUAWebTest,
    test_tender_open_tendering_ua_criteria,
)
from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import (
    test_docs_bid2,
    test_docs_bid3_with_docs,
    test_docs_bid_draft,
    test_docs_lots,
    test_docs_question,
    test_docs_subcontracting,
    test_docs_tender_openeu,
    test_docs_tender_openua,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

# openTendering: the UA/EU variant is set by procurementAspects
test_tender_ua_data = deepcopy(test_docs_tender_openua)
test_tender_ua_data["procurementMethodType"] = "openTendering"
test_tender_ua_data["procurementAspects"] = ["UA"]

test_tender_eu_data = deepcopy(test_docs_tender_openeu)
test_tender_eu_data["procurementMethodType"] = "openTendering"
test_tender_eu_data["procurementAspects"] = ["EU"]

test_lots = deepcopy(test_docs_lots)
test_lots[0]["value"] = test_tender_eu_data["value"]
test_lots[0]["minimalStep"] = {"amount": 5, "currency": "UAH"}

bid = deepcopy(test_docs_bid_draft)
bid2 = deepcopy(test_docs_bid2)
bid3 = deepcopy(test_docs_bid3_with_docs)

bid.update(test_docs_subcontracting)

BASE_DIR = "docs/source/tendering/open/"
UA_TARGET_DIR = BASE_DIR + "http/opentendering-ua/"
UA_TARGET_CSV_DIR = BASE_DIR + "csv/opentendering-ua/"
EU_TARGET_DIR = BASE_DIR + "http/opentendering-eu/"
EU_TARGET_CSV_DIR = BASE_DIR + "csv/opentendering-eu/"


class TenderOpenTenderingUAResourceTest(BaseTenderOpenTenderingUAWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_ua_data
    initial_lots = test_tender_below_lots
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        self.setUpMock()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.tearDownMock()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="openTendering.UA",
            file_path=UA_TARGET_CSV_DIR + "config.csv",
        )

    def test_docs_allowed_kind_csv(self):
        self.write_allowed_kind_csv(
            pmt="openTendering",
            file_path=UA_TARGET_CSV_DIR + "kind.csv",
        )

    def test_docs(self):
        request_path = "/tenders?opt_pretty=1"

        self.app.authorization = ("Basic", ("broker", ""))

        #### Creating tender

        # the procurement aspects are required
        data = deepcopy(test_tender_ua_data)
        del data["procurementAspects"]
        with open(UA_TARGET_DIR + "tender-post-without-procurement-aspects.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1", {"data": data, "config": self.initial_config}, status=422
            )

        # only one of the allowed combinations of the procurement aspects
        data["procurementAspects"] = ["UA", "EU"]
        with open(UA_TARGET_DIR + "tender-post-invalid-procurement-aspects.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1", {"data": data, "config": self.initial_config}, status=422
            )

        # the config values are pinned by the variant
        config = deepcopy(self.initial_config)
        config["minTenderingDuration"] = 30
        with open(UA_TARGET_DIR + "tender-post-invalid-config.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1", {"data": test_tender_ua_data, "config": config}, status=422
            )

        with open(UA_TARGET_DIR + "tender-post-attempt-json-data.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1", {"data": test_tender_ua_data, "config": self.initial_config}
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        owner_token = response.json["access"]["token"]
        self.tender_id = tender["id"]

        with open(UA_TARGET_DIR + "blank-tender-view.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}".format(tender["id"]))
            self.assertEqual(response.status, "200 OK")

        # the procurement aspects can't be changed
        with open(UA_TARGET_DIR + "patch-procurement-aspects.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"procurementAspects": ["EU"]}},
                status=422,
            )

        with open(UA_TARGET_DIR + "tender-listing-no-auth.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        # add lots
        with open(UA_TARGET_DIR + "tender-add-lot.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/lots?acc_token={}".format(self.tender_id, owner_token), {"data": self.initial_lots[0]}
            )
            self.assertEqual(response.status, "201 Created")
            lot_id = response.json["data"]["id"]

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        with open(UA_TARGET_DIR + "tender-add-relatedLot-to-item.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, "200 OK")

        # Tender activating
        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]

        test_criteria_data = deepcopy(test_tender_open_tendering_ua_criteria)
        set_tender_criteria(test_criteria_data, tender["lots"], tender["items"])

        with open(UA_TARGET_DIR + "add-exclusion-criteria.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(tender["id"], owner_token), {"data": test_criteria_data}
            )
            self.assertEqual(response.status, "201 Created")

        with open(UA_TARGET_DIR + "contract-template-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
                {"data": {"status": "active.tendering"}},
                status=422,
            )

        with open(UA_TARGET_DIR + "add-contract-proforma-document.http", "w") as self.app.file_obj:
            self.add_contract_proforma_doc(tender["id"], owner_token)

        with open(UA_TARGET_DIR + "notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
                {"data": {"status": "active.tendering"}},
                status=422,
            )

        with open(UA_TARGET_DIR + "add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(tender["id"], owner_token)

        with open(UA_TARGET_DIR + "tender-activating.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "active-tender-listing-no-auth.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path + "&opt_fields=procurementAspects")
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        #### Modifying tender

        tender_period_end_date = calculate_date(get_now(), timedelta(days=16))
        with open(UA_TARGET_DIR + "patch-items-value-periods.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
                {
                    "data": {
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        }
                    }
                },
            )

        with open(UA_TARGET_DIR + "tender-listing-after-patch.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))
        self.tender_id = tender["id"]

        # Setting Bid guarantee

        with open(UA_TARGET_DIR + "set-bid-guarantee.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"guarantee": {"amount": 8, "currency": "USD"}}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("guarantee", response.json["data"])

        #### Uploading documentation

        with open(UA_TARGET_DIR + "upload-tender-notice.http", "w") as self.app.file_obj:
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
        with open(UA_TARGET_DIR + "tender-documents.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "upload-award-criteria.http", "w") as self.app.file_obj:
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

        with open(UA_TARGET_DIR + "tender-documents-2.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents?acc_token={}".format(self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "update-award-criteria.http", "w") as self.app.file_obj:
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

        with open(UA_TARGET_DIR + "tender-documents-3.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        #### Enquiries

        with open(UA_TARGET_DIR + "ask-question.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/questions".format(self.tender_id), {"data": test_docs_question}, status=201
            )
            question_id = response.json["data"]["id"]
            self.assertEqual(response.status, "201 Created")

        with open(UA_TARGET_DIR + "answer-question.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question_id, owner_token),
                {"data": {"answer": 'Таблицю додано в файлі "Kalorijnist.xslx"'}},
                status=200,
            )
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "list-question.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/questions".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "get-answer.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/questions/{}".format(self.tender_id, question_id))
            self.assertEqual(response.status, "200 OK")

        self.set_enquiry_period_end()
        self.app.authorization = ("Basic", ("broker", ""))

        with open(UA_TARGET_DIR + "update-tender-after-enqiery.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
                {"data": {"value": {"amount": 501.0}}},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")

        with open(UA_TARGET_DIR + "ask-question-after-enquiry-period.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/questions".format(self.tender_id), {"data": test_docs_question}, status=403
            )
            self.assertEqual(response.status, "403 Forbidden")

        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]
        with open(UA_TARGET_DIR + "update-tender-after-enqiery-with-update-periods.http", "w") as self.app.file_obj:
            tender_period_end_date = calculate_date(get_now(), timedelta(days=5))
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

        bids_access = {}
        bid_data = deepcopy(bid)
        set_bid_lotvalues(bid_data, self.initial_lots)
        set_bid_items(self, bid_data, tender["items"])
        with open(UA_TARGET_DIR + "register-bidder.http", "w") as self.app.file_obj:
            response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
            bid1_id = response.json["data"]["id"]
            bids_access[bid1_id] = response.json["access"]["token"]
            self.assertEqual(response.status, "201 Created")

        requirementResponses = generate_responses(self)
        with open(UA_TARGET_DIR + "add-requirement-responses-to-bidder.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"requirementResponses": requirementResponses}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "activate-bidder-without-proposal.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
                status=422,
            )

        with open(UA_TARGET_DIR + "upload-bid-proposal.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
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

        with open(UA_TARGET_DIR + "activate-bidder.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "bidder-documents.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        tenderers = deepcopy(test_docs_bid_draft["tenderers"])
        tenderers[0]["name"] = "Школяр"
        with open(UA_TARGET_DIR + "patch-pending-bid.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"tenderers": tenderers}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "activate-bidder-without-sign.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
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
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
            {"data": {"status": "pending"}},
        )

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"value": {"amount": 501.0}}}
        )
        self.assertEqual(response.status, "200 OK")

        #### Bid invalidation

        with open(UA_TARGET_DIR + "bidder-after-changing-tender.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        #### Bid confirmation

        self.tick()
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid1_id],
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
            doc_id=doc_id,
        )
        with open(UA_TARGET_DIR + "bidder-activate-after-changing-tender.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        bid2_data = deepcopy(bid2)
        bid2_data["status"] = "draft"
        set_bid_lotvalues(bid2_data, self.initial_lots)
        set_bid_items(self, bid2_data, tender["items"])
        with open(UA_TARGET_DIR + "register-2nd-bidder.http", "w") as self.app.file_obj:
            response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid2_data})
            bid2_id = response.json["data"]["id"]
            bids_access[bid2_id] = response.json["access"]["token"]
            self.assertEqual(response.status, "201 Created")

        self.add_sign_doc(
            self.tender_id,
            bids_access[bid2_id],
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json)

        #### Auction
        self.set_status("active.auction")
        self.app.authorization = ("Basic", ("auction", ""))
        auction_url = "{}/tenders/{}_{}".format(self.auctions_url, self.tender_id, lot_id)
        patch_data = {
            "lots": [
                {
                    "id": lot_id,
                    "auctionUrl": auction_url,
                },
            ],
            "bids": [
                {"id": bid1_id, "lotValues": [{"participationUrl": "{}?key_for_bid={}".format(auction_url, bid1_id)}]},
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": "{}?key_for_bid={}".format(auction_url, bid2_id)},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            "/tenders/{}/auction/{}?acc_token={}".format(self.tender_id, lot_id, owner_token), {"data": patch_data}
        )
        self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        with open(UA_TARGET_DIR + "auction-url.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "bidder-participation-url.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "bidder2-participation-url.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid2_id, bids_access[bid2_id])
            )
            self.assertEqual(response.status, "200 OK")

        #### Confirming qualification
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        auction_bids_data[0]["lotValues"][0]["value"]["amount"] = 250  # too low price

        self.app.post_json(
            "/tenders/{}/auction/{}".format(self.tender_id, lot_id),
            {
                "data": {
                    "bids": [
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
        self.app.authorization = ("Basic", ("broker", ""))

        # get pending award
        with open(UA_TARGET_DIR + "get-awards-list.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, owner_token))

        award = response.json["data"][0]
        award_id = award["id"]
        award_bid_id = award["bid_id"]
        self.assertEqual(len(award.get("milestones", "")), 1)

        with open(UA_TARGET_DIR + "fail-disqualification.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {
                    "data": {
                        "status": "unsuccessful",
                        "qualified": False,
                        "eligible": False,
                    }
                },
                status=403,
            )

        with open(UA_TARGET_DIR + "post-evidence-document.http", "w") as self.app.file_obj:
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

        with open(UA_TARGET_DIR + "unsuccessful-qualified-award.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}},
                status=422,
            )

        with open(UA_TARGET_DIR + "activate-non-qualified-award.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": False, "eligible": True}},
                status=422,
            )

        with open(UA_TARGET_DIR + "award-notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=422,
            )
        with open(UA_TARGET_DIR + "award-unsuccessful-notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful"}},
                status=422,
            )
        with open(UA_TARGET_DIR + "award-add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")

        with open(UA_TARGET_DIR + "confirm-qualification.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=200,
            )

        #### Preparing the cancellation request

        with open(UA_TARGET_DIR + "prepare-cancellation.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"reason": "cancellation reason", "reasonType": "unFixable"}},
            )
            self.assertEqual(response.status, "201 Created")

        cancellation_id = response.json["data"]["id"]

        with open(UA_TARGET_DIR + "update-cancellation-reasonType.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"reasonType": "forceMajeure"}},
            )
            self.assertEqual(response.status, "200 OK")

        #### Filling cancellation with protocol and supplementary documentation

        with open(UA_TARGET_DIR + "upload-cancellation-doc.http", "w") as self.app.file_obj:
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

        with open(UA_TARGET_DIR + "patch-cancellation.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}/documents/{}?acc_token={}".format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {"data": {"description": "Changed description"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(UA_TARGET_DIR + "update-cancellation-doc.http", "w") as self.app.file_obj:
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

        with open(UA_TARGET_DIR + "cancellation-sign-doc-is-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
                status=422,
            )

        with open(UA_TARGET_DIR + "upload-cancellation-report-doc.http", "w") as self.app.file_obj:
            self.add_sign_doc(
                self.tender_id,
                owner_token,
                docs_url=f"/cancellations/{cancellation_id}/documents",
                document_type="cancellationReport",
            )

        #### Activating the request and cancelling tender
        with open(UA_TARGET_DIR + "pending-cancellation.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        self.tick(delta=timedelta(days=11))
        self.check_chronograph()

        with open(UA_TARGET_DIR + "active-cancellation.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token)
            )
            self.assertEqual(response.status, "200 OK")

    def test_docs_one_bid(self):
        """openTendering: a single bid is enough, the tender proceeds to the qualification without an auction"""
        self.app.authorization = ("Basic", ("broker", ""))

        response = self.app.post_json("/tenders", {"data": test_tender_ua_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        tender = response.json["data"]
        owner_token = response.json["access"]["token"]
        self.tender_id = tender["id"]

        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, owner_token), {"data": self.initial_lots[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lot_id = response.json["data"]["id"]
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, "200 OK")
        tender = response.json["data"]

        test_criteria_data = deepcopy(test_tender_open_tendering_ua_criteria)
        set_tender_criteria(test_criteria_data, tender["lots"], tender["items"])
        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, owner_token), {"data": test_criteria_data}
        )
        self.assertEqual(response.status, "201 Created")
        self.add_contract_proforma_doc(self.tender_id, owner_token)
        self.add_sign_doc(self.tender_id, owner_token)
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"status": "active.tendering"}}
        )
        self.assertEqual(response.status, "200 OK")

        bid_data = deepcopy(bid)
        set_bid_lotvalues(bid_data, self.initial_lots)
        set_bid_items(self, bid_data, tender["items"])
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
        self.assertEqual(response.status, "201 Created")
        bid1_id = response.json["data"]["id"]
        bid1_token = response.json["access"]["token"]
        self.add_sign_doc(self.tender_id, bid1_token, docs_url=f"/bids/{bid1_id}/documents", document_type="proposal")
        self.set_responses(self.tender_id, response.json)

        # the tender period ends with a single bid: no auction, the award is created
        self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
        with open(UA_TARGET_DIR + "one-bid-switch-to-qualification.http", "w") as self.app.file_obj:
            response = self.check_chronograph()
            self.assertEqual(response.json["data"]["status"], "active.qualification")

        with open(UA_TARGET_DIR + "one-bid-awards-list.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(len(response.json["data"]), 1)
            self.assertEqual(response.json["data"][0]["bid_id"], bid1_id)
            self.assertEqual(response.json["data"][0]["status"], "pending")


class TenderOpenTenderingEUResourceTest(BaseTenderOpenTenderingEUWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_eu_data
    initial_lots = deepcopy(test_lots[:1])
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        self.setUpMock()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.tearDownMock()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="openTendering.EU",
            file_path=EU_TARGET_CSV_DIR + "config.csv",
        )

    def test_docs_allowed_kind_csv(self):
        self.write_allowed_kind_csv(
            pmt="openTendering",
            file_path=EU_TARGET_CSV_DIR + "kind.csv",
        )

    def test_docs(self):
        request_path = "/tenders?opt_pretty=1"

        self.app.authorization = ("Basic", ("broker", ""))

        #### Creating tender

        # the config values are pinned by the variant
        config = deepcopy(self.initial_config)
        config["hasPrequalification"] = False
        with open(EU_TARGET_DIR + "tender-post-invalid-config.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1", {"data": test_tender_eu_data, "config": config}, status=422
            )

        # the announcement is published in English as well
        data = deepcopy(test_tender_eu_data)
        data["procuringEntity"] = deepcopy(data["procuringEntity"])
        del data["procuringEntity"]["name_en"]
        with open(EU_TARGET_DIR + "tender-post-without-english-fields.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1", {"data": data, "config": self.initial_config}, status=422
            )

        with open(EU_TARGET_DIR + "tender-post-attempt-json-data.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1", {"data": test_tender_eu_data, "config": self.initial_config}
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        owner_token = response.json["access"]["token"]
        self.tender_id = tender["id"]

        with open(EU_TARGET_DIR + "blank-tender-view.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}".format(tender["id"]))
            self.assertEqual(response.status, "200 OK")

        # the procurement aspects can't be changed
        with open(EU_TARGET_DIR + "patch-procurement-aspects.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"procurementAspects": ["UA"]}},
                status=422,
            )

        with open(EU_TARGET_DIR + "tender-listing-no-auth.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        # add lots
        with open(EU_TARGET_DIR + "tender-add-lot.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/lots?acc_token={}".format(self.tender_id, owner_token), {"data": self.initial_lots[0]}
            )
            self.assertEqual(response.status, "201 Created")
            lot_id = response.json["data"]["id"]

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        items[1]["relatedLot"] = lot_id
        with open(EU_TARGET_DIR + "tender-add-relatedLot-to-item.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, "200 OK")

        # add criteria
        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]

        test_criteria_data = deepcopy(test_tender_open_tendering_eu_criteria)
        set_tender_criteria(test_criteria_data, tender["lots"], tender["items"])

        with open(EU_TARGET_DIR + "add-exclusion-criteria.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(tender["id"], owner_token), {"data": test_criteria_data}
            )
            self.assertEqual(response.status, "201 Created")

        # Tender activating
        with open(EU_TARGET_DIR + "add-contract-proforma-document.http", "w") as self.app.file_obj:
            self.add_contract_proforma_doc(tender["id"], owner_token)

        with open(EU_TARGET_DIR + "notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
                {"data": {"status": "active.tendering"}},
                status=422,
            )

        with open(EU_TARGET_DIR + "add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(tender["id"], owner_token)

        with open(EU_TARGET_DIR + "tender-activating.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "active-tender-listing-no-auth.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path + "&opt_fields=procurementAspects")
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        #### Modifying tender

        tender_period_end_date = calculate_date(get_now(), timedelta(days=31))
        with open(EU_TARGET_DIR + "patch-items-value-periods.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
                {
                    "data": {
                        "tenderPeriod": {
                            "startDate": tender["tenderPeriod"]["startDate"],
                            "endDate": tender_period_end_date.isoformat(),
                        }
                    }
                },
            )

        with open(EU_TARGET_DIR + "tender-listing-after-patch.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))
        self.tender_id = tender["id"]

        # Setting Bid guarantee

        with open(EU_TARGET_DIR + "set-bid-guarantee.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"guarantee": {"amount": 8, "currency": "USD"}}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("guarantee", response.json["data"])

        #### Uploading documentation

        with open(EU_TARGET_DIR + "upload-tender-notice.http", "w") as self.app.file_obj:
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
        with open(EU_TARGET_DIR + "tender-documents.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "upload-award-criteria.http", "w") as self.app.file_obj:
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

        with open(EU_TARGET_DIR + "tender-documents-2.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents?acc_token={}".format(self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "update-award-criteria.http", "w") as self.app.file_obj:
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

        with open(EU_TARGET_DIR + "tender-documents-3.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/documents".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        #### Enquiries

        with open(EU_TARGET_DIR + "ask-question.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/questions".format(self.tender_id), {"data": test_docs_question}, status=201
            )
            question_id = response.json["data"]["id"]
            self.assertEqual(response.status, "201 Created")

        with open(EU_TARGET_DIR + "answer-question.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question_id, owner_token),
                {"data": {"answer": 'Таблицю додано в файлі "Kalorijnist.xslx"'}},
                status=200,
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "list-question.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/questions".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "get-answer.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/questions/{}".format(self.tender_id, question_id))
            self.assertEqual(response.status, "200 OK")

        self.set_enquiry_period_end()
        self.app.authorization = ("Basic", ("broker", ""))

        with open(EU_TARGET_DIR + "update-tender-after-enqiery.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
                {"data": {"value": {"amount": 501.0}}},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")

        with open(EU_TARGET_DIR + "ask-question-after-enquiry-period.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/questions".format(self.tender_id), {"data": test_docs_question}, status=403
            )
            self.assertEqual(response.status, "403 Forbidden")

        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]

        with open(EU_TARGET_DIR + "update-tender-after-enqiery-with-update-periods.http", "w") as self.app.file_obj:
            tender_period_end_date = calculate_date(get_now(), timedelta(days=8))
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

        bids_access = {}
        bid_data = deepcopy(bid)
        set_bid_lotvalues(bid_data, self.initial_lots)
        set_bid_items(self, bid_data, tender["items"])
        with open(EU_TARGET_DIR + "register-bidder.http", "w") as self.app.file_obj:
            response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
            bid1_id = response.json["data"]["id"]
            bids_access[bid1_id] = response.json["access"]["token"]
            self.assertEqual(response.status, "201 Created")

        requirementResponses = generate_responses(self)
        with open(EU_TARGET_DIR + "add-requirement-responses-to-bidder.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"requirementResponses": requirementResponses}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "activate-bidder-without-proposal.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
                status=422,
            )

        with open(EU_TARGET_DIR + "upload-bid-proposal.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
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

        with open(EU_TARGET_DIR + "activate-bidder.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        tenderers = deepcopy(test_docs_bid_draft["tenderers"])
        tenderers[0]["name"] = "Школяр"
        with open(EU_TARGET_DIR + "patch-pending-bid.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"tenderers": tenderers}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "activate-bidder-without-sign.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
                status=422,
            )

        # Confidentiality

        with open(EU_TARGET_DIR + "upload-bid-private-proposal.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {
                    "data": {
                        "title": "Proposal_top_secrets.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            priv_doc_id = response.json["data"]["id"]

        # set confidentiality properties
        with open(EU_TARGET_DIR + "mark-bid-doc-private.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
                    self.tender_id, bid1_id, priv_doc_id, bids_access[bid1_id]
                ),
                {
                    "data": {
                        "confidentiality": "buyerOnly",
                        "confidentialityRationale": "Only our company sells badgers with pink hair.",
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "bidder-documents.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "upload-bid-financial-document-proposal.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/financial_documents?acc_token={}".format(
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
            self.assertEqual(response.status, "201 Created")

        response = self.app.post_json(
            "/tenders/{}/bids/{}/financial_documents?acc_token={}".format(
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
        self.assertEqual(response.status, "201 Created")

        with open(EU_TARGET_DIR + "bidder-financial-documents.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}/financial_documents?acc_token={}".format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                )
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "upload-bid-eligibility-document-proposal.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/eligibility_documents?acc_token={}".format(
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
            self.assertEqual(response.status, "201 Created")

        with open(EU_TARGET_DIR + "upload-bid-qualification-document-proposal.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/qualification_documents?acc_token={}".format(
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
            self.assertEqual(response.status, "201 Created")

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
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
            {"data": {"status": "pending"}},
        )

        with open(EU_TARGET_DIR + "bidder-view-financial-documents.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"value": {"amount": 501.0}}}
        )
        self.assertEqual(response.status, "200 OK")

        #### Bid invalidation

        with open(EU_TARGET_DIR + "bidder-after-changing-tender.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        #### Bid confirmation

        self.tick(timedelta(minutes=1))
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid1_id],
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
            doc_id=doc_id,
        )
        with open(EU_TARGET_DIR + "bidder-activate-after-changing-tender.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "register-2nd-bidder.http", "w") as self.app.file_obj:
            bid2_draft = deepcopy(bid2)
            bid2_draft["status"] = "draft"
            set_bid_lotvalues(bid2_draft, self.initial_lots)
            set_bid_items(self, bid2_draft, tender["items"])
            response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid2_draft})
            bid2_id = response.json["data"]["id"]
            bids_access[bid2_id] = response.json["access"]["token"]
            self.assertEqual(response.status, "201 Created")
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid2_id],
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, "pending")

        for document in bid3["documents"]:
            document["url"] = self.generate_docservice_url()
        for document in bid3["eligibilityDocuments"]:
            document["url"] = self.generate_docservice_url()
        for document in bid3["financialDocuments"]:
            document["url"] = self.generate_docservice_url()
        for document in bid3["qualificationDocuments"]:
            document["url"] = self.generate_docservice_url()

        with open(EU_TARGET_DIR + "register-3rd-bidder.http", "w") as self.app.file_obj:
            bid3_draft = deepcopy(bid3)
            bid3_draft["status"] = "draft"
            set_bid_lotvalues(bid3_draft, self.initial_lots)
            set_bid_items(self, bid3_draft, tender["items"])
            response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid3_draft})
            bid3_id = response.json["data"]["id"]
            bids_access[bid3_id] = response.json["access"]["token"]
            self.assertEqual(response.status, "201 Created")
        self.add_sign_doc(
            self.tender_id,
            bids_access[bid3_id],
            docs_url=f"/bids/{bid3_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, "pending")

        # Pre-qualification

        self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
        self.check_chronograph()

        with open(EU_TARGET_DIR + "qualifications-listing.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")
            qualifications = response.json["data"]["qualifications"]
            self.assertEqual(len(qualifications), 3)
            self.assertEqual(qualifications[0]["bidID"], bid1_id)
            self.assertEqual(qualifications[1]["bidID"], bid2_id)
            self.assertEqual(qualifications[2]["bidID"], bid3_id)

        with open(EU_TARGET_DIR + "approve-qualification1.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualifications[0]["id"], owner_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
        with open(EU_TARGET_DIR + "approve-qualification2.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualifications[1]["id"], owner_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "reject-qualification3.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualifications[2]["id"], owner_token
                ),
                {"data": {"status": "unsuccessful"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "qualificated-bids-view.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/bids?acc_token={}".format(self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "rejected-bid-view.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid3_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still
        with open(EU_TARGET_DIR + "pre-qualification-sign-doc-is-required.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"status": "active.pre-qualification.stand-still"}},
                status=422,
            )
        with open(EU_TARGET_DIR + "upload-evaluation-reports-doc.http", "w") as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, document_type="evaluationReports")
        with open(EU_TARGET_DIR + "pre-qualification-confirmation.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"status": "active.pre-qualification.stand-still"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        #### Auction

        self.set_status("active.auction")
        self.app.authorization = ("Basic", ("auction", ""))
        auction_url = "{}/tenders/{}_{}".format(self.auctions_url, self.tender_id, lot_id)
        patch_data = {
            "lots": [
                {
                    "id": lot_id,
                    "auctionUrl": auction_url,
                },
            ],
            "bids": [
                {"id": bid1_id, "lotValues": [{"participationUrl": "{}?key_for_bid={}".format(auction_url, bid1_id)}]},
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": "{}?key_for_bid={}".format(auction_url, bid2_id)},
                    ],
                },
                {
                    "id": bid3_id,
                },
            ],
        }
        response = self.app.patch_json(
            "/tenders/{}/auction/{}?acc_token={}".format(self.tender_id, lot_id, owner_token), {"data": patch_data}
        )
        self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        with open(EU_TARGET_DIR + "auction-url.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "bidder-participation-url.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "bidder2-participation-url.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid2_id, bids_access[bid2_id])
            )
            self.assertEqual(response.status, "200 OK")

        #### Confirming qualification
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        self.app.post_json(
            "/tenders/{}/auction/{}".format(self.tender_id, lot_id),
            {
                "data": {
                    "bids": [
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

        self.app.authorization = ("Basic", ("broker", ""))

        with open(EU_TARGET_DIR + "get-awards-list.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, owner_token))
        # get pending award
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

        with open(EU_TARGET_DIR + "unsuccessful-qualified-award.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}},
                status=422,
            )

        with open(EU_TARGET_DIR + "activate-non-qualified-award.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": False, "eligible": True}},
                status=422,
            )

        with open(EU_TARGET_DIR + "award-notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=422,
            )
        with open(EU_TARGET_DIR + "award-unsuccessful-notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful"}},
                status=422,
            )
        with open(EU_TARGET_DIR + "award-add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")

        with open(EU_TARGET_DIR + "confirm-qualification.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        #### Preparing the cancellation request

        with open(EU_TARGET_DIR + "prepare-cancellation.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"reason": "cancellation reason", "reasonType": "noDemand"}},
            )
            self.assertEqual(response.status, "201 Created")

        cancellation_id = response.json["data"]["id"]

        with open(EU_TARGET_DIR + "update-cancellation-reasonType.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"reasonType": "unFixable"}},
            )
            self.assertEqual(response.status, "200 OK")

        #### Filling cancellation with protocol and supplementary documentation

        with open(EU_TARGET_DIR + "upload-cancellation-doc.http", "w") as self.app.file_obj:
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

        with open(EU_TARGET_DIR + "patch-cancellation.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}/documents/{}?acc_token={}".format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token
                ),
                {"data": {"description": "Changed description"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(EU_TARGET_DIR + "update-cancellation-doc.http", "w") as self.app.file_obj:
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

        with open(EU_TARGET_DIR + "cancellation-sign-doc-is-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
                status=422,
            )

        with open(EU_TARGET_DIR + "upload-cancellation-report-doc.http", "w") as self.app.file_obj:
            self.add_sign_doc(
                self.tender_id,
                owner_token,
                docs_url=f"/cancellations/{cancellation_id}/documents",
                document_type="cancellationReport",
            )

        #### Activating the request and cancelling tender
        with open(EU_TARGET_DIR + "pending-cancellation.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        self.tick(delta=timedelta(days=11))
        self.check_chronograph()

        with open(EU_TARGET_DIR + "active-cancellation.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token)
            )
            self.assertEqual(response.status, "200 OK")
