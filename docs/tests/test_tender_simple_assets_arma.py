import os
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from openprocurement.api.utils import calculate_date, get_now
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.arma.tests.base import (
    test_framework_arma_config,
    test_framework_arma_data,
)
from openprocurement.framework.core.tests.base import FrameworkActionsTestMixin
from openprocurement.tender.arma.tests.simple_asset.base import BaseTenderSimpleAssetWebTest
from openprocurement.tender.core.tests.utils import set_bid_items, set_bid_lotvalues
from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import (
    test_docs_bid2,
    test_docs_bid3_with_docs,
    test_docs_bid_draft,
    test_docs_lots,
    test_docs_subcontracting,
    test_docs_tender_simple_assets_arma,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

test_tender_data = deepcopy(test_docs_tender_simple_assets_arma)
test_lots = deepcopy(test_docs_lots)
bid = deepcopy(test_docs_bid_draft)
bid2 = deepcopy(test_docs_bid2)
bid3 = deepcopy(test_docs_bid3_with_docs)

bid.update(test_docs_subcontracting)

# clear eContract fields
for b in [bid, bid2, bid3]:
    for x in b["tenderers"]:
        x.pop("signerInfo", None)
    b["value"].pop("amount", None)
    b["value"]["amountPercentage"] = 50

test_lots[0]["value"] = {"amountPercentage": 50}
test_lots[0]["minimalStep"] = {"amountPercentage": 1}
test_lots[0]["minExpectedIncome"] = {"amount": 100000.00, "currency": "UAH", "valueAddedTaxIncluded": True}

test_framework_data = deepcopy(test_framework_arma_data)
test_framework_data["procuringEntity"]["identifier"] = deepcopy(test_tender_data["procuringEntity"]["identifier"])

BASE_DIR = "docs/source/tendering/arma/"
TARGET_DIR = BASE_DIR + "simpleAsset/http/tutorial/"
TARGET_CSV_DIR = BASE_DIR + "simpleAsset/csv/"


class TenderResourceTest(
    BaseTenderSimpleAssetWebTest,
    MockWebTestMixin,
    FrameworkActionsTestMixin,
    TenderConfigCSVMixin,
):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL
    framework_type = ARMA_TYPE

    def setUp(self):
        self.setUpMock()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.tearDownMock()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="simpleAsset.arma",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def test_docs_allowed_kind_csv(self):
        self.write_allowed_kind_csv(
            pmt="simpleAsset.arma",
            file_path=TARGET_CSV_DIR + "kind.csv",
        )

    def create_arma_agreement(self):
        framework_data = deepcopy(test_framework_data)
        framework_data["qualificationPeriod"] = {"endDate": calculate_date(get_now(), timedelta(days=420)).isoformat()}

        self.create_framework(data=framework_data, config=deepcopy(test_framework_arma_config))
        self.activate_framework()

        for bid_data in (bid, bid2):
            self.create_submission(
                data={"tenderers": deepcopy(bid_data["tenderers"])},
                config={"restricted": False},
            )
            self.activate_submission()
            self.activate_qualification()

        response = self.get_framework()
        return response.json["data"]["agreementID"]

    def test_docs(self):
        request_path = "/tenders?opt_pretty=1"

        self.app.authorization = ("Basic", ("broker", ""))

        #### Agreement of the preliminary selection

        self.agreement_id = self.create_arma_agreement()

        with open(TARGET_DIR + "view-agreement.http", "w") as self.app.file_obj:
            response = self.app.get("/agreements/{}".format(self.agreement_id))
            self.assertEqual(response.status, "200 OK")

        #### Creating tender
        lots = test_lots[:1]
        lots[0]["id"] = uuid4().hex
        tender_data = {**test_tender_data, "lots": lots}

        with open(TARGET_DIR + "tender-post-attempt-without-agreement.http", "w") as self.app.file_obj:
            self.app.post_json(
                "/tenders?opt_pretty=1",
                {"data": tender_data, "config": self.initial_config},
                status=422,
            )

        with open(TARGET_DIR + "tender-post-attempt-unknown-agreement.http", "w") as self.app.file_obj:
            self.app.post_json(
                "/tenders?opt_pretty=1",
                {"data": {**tender_data, "agreement": {"id": "0" * 32}}, "config": self.initial_config},
                status=422,
            )

        tender_data["agreement"] = {"id": self.agreement_id}

        with open(TARGET_DIR + "tender-post-attempt-json-data.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1",
                {"data": tender_data, "config": self.initial_config},
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        owner_token = response.json["access"]["token"]
        self.tender_id = tender["id"]
        lot_id = lots[0]["id"]

        with open(TARGET_DIR + "blank-tender-view.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "tender-listing-no-auth.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        items[1]["relatedLot"] = lot_id
        with open(TARGET_DIR + "tender-add-relatedLot-to-item.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, "200 OK")

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]

        # Tender activating
        with open(TARGET_DIR + "notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"status": "active.tendering"}},
                status=422,
            )

        with open(TARGET_DIR + "add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token)

        with open(TARGET_DIR + "tender-activating.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "active-tender-listing-no-auth.http", "w") as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        #### Modifying tender

        tender_period_end_date = calculate_date(get_now(), timedelta(weeks=4, days=1))
        with open(TARGET_DIR + "patch-items-value-periods.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
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

        self.set_enquiry_period_end()
        self.app.authorization = ("Basic", ("broker", ""))

        with open(TARGET_DIR + "update-tender-before-tendering-end.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"description": "new description"}},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")

        response = self.app.get(f"/tenders/{self.tender_id}")
        tender = response.json["data"]

        tender_period_end_date = calculate_date(get_now(), timedelta(days=8))
        with open(TARGET_DIR + "update-tender-with-extended-period.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {
                    "data": {
                        "description": "new description",
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
        set_bid_lotvalues(bid_data, lots)
        set_bid_items(self, bid_data, tender["items"])
        with open(TARGET_DIR + "register-bidder.http", "w") as self.app.file_obj:
            response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
            bid1_id = response.json["data"]["id"]
            bids_access[bid1_id] = response.json["access"]["token"]
            self.assertEqual(response.status, "201 Created")

        with open(TARGET_DIR + "activate-bidder-without-proposal.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
                status=422,
            )

        with open(TARGET_DIR + "upload-bid-proposal.http", "w") as self.app.file_obj:
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

        with open(TARGET_DIR + "activate-bidder.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        tenderers = deepcopy(test_docs_bid_draft["tenderers"])
        tenderers[0]["name"] = "Школяр"
        # clear eContract fields
        for tenderer in tenderers:
            tenderer.pop("signerInfo", None)

        with open(TARGET_DIR + "patch-pending-bid.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"tenderers": tenderers}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "activate-bidder-without-sign.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
                status=422,
            )

        # Confidentiality

        with open(TARGET_DIR + "upload-bid-private-proposal.http", "w") as self.app.file_obj:
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
        with open(TARGET_DIR + "mark-bid-doc-private.http", "w") as self.app.file_obj:
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

        with open(TARGET_DIR + "bidder-documents.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "upload-bid-financial-document-proposal.http", "w") as self.app.file_obj:
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

        with open(TARGET_DIR + "bidder-financial-documents.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}/financial_documents?acc_token={}".format(
                    self.tender_id, bid1_id, bids_access[bid1_id]
                )
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "upload-bid-eligibility-document-proposal.http", "w") as self.app.file_obj:
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

        with open(TARGET_DIR + "upload-bid-qualification-document-proposal.http", "w") as self.app.file_obj:
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

        with open(TARGET_DIR + "bidder-view-financial-documents.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        #### Bid invalidation

        with open(TARGET_DIR + "bidder-after-changing-tender.http", "w") as self.app.file_obj:
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
        with open(TARGET_DIR + "bidder-activate-after-changing-tender.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "register-2nd-bidder.http", "w") as self.app.file_obj:
            bid2_draft = deepcopy(bid2)
            bid2_draft["status"] = "draft"
            set_bid_lotvalues(bid2_draft, lots)
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

        with open(TARGET_DIR + "register-3rd-bidder.http", "w") as self.app.file_obj:
            bid3_draft = deepcopy(bid3)
            bid3_draft["status"] = "draft"
            set_bid_lotvalues(bid3_draft, lots)
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

        #### Auction

        self.set_status("active.auction", {"id": self.tender_id, "status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.auction")

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
                {
                    "id": bid_id,
                    "lotValues": [{"participationUrl": "{}?key_for_bid={}".format(auction_url, bid_id)}],
                }
                for bid_id in (bid1_id, bid2_id, bid3_id)
            ],
        }
        response = self.app.patch_json(
            "/tenders/{}/auction/{}?acc_token={}".format(self.tender_id, lot_id, owner_token), {"data": patch_data}
        )
        self.assertEqual(response.status, "200 OK")

        self.app.authorization = ("Basic", ("broker", ""))

        with open(TARGET_DIR + "auction-url.http", "w") as self.app.file_obj:
            response = self.app.get("/tenders/{}".format(self.tender_id))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "bidder-participation-url.http", "w") as self.app.file_obj:
            response = self.app.get(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid1_id, bids_access[bid1_id])
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + "bidder2-participation-url.http", "w") as self.app.file_obj:
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
                                {"relatedLot": lot["relatedLot"], "value": lot["value"]} for lot in b["lotValues"]
                            ],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )

        self.app.authorization = ("Basic", ("broker", ""))

        response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, owner_token))
        # get pending award
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

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
                {"data": {"status": "unsuccessful"}},
                status=422,
            )
        with open(TARGET_DIR + "award-add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")

        with open(TARGET_DIR + "confirm-qualification.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        # get contract id
        response = self.app.get(f"/tenders/{self.tender_id}")
        contract = response.json["data"]["contracts"][-1]
        contract_id = contract["id"]

        ####  Set contract value

        with open(TARGET_DIR + "contract-set-contract-value-percentage.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                f"/contracts/{contract_id}?acc_token={owner_token}", {"data": {"value": {"amountPercentage": 35}}}
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["value"]["amountPercentage"], 35)

        #### Preparing the cancellation request

        with open(TARGET_DIR + "prepare-cancellation.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"reason": "cancellation reason", "reasonType": "noDemand"}},
            )
            self.assertEqual(response.status, "201 Created")

        cancellation_id = response.json["data"]["id"]

        with open(TARGET_DIR + "update-cancellation-reasonType.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"reasonType": "unFixable"}},
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

        with open(TARGET_DIR + "cancellation-sign-doc-is-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
                status=422,
            )

        with open(TARGET_DIR + "upload-cancellation-report-doc.http", "w") as self.app.file_obj:
            self.add_sign_doc(
                self.tender_id,
                owner_token,
                docs_url=f"/cancellations/{cancellation_id}/documents",
                document_type="cancellationReport",
            )

        #### Activating the request and cancelling tender
        with open(TARGET_DIR + "pending-cancellation.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")
