import os
from copy import deepcopy

from openprocurement.tender.core.constants import (
    CRITERION_BID_GUARANTEE,
    CRITERION_BID_LANGUAGE,
    CRITERION_BID_VALIDITY_PERIOD,
    CRITERION_SUBCONTRACTING_PROPORTION,
    QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA,
)
from openprocurement.tender.core.tests.base import (
    get_criteria_by_ids,
    test_article_20_criteria,
    test_article_21_criteria,
    test_criteria_other_law_4888,
)
from openprocurement.tender.core.tests.criteria_utils import generate_responses
from openprocurement.tender.core.tests.utils import (
    change_auth,
    set_bid_items,
    set_bid_lotvalues,
    set_criteria_evidences_document,
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

        exclusion_criteria = [
            criterion
            for criterion in deepcopy(test_article_21_criteria)
            if criterion["classification"]["id"] != CRITERION_SUBCONTRACTING_PROPORTION
        ]
        set_tender_criteria(exclusion_criteria, lots, tender["items"])
        set_criteria_evidences_document(exclusion_criteria, evaluation_criteria_doc_id)

        with open(TARGET_DIR + "exclusion-criteria-invalid-document-type.http", "w") as self.app.file_obj:
            self.app.post_json(criteria_path, {"data": exclusion_criteria}, status=422)

        with open(TARGET_DIR + "add-eligibility-criteria-document.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/documents?acc_token={}".format(self.tender_id, owner_token),
                {
                    "data": {
                        "title": "eligibility_criteria.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": "eligibilityCriteria",
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            eligibility_criteria_doc_id = response.json["data"]["id"]

        set_criteria_evidences_document(exclusion_criteria, eligibility_criteria_doc_id)

        subcontracting_criteria = []
        for lot in lots:
            lot_criteria = [
                criterion
                for criterion in deepcopy(test_article_21_criteria)
                if criterion["classification"]["id"] == CRITERION_SUBCONTRACTING_PROPORTION
            ]
            subcontracting_criteria.extend(set_tender_criteria(lot_criteria, [lot], tender["items"]))
        set_criteria_evidences_document(subcontracting_criteria, evaluation_criteria_doc_id)

        with open(TARGET_DIR + "add-exclusion-criteria.http", "w") as self.app.file_obj:
            response = self.app.post_json(criteria_path, {"data": exclusion_criteria + subcontracting_criteria})
            self.assertEqual(response.status, "201 Created")

        other_criteria = deepcopy(
            get_criteria_by_ids(test_criteria_other_law_4888, {CRITERION_BID_LANGUAGE, CRITERION_BID_VALIDITY_PERIOD})
        )
        set_tender_criteria(other_criteria, lots, tender["items"])

        with open(TARGET_DIR + "add-other-criteria.http", "w") as self.app.file_obj:
            response = self.app.post_json(criteria_path, {"data": other_criteria})
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

        response = self.app.post_json(
            "/tenders/{}/documents?acc_token={}".format(self.tender_id, owner_token),
            {
                "data": {
                    "title": "bidding_documents.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "biddingDocuments",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        bidding_documents_doc_id = response.json["data"]["id"]

        guarantee_criteria = deepcopy(get_criteria_by_ids(test_criteria_other_law_4888, {CRITERION_BID_GUARANTEE}))
        set_tender_criteria(guarantee_criteria, lots, tender["items"])
        set_criteria_evidences_document(guarantee_criteria, bidding_documents_doc_id)
        guarantee_criteria[0]["relatesTo"] = "tender"
        del guarantee_criteria[0]["relatedItem"]

        with open(TARGET_DIR + "criteria-bid-guarantee-relates-to.http", "w") as self.app.file_obj:
            self.app.post_json(criteria_path, {"data": guarantee_criteria}, status=422)

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

        response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
        requirement_criteria = {
            requirement["id"]: criterion["classification"]["id"]
            for criterion in response.json["data"]
            for group in criterion["requirementGroups"]
            for requirement in group["requirements"]
        }

        def find_response(classification_id):
            return next(
                req_response
                for req_response in requirement_responses
                if requirement_criteria[req_response["requirement"]["id"]] == classification_id
            )

        requirement_responses = generate_responses(self)
        selection_response = find_response(test_article_20_criteria[0]["classification"]["id"])
        exclusion_response = find_response("CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION")

        selection_response["evidences"] = [
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

        selection_response["evidences"][0]["relatedDocument"] = {"id": qualification_doc_id}

        exclusion_response["evidences"] = [
            {
                "title": "Документальне підтвердження",
                "type": "document",
                "relatedDocument": {"id": qualification_doc_id},
            }
        ]
        with open(TARGET_DIR + "bid-exclusion-evidence-invalid-document-type.http", "w") as self.app.file_obj:
            self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {"data": {"requirementResponses": requirement_responses, "status": "pending"}},
                status=422,
            )

        with open(TARGET_DIR + "add-bid-eligibility-document.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders/{}/bids/{}/eligibility_documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {
                    "data": {
                        "title": "eligibility_documents.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": "eligibilityDocuments",
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            eligibility_doc_id = response.json["data"]["id"]

        exclusion_response["evidences"][0]["relatedDocument"] = {"id": eligibility_doc_id}
        with open(TARGET_DIR + "activate-bid-with-evidence.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
                {"data": {"requirementResponses": requirement_responses, "status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")

        self.set_status("active.qualification")
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [bid_data["tenderers"][0]],
                        "status": "pending",
                        "bid_id": bid_id,
                        "lotID": lots[0]["id"],
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            award_id = response.json["data"]["id"]

        award_path = "/tenders/{}/awards/{}".format(self.tender_id, award_id)
        blocking_requirement_ids = {
            requirement_id: classification_id
            for requirement_id, classification_id in requirement_criteria.items()
            if classification_id in QUALIFICATION_ACTIVATION_BLOCKING_CRITERIA
        }

        with open(TARGET_DIR + "award-exclusion-responses.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "{}/requirement_responses?acc_token={}".format(award_path, owner_token),
                {
                    "data": [
                        {"requirement": {"id": requirement_id}, "value": True}
                        for requirement_id in blocking_requirement_ids
                    ]
                },
            )
            self.assertEqual(response.status, "201 Created")
            award_responses = {rr["requirement"]["id"]: rr["id"] for rr in response.json["data"]}

        self.add_sign_doc(self.tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")

        with open(TARGET_DIR + "activate-award-with-exclusion-grounds.http", "w") as self.app.file_obj:
            with change_auth(self.app, ("Basic", ("token", ""))):
                self.app.patch_json(
                    "{}?acc_token={}".format(award_path, owner_token),
                    {"data": {"status": "active", "qualified": True, "eligible": True}},
                    status=422,
                )

        for requirement_id in blocking_requirement_ids:
            self.app.patch_json(
                "{}/requirement_responses/{}?acc_token={}".format(
                    award_path, award_responses[requirement_id], owner_token
                ),
                {"data": {"value": False}},
            )

        with open(TARGET_DIR + "activate-award.http", "w") as self.app.file_obj:
            with change_auth(self.app, ("Basic", ("token", ""))):
                response = self.app.patch_json(
                    "{}?acc_token={}".format(award_path, owner_token),
                    {"data": {"status": "active", "qualified": True, "eligible": True}},
                )
                self.assertEqual(response.status, "200 OK")
