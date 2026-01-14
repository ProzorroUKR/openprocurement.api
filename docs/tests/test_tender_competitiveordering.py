import datetime
import os
from copy import deepcopy
from uuid import uuid4

from openprocurement.api.context import get_request_now, set_request_now
from openprocurement.api.tests.base import test_signer_info
from openprocurement.framework.core.tests.base import FrameworkActionsTestMixin
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.tests.base import (
    test_framework_dps_config,
    test_framework_dps_data,
    test_submission_config,
    test_submission_data,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
)
from openprocurement.tender.competitiveordering.tests.long.base import (
    BaseTenderCOLongWebTest,
    test_tender_co_long_config,
    test_tender_co_long_criteria,
)
from openprocurement.tender.competitiveordering.tests.short.base import (
    BaseTenderCOShortWebTest,
    test_tender_co_short_config,
    test_tender_co_short_criteria,
)
from openprocurement.tender.core.tests.criteria_utils import generate_responses
from openprocurement.tender.core.tests.utils import set_tender_criteria
from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import test_docs_lots, test_docs_question, test_docs_tender_co
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.test_tender_config import TenderConfigCSVMixin

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/source/tendering/competitiveordering/"
TARGET_SHORT_DIR = BASE_DIR + "http/short/"
TARGET_LONG_DIR = BASE_DIR + "http/long/"
TARGET_CSV_DIR = BASE_DIR + "csv/"


class TenderrCOResourceTest(
    BaseTenderCOShortWebTest,
    TenderConfigCSVMixin,
    MockWebTestMixin,
):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="competitiveOrdering",
            file_path=TARGET_CSV_DIR + "config.csv",
        )

    def test_docs_allowed_kind_csv(self):
        self.write_allowed_kind_csv(
            pmt="competitiveOrdering",
            file_path=TARGET_CSV_DIR + "kind.csv",
        )


class TenderrCOShortResourceTest(
    BaseTenderCOShortWebTest,
    TenderConfigCSVMixin,
    FrameworkActionsTestMixin,
    MockWebTestMixin,
):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL
    framework_type = DPS_TYPE

    def setUp(self):
        super().setUp()
        self.setUpMock()
        set_request_now()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="competitiveOrdering.short",
            file_path=TARGET_CSV_DIR + "config-short.csv",
        )

    def test_docs_tutorial(self):
        # Create agreement

        self.tick(datetime.timedelta(days=-15))

        framework_data = deepcopy(test_framework_dps_data)
        framework_data["qualificationPeriod"] = {
            "endDate": (get_request_now() + datetime.timedelta(days=420)).isoformat()
        }
        item = deepcopy(test_docs_tender_co["items"][0])
        framework_data["items"] = [item]
        framework_data["classification"] = item["classification"]
        framework_config = deepcopy(test_framework_dps_config)
        framework_config["hasItems"] = True
        self.create_framework(data=framework_data, config=framework_config)
        self.activate_framework()

        # TODO: fix tick method
        self.tick(datetime.timedelta(days=30))

        submission_data = deepcopy(test_submission_data)
        submission_data["tenderers"][0]["identifier"]["id"] = "12345678"
        submission_config = deepcopy(test_submission_config)
        self.create_submission(data=submission_data, config=submission_config)
        self.activate_submission()
        self.activate_qualification()

        response = self.get_framework()
        self.agreement_id = response.json["data"]["agreementID"]

        # View agreement

        with open(TARGET_SHORT_DIR + "view-agreement-1-contract.http", "w") as self.app.file_obj:
            response = self.app.get("/agreements/{}".format(self.agreement_id))
            self.assertEqual(response.status, "200 OK")
            agreement = response.json["data"]

        self.app.authorization = ("Basic", ("broker", ""))

        # Creating tender

        data = deepcopy(test_docs_tender_co)
        data["items"] = [data["items"][0]]
        data["procuringEntity"]["identifier"]["id"] = test_framework_dps_data["procuringEntity"]["identifier"]["id"]

        data["agreements"] = [{"id": self.agreement_id}]

        lot = deepcopy(test_docs_lots[0])
        lot["value"] = data["value"]
        lot["minimalStep"] = {"amount": 5, "currency": "UAH"}
        lot["id"] = uuid4().hex

        data["lots"] = [lot]

        config = deepcopy(test_tender_co_short_config)

        for item in data["items"]:
            item["relatedLot"] = lot["id"]
            item["deliveryDate"] = {
                "startDate": (get_request_now() + datetime.timedelta(days=2)).isoformat(),
                "endDate": (get_request_now() + datetime.timedelta(days=5)).isoformat(),
            }
        for milestone in data["milestones"]:
            milestone["relatedLot"] = lot["id"]

        with open(TARGET_SHORT_DIR + "tender-post-attempt-json-data.http", "w") as self.app.file_obj:
            response = self.app.post_json("/tenders?opt_pretty=1", {"data": data, "config": config})
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        tender_id = self.tender_id = tender["id"]
        owner_token = response.json["access"]["token"]

        # add relatedLot for item

        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = tender["lots"][0]["id"]
        with open(TARGET_SHORT_DIR + "tender-add-relatedLot-to-item.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, "200 OK")

        # add criteria
        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]

        test_criteria_data = deepcopy(test_tender_co_short_criteria)
        set_tender_criteria(test_criteria_data, tender["lots"], tender["items"])

        with open(TARGET_SHORT_DIR + "add-exclusion-criteria.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(tender_id, owner_token), {"data": test_criteria_data}
            )
            self.assertEqual(response.status, "201 Created")

        # Tender activating (fail)

        with open(
            TARGET_SHORT_DIR + "tender-activating-insufficient-active-contracts-error.http", "w"
        ) as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token),
                {"data": {"status": "active.tendering"}},
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(response.json["errors"][0]["description"], "Agreement has less than 3 active contracts")

        # Add agreement contracts

        self.app.authorization = ("Basic", ("broker", ""))

        submission_data = deepcopy(test_submission_data)
        submission_data["tenderers"][0]["identifier"]["id"] = "11111111"
        submission_config = deepcopy(test_submission_config)
        self.create_submission(data=submission_data, config=submission_config)
        self.activate_submission()
        self.activate_qualification()

        submission_data = deepcopy(test_submission_data)
        submission_data["tenderers"][0]["identifier"]["id"] = "22222222"
        submission_config = deepcopy(test_submission_config)
        self.create_submission(data=submission_data, config=submission_config)
        self.activate_submission()
        self.activate_qualification()

        submission_tenderer = submission_data["tenderers"][0]

        bid_tenderer = deepcopy(submission_tenderer)
        bid_tenderer["signerInfo"] = test_signer_info

        # Tender activating
        with open(TARGET_SHORT_DIR + "notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token),
                {"data": {"status": "active.tendering"}},
                status=422,
            )

        with open(TARGET_SHORT_DIR + "add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(tender_id, owner_token)

        with open(TARGET_SHORT_DIR + "tender-activating.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, "200 OK")

        # try to add complaint
        with open(TARGET_SHORT_DIR + "tender-add-complaint-error.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                f"/tenders/{tender_id}/complaints?acc_token={owner_token}",
                {"data": test_tender_below_draft_complaint},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertEqual(
                response.json["errors"][0]["description"], "Can't add complaint as it is forbidden by configuration"
            )

        # Setting Bid guarantee

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={owner_token}",
            {"data": {"guarantee": {"amount": 8, "currency": "USD"}}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertIn("guarantee", response.json["data"])

        # Uploading documentation
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/documents?acc_token={owner_token}",
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

        # Registering bid
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            f"/tenders/{tender_id}/bids",
            {
                "data": {
                    "selfQualified": True,
                    "status": "draft",
                    "tenderers": [bid_tenderer],
                    "lotValues": [
                        {
                            "subcontractingDetails": "ДКП «Орфей», Україна",
                            "value": {"amount": 500},
                            "relatedLot": lot["id"],
                        }
                    ],
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        bid1_token = response.json["access"]["token"]
        bid1_id = response.json["data"]["id"]

        requirement_responses = generate_responses(self)
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/bids/{bid1_id}?acc_token={bid1_token}",
            {"data": {"requirementResponses": requirement_responses}},
        )
        self.assertEqual(response.status, "200 OK")
        self.add_sign_doc(
            self.tender_id,
            bid1_token,
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
        )

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/bids/{bid1_id}?acc_token={bid1_token}", {"data": {"status": "pending"}}
        )
        self.assertEqual(response.status, "200 OK")

        # Registering bid 2
        response = self.app.post_json(
            f"/tenders/{tender_id}/bids",
            {
                "data": {
                    "selfQualified": True,
                    "status": "draft",
                    "tenderers": [bid_tenderer],
                    "lotValues": [{"value": {"amount": 500}, "relatedLot": lot["id"]}],
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        bid2_id = response.json["data"]["id"]
        bid2_token = response.json["access"]["token"]
        self.add_sign_doc(
            self.tender_id,
            bid2_token,
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, "pending")

        lot_values = response.json["data"]["lotValues"]

        # Bids confirmation
        response = self.app.patch_json(
            f"/tenders/{tender_id}/bids/{bid2_id}?acc_token={bid2_token}",
            {
                "data": {
                    "lotValues": [{**lot_values[0], "value": {"amount": 500}, "relatedLot": lot["id"]}],
                    "status": "pending",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")

        # Registering bid 3
        agreement = self.mongodb.agreements.get(self.agreement_id)
        tenderer = deepcopy(bid_tenderer)
        tenderer["identifier"]["id"] = agreement["contracts"][1]["suppliers"][0]["identifier"]["id"]
        with open(TARGET_SHORT_DIR + "register-third-bid.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                f"/tenders/{tender_id}/bids",
                {
                    "data": {
                        "selfQualified": True,
                        "status": "draft",
                        "tenderers": [tenderer],
                        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot["id"]}],
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
        bid3_id = response.json["data"]["id"]
        bid3_token = response.json["access"]["token"]
        self.add_sign_doc(
            self.tender_id,
            bid3_token,
            docs_url=f"/bids/{bid3_id}/documents",
            document_type="proposal",
        )
        self.set_responses(tender_id, response.json, "pending")

        # disqualify second supplier from agreement during active.tendering
        agreement["contracts"][1]["status"] = "terminated"
        self.mongodb.agreements.save(agreement)

        self.set_status("active.tendering", startend="end")
        self.check_chronograph()
        with open(TARGET_SHORT_DIR + "active-tendering-end-not-member-bid.http", "w") as self.app.file_obj:
            response = self.app.get(
                f"/tenders/{tender_id}/bids/{bid3_id}?acc_token={bid3_token}",
            )
            self.assertEqual(response.status, "200 OK")

        #  Auction
        self.set_status("active.auction")
        self.app.authorization = ("Basic", ("auction", ""))
        auction1_url = f'{self.auctions_url}/tenders/{self.tender_id}_{lot["id"]}'
        patch_data = {
            "lots": [
                {
                    "id": lot["id"],
                    "auctionUrl": auction1_url,
                }
            ],
            "bids": [
                {
                    "id": bid1_id,
                    "lotValues": [
                        {"participationUrl": f"{auction1_url}?key_for_bid={bid1_id}"},
                    ],
                },
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": f"{auction1_url}?key_for_bid={bid2_id}"},
                    ],
                },
                {
                    "id": bid3_id,
                    "lotValues": [
                        {"participationUrl": f"{auction1_url}?key_for_bid={bid3_id}"},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            f'/tenders/{self.tender_id}/auction/{lot["id"]}?acc_token={owner_token}', {"data": patch_data}
        )
        self.assertEqual(response.status, "200 OK")

        # Confirming qualification
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get(f"/tenders/{self.tender_id}/auction")
        auction_bids_data = response.json["data"]["bids"]
        auction_bids_data[0]["lotValues"][0]["value"]["amount"] = 250  # too low price

        self.app.post_json(
            f'/tenders/{self.tender_id}/auction/{lot["id"]}',
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
        response = self.app.get(f"/tenders/{self.tender_id}/awards?acc_token={owner_token}")

        award = response.json["data"][0]
        award_id = award["id"]
        self.assertEqual(len(award.get("milestones", "")), 1)
        tender = self.mongodb.tenders.get(self.tender_id)
        tender["awards"][0]["milestones"][0]["dueDate"] = (get_request_now() - datetime.timedelta(days=1)).isoformat()
        self.mongodb.tenders.save(tender)

        self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={owner_token}",
            {"data": {"status": "active", "qualified": True}},
            status=200,
        )

        with open(TARGET_SHORT_DIR + "tender-get-award.http", "w") as self.app.file_obj:
            self.app.get(f"/tenders/{self.tender_id}/awards/{award_id}")

        # try to add complaint to award
        with open(TARGET_SHORT_DIR + "tender-add-complaint-qualification-error.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                f"/tenders/{tender_id}/awards/{award_id}/complaints?acc_token={bid2_token}",
                {"data": test_tender_below_draft_complaint},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertEqual(
                response.json["errors"][0]["description"], "Can't add complaint as it is forbidden by configuration"
            )

        # Preparing the cancellation request

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/cancellations?acc_token={owner_token}",
            {"data": {"reason": "cancellation reason", "reasonType": "unFixable"}},
        )
        self.assertEqual(response.status, "201 Created")

        cancellation_id = response.json["data"]["id"]

        #  Filling cancellation with protocol and supplementary documentation

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/documents?acc_token={owner_token}",
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

        # try to add complaint to cancellation
        with open(TARGET_SHORT_DIR + "tender-add-complaint-cancellation-error.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                f"/tenders/{tender_id}/cancellations/{cancellation_id}/complaints?acc_token={owner_token}",
                {"data": test_tender_below_draft_complaint},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertEqual(
                response.json["errors"][0]["description"], "Can't add complaint as it is forbidden by configuration"
            )

        with open(TARGET_SHORT_DIR + "cancellation-sign-doc-is-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
                status=422,
            )

        with open(TARGET_SHORT_DIR + "upload-cancellation-report-doc.http", "w") as self.app.file_obj:
            self.add_sign_doc(
                self.tender_id,
                owner_token,
                docs_url=f"/cancellations/{cancellation_id}/documents",
                document_type="cancellationReport",
            )

        # Activating the request and cancelling tender
        with open(TARGET_SHORT_DIR + "pending-cancellation.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                f"/tenders/{self.tender_id}/cancellations/{cancellation_id}?acc_token={owner_token}",
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        response = self.app.get(f"/tenders/{self.tender_id}?acc_token={owner_token}")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "cancelled")


class TenderrCOLongResourceTest(
    BaseTenderCOLongWebTest,
    TenderConfigCSVMixin,
    FrameworkActionsTestMixin,
    MockWebTestMixin,
):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL
    framework_type = DPS_TYPE

    def setUp(self):
        super().setUp()
        self.setUpMock()
        set_request_now()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs_config_csv(self):
        self.write_config_pmt_csv(
            pmt="competitiveOrdering.long",
            file_path=TARGET_CSV_DIR + "config-long.csv",
        )

    def test_docs_tutorial(self):
        # Create agreement

        self.tick(datetime.timedelta(days=-15))

        framework_data = deepcopy(test_framework_dps_data)
        framework_data["qualificationPeriod"] = {
            "endDate": (get_request_now() + datetime.timedelta(days=365)).isoformat()
        }
        item = deepcopy(test_docs_tender_co["items"][0])
        framework_data["classification"] = item["classification"]
        framework_config = deepcopy(test_framework_dps_config)
        self.create_framework(data=framework_data, config=framework_config)
        self.activate_framework()

        # TODO: fix tick method
        self.tick(datetime.timedelta(days=30))

        submission_data = deepcopy(test_submission_data)
        submission_data["tenderers"][0]["identifier"]["id"] = "12345678"
        submission_config = deepcopy(test_submission_config)
        self.create_submission(data=submission_data, config=submission_config)
        self.activate_submission()
        self.activate_qualification()

        response = self.get_framework()
        self.agreement_id = response.json["data"]["agreementID"]

        # View agreement

        with open(TARGET_LONG_DIR + "view-agreement-1-contract.http", "w") as self.app.file_obj:
            response = self.app.get("/agreements/{}".format(self.agreement_id))
            self.assertEqual(response.status, "200 OK")
            agreement = response.json["data"]

        self.app.authorization = ("Basic", ("broker", ""))

        # Creating tender

        data = deepcopy(test_docs_tender_co)
        data["items"] = [data["items"][0]]
        data["procuringEntity"]["identifier"]["id"] = test_framework_dps_data["procuringEntity"]["identifier"]["id"]

        data["agreements"] = [{"id": self.agreement_id}]

        lot = deepcopy(test_docs_lots[0])
        lot["value"] = data["value"]
        lot["minimalStep"] = {"amount": 5, "currency": "UAH"}
        lot["id"] = uuid4().hex

        data["lots"] = [lot]

        config = deepcopy(test_tender_co_long_config)

        for item in data["items"]:
            item["relatedLot"] = lot["id"]
            item["deliveryDate"] = {
                "startDate": (get_request_now() + datetime.timedelta(days=2)).isoformat(),
                "endDate": (get_request_now() + datetime.timedelta(days=5)).isoformat(),
            }
        for milestone in data["milestones"]:
            milestone["relatedLot"] = lot["id"]

        with open(TARGET_LONG_DIR + "tender-post-attempt-json-data.http", "w") as self.app.file_obj:
            response = self.app.post_json("/tenders?opt_pretty=1", {"data": data, "config": config})
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        tender_id = self.tender_id = tender["id"]
        owner_token = response.json["access"]["token"]

        # add relatedLot for item

        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = tender["lots"][0]["id"]
        with open(TARGET_LONG_DIR + "tender-add-relatedLot-to-item.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, "200 OK")

        # add criteria
        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]

        test_criteria_data = deepcopy(test_tender_co_long_criteria)
        set_tender_criteria(test_criteria_data, tender["lots"], tender["items"])

        with open(TARGET_LONG_DIR + "add-exclusion-criteria.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(tender_id, owner_token), {"data": test_criteria_data}
            )
            self.assertEqual(response.status, "201 Created")

        # Tender activating (fail)

        with open(
            TARGET_LONG_DIR + "tender-activating-insufficient-active-contracts-error.http", "w"
        ) as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token),
                {"data": {"status": "active.tendering"}},
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(response.json["errors"][0]["description"], "Agreement has less than 3 active contracts")

        # Add agreement contracts

        self.app.authorization = ("Basic", ("broker", ""))

        submission_data = deepcopy(test_submission_data)
        submission_data["tenderers"][0]["identifier"]["id"] = "11111111"
        submission_config = deepcopy(test_submission_config)
        self.create_submission(data=submission_data, config=submission_config)
        self.activate_submission()
        self.activate_qualification()

        submission_data = deepcopy(test_submission_data)
        submission_data["tenderers"][0]["identifier"]["id"] = "22222222"
        submission_config = deepcopy(test_submission_config)
        self.create_submission(data=submission_data, config=submission_config)
        self.activate_submission()
        self.activate_qualification()

        submission_tenderer = submission_data["tenderers"][0]

        bid_tenderer = deepcopy(submission_tenderer)
        bid_tenderer["signerInfo"] = test_signer_info

        # Tender activating
        with open(TARGET_LONG_DIR + "notice-document-required.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token),
                {"data": {"status": "active.tendering"}},
                status=422,
            )

        with open(TARGET_LONG_DIR + "add-notice-document.http", "w") as self.app.file_obj:
            self.add_sign_doc(tender_id, owner_token)

        with open(TARGET_LONG_DIR + "tender-activating.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"status": "active.tendering"}}
            )
            self.assertEqual(response.status, "200 OK")

        # asking questions
        docs_data = deepcopy(test_docs_question)
        docs_data["author"]["identifier"]["id"] = "11112222"
        with open(TARGET_LONG_DIR + "ask-question-invalid-author.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/questions".format(self.tender_id), {"data": docs_data}, status=403
            )
            self.assertEqual(response.status, "403 Forbidden")

        docs_data["author"]["identifier"]["id"] = agreement["contracts"][0]["suppliers"][0]["identifier"]["id"]
        with open(TARGET_LONG_DIR + "ask-question.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/questions".format(self.tender_id), {"data": docs_data}, status=201
            )
            question_id = response.json["data"]["id"]
            self.assertEqual(response.status, "201 Created")

        response = self.app.patch_json(
            "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question_id, owner_token),
            {"data": {"answer": "answer"}},
        )
        self.assertEqual(response.status, "200 OK")

        # Setting Bid guarantee

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={owner_token}",
            {"data": {"guarantee": {"amount": 8, "currency": "USD"}}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertIn("guarantee", response.json["data"])

        # Uploading documentation
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/documents?acc_token={owner_token}",
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

        # Registering bid
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            f"/tenders/{tender_id}/bids",
            {
                "data": {
                    "selfQualified": True,
                    "status": "draft",
                    "tenderers": [bid_tenderer],
                    "lotValues": [
                        {
                            "subcontractingDetails": "ДКП «Орфей», Україна",
                            "value": {"amount": 500},
                            "relatedLot": lot["id"],
                        }
                    ],
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        bid1_token = response.json["access"]["token"]
        bid1_id = response.json["data"]["id"]

        requirement_responses = generate_responses(self)
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/bids/{bid1_id}?acc_token={bid1_token}",
            {"data": {"requirementResponses": requirement_responses}},
        )
        self.assertEqual(response.status, "200 OK")
        self.add_sign_doc(
            self.tender_id,
            bid1_token,
            docs_url=f"/bids/{bid1_id}/documents",
            document_type="proposal",
        )

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/bids/{bid1_id}?acc_token={bid1_token}", {"data": {"status": "pending"}}
        )
        self.assertEqual(response.status, "200 OK")

        # Registering bid 2
        response = self.app.post_json(
            f"/tenders/{tender_id}/bids",
            {
                "data": {
                    "selfQualified": True,
                    "status": "draft",
                    "tenderers": [bid_tenderer],
                    "lotValues": [{"value": {"amount": 500}, "relatedLot": lot["id"]}],
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        bid2_id = response.json["data"]["id"]
        bid2_token = response.json["access"]["token"]
        self.add_sign_doc(
            self.tender_id,
            bid2_token,
            docs_url=f"/bids/{bid2_id}/documents",
            document_type="proposal",
        )
        self.set_responses(self.tender_id, response.json, "pending")

        lot_values = response.json["data"]["lotValues"]

        # Bids confirmation
        response = self.app.patch_json(
            f"/tenders/{tender_id}/bids/{bid2_id}?acc_token={bid2_token}",
            {
                "data": {
                    "lotValues": [{**lot_values[0], "value": {"amount": 500}, "relatedLot": lot["id"]}],
                    "status": "pending",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")

        # Registering bid 3
        agreement = self.mongodb.agreements.get(self.agreement_id)
        tenderer = deepcopy(bid_tenderer)
        tenderer["identifier"]["id"] = agreement["contracts"][1]["suppliers"][0]["identifier"]["id"]
        with open(TARGET_LONG_DIR + "register-third-bid.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                f"/tenders/{tender_id}/bids",
                {
                    "data": {
                        "selfQualified": True,
                        "status": "draft",
                        "tenderers": [tenderer],
                        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot["id"]}],
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
        bid3_id = response.json["data"]["id"]
        bid3_token = response.json["access"]["token"]
        self.add_sign_doc(
            self.tender_id,
            bid3_token,
            docs_url=f"/bids/{bid3_id}/documents",
            document_type="proposal",
        )
        self.set_responses(tender_id, response.json, "pending")

        # disqualify second supplier from agreement during active.tendering
        agreement["contracts"][1]["status"] = "terminated"
        self.mongodb.agreements.save(agreement)

        self.set_status("active.tendering", startend="end")
        self.check_chronograph()
        with open(TARGET_LONG_DIR + "active-tendering-end-not-member-bid.http", "w") as self.app.file_obj:
            response = self.app.get(
                f"/tenders/{tender_id}/bids/{bid3_id}?acc_token={bid3_token}",
            )
            self.assertEqual(response.status, "200 OK")

        #  Auction
        self.set_status("active.auction")
        self.app.authorization = ("Basic", ("auction", ""))
        auction1_url = f'{self.auctions_url}/tenders/{self.tender_id}_{lot["id"]}'
        patch_data = {
            "lots": [
                {
                    "id": lot["id"],
                    "auctionUrl": auction1_url,
                }
            ],
            "bids": [
                {
                    "id": bid1_id,
                    "lotValues": [
                        {"participationUrl": f"{auction1_url}?key_for_bid={bid1_id}"},
                    ],
                },
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": f"{auction1_url}?key_for_bid={bid2_id}"},
                    ],
                },
                {
                    "id": bid3_id,
                    "lotValues": [
                        {"participationUrl": f"{auction1_url}?key_for_bid={bid3_id}"},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            f'/tenders/{self.tender_id}/auction/{lot["id"]}?acc_token={owner_token}', {"data": patch_data}
        )
        self.assertEqual(response.status, "200 OK")

        # Confirming qualification
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get(f"/tenders/{self.tender_id}/auction")
        auction_bids_data = response.json["data"]["bids"]
        auction_bids_data[0]["lotValues"][0]["value"]["amount"] = 250  # too low price

        self.app.post_json(
            f'/tenders/{self.tender_id}/auction/{lot["id"]}',
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
        response = self.app.get(f"/tenders/{self.tender_id}/awards?acc_token={owner_token}")

        award = response.json["data"][0]
        award_id = award["id"]
        self.assertEqual(len(award.get("milestones", "")), 1)
        tender = self.mongodb.tenders.get(self.tender_id)
        tender["awards"][0]["milestones"][0]["dueDate"] = (get_request_now() - datetime.timedelta(days=1)).isoformat()
        self.mongodb.tenders.save(tender)

        self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={owner_token}",
            {"data": {"status": "active", "qualified": True}},
            status=200,
        )
