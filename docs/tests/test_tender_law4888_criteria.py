import os
from copy import deepcopy

from openprocurement.tender.core.tests.base import test_article_20_criteria
from openprocurement.tender.core.tests.criteria_utils import generate_responses
from openprocurement.tender.core.tests.utils import (
    set_bid_items,
    set_bid_lotvalues,
    set_tender_criteria,
)
from openprocurement.tender.open.tests.open_tendering.ua.base import (
    BaseTenderOpenTenderingUAWebTest,
)
from tests.base.constants import AUCTIONS_URL, DOCS_URL
from tests.base.data import (
    test_docs_bid_draft,
    test_docs_lots,
    test_docs_tender_openua,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

test_tender_data = deepcopy(test_docs_tender_openua)
test_tender_data["procurementMethodType"] = "openTendering"
test_tender_data["procedure"] = {"euPublished": False}

test_lots = deepcopy(test_docs_lots)
for test_lot in test_lots:
    test_lot["value"] = test_tender_data["value"]
    test_lot["minimalStep"] = {"amount": 5, "currency": "UAH"}

bid = deepcopy(test_docs_bid_draft)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, "source/tendering/law4888/http/")


class TenderLaw4888CriteriaResourceTest(BaseTenderOpenTenderingUAWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        self.setUpMock()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.tearDownMock()

    def test_docs(self):
        self.app.authorization = ("Basic", ("broker", ""))

        response = self.app.post_json(
            "/tenders?opt_pretty=1", {"data": test_tender_data, "config": self.initial_config}
        )
        self.assertEqual(response.status, "201 Created")
        tender = response.json["data"]
        owner_token = response.json["access"]["token"]
        self.tender_id = tender["id"]

        for test_lot in test_lots:
            response = self.app.post_json(
                "/tenders/{}/lots?acc_token={}".format(self.tender_id, owner_token), {"data": test_lot}
            )
            self.assertEqual(response.status, "201 Created")

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]
        lots = tender["lots"]

        items = deepcopy(tender["items"])
        for item in items:
            item["relatedLot"] = lots[0]["id"]
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, "200 OK")

        response = self.add_contract_proforma_doc(self.tender_id, owner_token)
        contract_proforma_doc_id = response.json["data"]["id"]

        criteria = deepcopy(test_article_20_criteria[:1])
        set_tender_criteria(criteria, lots, tender["items"])
        evidence = criteria[0]["requirementGroups"][0]["requirements"][0]["eligibleEvidences"][0]

        criteria_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, owner_token)

        evidence["title"] = ""
        with open(TARGET_DIR + "criteria-evidence-title-required.http", "w") as self.app.file_obj:
            self.app.post_json(criteria_path, {"data": criteria}, status=422)

        evidence["title"] = "Документальне підтвердження"
        with open(TARGET_DIR + "criteria-evidence-document-required.http", "w") as self.app.file_obj:
            self.app.post_json(criteria_path, {"data": criteria}, status=422)

        evidence["relatedDocument"] = {"id": contract_proforma_doc_id}
        with open(TARGET_DIR + "criteria-evidence-invalid-document-type.http", "w") as self.app.file_obj:
            self.app.post_json(criteria_path, {"data": criteria}, status=422)

        with open(TARGET_DIR + "add-evaluation-criteria-document.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/documents?acc_token={}".format(self.tender_id, owner_token),
                {
                    "data": {
                        "title": "evaluation_criteria.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": "evaluationCriteria",
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            evaluation_criteria_doc_id = response.json["data"]["id"]

        evidence["relatedDocument"] = {"id": evaluation_criteria_doc_id}
        with open(TARGET_DIR + "add-selection-criteria.http", "w") as self.app.file_obj:
            response = self.app.post_json(criteria_path, {"data": criteria})
            self.assertEqual(response.status, "201 Created")

        self.add_sign_doc(self.tender_id, owner_token)

        with open(TARGET_DIR + "activate-tender-without-selection-criteria.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"status": "active.tendering"}},
                status=403,
            )

        second_criteria = deepcopy(test_article_20_criteria[2:3])
        set_tender_criteria(second_criteria, lots, tender["items"])
        second_criteria[0]["relatedItem"] = lots[1]["id"]
        second_evidence = second_criteria[0]["requirementGroups"][0]["requirements"][0]["eligibleEvidences"][0]
        second_evidence["relatedDocument"] = {"id": evaluation_criteria_doc_id}

        with open(TARGET_DIR + "add-selection-criteria-second-lot.http", "w") as self.app.file_obj:
            response = self.app.post_json(criteria_path, {"data": second_criteria})
            self.assertEqual(response.status, "201 Created")

        with open(TARGET_DIR + "activate-tender.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
                {"data": {"status": "active.tendering"}},
            )
            self.assertEqual(response.status, "200 OK")

        bid_data = deepcopy(bid)
        set_bid_lotvalues(bid_data, [lots[0]])
        set_bid_items(self, bid_data, tender["items"])
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
        self.assertEqual(response.status, "201 Created")
        bid_id = response.json["data"]["id"]
        bid_token = response.json["access"]["token"]

        response = self.app.post_json(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
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
        proposal_doc_id = response.json["data"]["id"]

        requirement_responses = generate_responses(self)
        requirement_responses[0]["evidences"] = [
            {
                "title": "Документальне підтвердження",
                "type": "document",
                "relatedDocument": {"id": proposal_doc_id},
            }
        ]

        with open(TARGET_DIR + "bid-evidence-invalid-document-type.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {"data": {"requirementResponses": requirement_responses, "status": "pending"}},
                status=422,
            )

        with open(TARGET_DIR + "add-bid-qualification-document.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {
                    "data": {
                        "title": "qualification_documents.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": "qualificationDocuments",
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            qualification_doc_id = response.json["data"]["id"]

        requirement_responses[0]["evidences"][0]["relatedDocument"] = {"id": qualification_doc_id}
        with open(TARGET_DIR + "activate-bid-with-evidence.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {"data": {"requirementResponses": requirement_responses, "status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")
