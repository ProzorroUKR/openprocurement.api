from copy import deepcopy
from uuid import uuid4

from openprocurement.tender.core.constants import CRITERION_SUBCONTRACTING_PROPORTION
from openprocurement.tender.core.tests.base import (
    get_criteria_by_ids,
    test_article_20_criteria,
    test_criteria_all_law_4888,
)
from openprocurement.tender.core.tests.utils import set_tender_criteria

SELECTION_CRITERIA_IDS = {criterion["classification"]["id"] for criterion in test_article_20_criteria}


def criterion_evidence_document_type(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    criteria_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)
    evaluation_doc_id = self.get_criteria_doc_id(document_type="evaluationCriteria")
    eligibility_doc_id = self.get_criteria_doc_id(document_type="eligibilityCriteria")

    cases = (
        (SELECTION_CRITERIA_IDS, "evaluationCriteria", evaluation_doc_id),
        ({CRITERION_SUBCONTRACTING_PROPORTION}, "evaluationCriteria", evaluation_doc_id),
        ({"CRITERION.EXCLUSION.CONVICTIONS.FRAUD"}, "eligibilityCriteria", eligibility_doc_id),
    )
    for classification_ids, document_type, valid_doc_id in cases:
        invalid_doc_id = eligibility_doc_id if valid_doc_id == evaluation_doc_id else evaluation_doc_id
        criteria = deepcopy(get_criteria_by_ids(test_criteria_all_law_4888, classification_ids)[:1])
        set_tender_criteria(criteria, tender.get("lots", []), tender.get("items", []))
        for requirement_group in criteria[0]["requirementGroups"]:
            for criterion_requirement in requirement_group["requirements"]:
                criterion_requirement.pop("eligibleEvidences", None)
        requirement = criteria[0]["requirementGroups"][0]["requirements"][0]
        requirement["id"] = uuid4().hex
        requirement["eligibleEvidences"] = [
            {
                "title": "Документальне підтвердження",
                "type": "document",
                "relatedDocument": {"id": invalid_doc_id},
            }
        ]

        response = self.app.post_json(criteria_path, {"data": criteria}, status=422)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "requirementGroups",
                    "description": [
                        {
                            "requirements": [
                                {
                                    "eligibleEvidences": [
                                        {
                                            "relatedDocument": [
                                                f"relatedDocument should have documentType {document_type} "
                                                f"(requirement {requirement['id']})"
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                }
            ],
        )

        requirement["eligibleEvidences"][0]["relatedDocument"]["id"] = valid_doc_id
        response = self.app.post_json(criteria_path, {"data": criteria})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(
            response.json["data"][0]["requirementGroups"][0]["requirements"][0]["eligibleEvidences"][0][
                "relatedDocument"
            ]["id"],
            valid_doc_id,
        )


def criterion_evidence_title_required(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    criteria = deepcopy(test_article_20_criteria[:1])
    set_tender_criteria(criteria, tender.get("lots", []), tender.get("items", []))
    self.set_criteria_evidences_doc(criteria)
    criteria[0]["requirementGroups"][0]["requirements"][0]["id"] = uuid4().hex
    evidence = criteria[0]["requirementGroups"][0]["requirements"][0]["eligibleEvidences"][0]
    requirement_id = criteria[0]["requirementGroups"][0]["requirements"][0]["id"]

    criteria_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)
    expected_errors = [
        {
            "location": "body",
            "name": "requirementGroups",
            "description": [
                {
                    "requirements": [
                        {"eligibleEvidences": [{"title": [f"This field is required (requirement {requirement_id})"]}]}
                    ]
                }
            ],
        }
    ]

    for title in ("", "   "):
        evidence["title"] = title
        response = self.app.post_json(criteria_path, {"data": criteria}, status=422)
        self.assertEqual(response.json["errors"], expected_errors)

    del evidence["title"]
    response = self.app.post_json(criteria_path, {"data": criteria}, status=422)
    self.assertEqual(response.json["errors"], expected_errors)

    evidence["title"] = "Документальне підтвердження"
    response = self.app.post_json(criteria_path, {"data": criteria})
    self.assertEqual(response.status, "201 Created")
    criterion = response.json["data"][0]
    rg = criterion["requirementGroups"][0]
    requirement = rg["requirements"][0]
    self.assertEqual(requirement["eligibleEvidences"][0]["title"], "Документальне підтвердження")

    posted_evidence = deepcopy(requirement["eligibleEvidences"][0])
    del posted_evidence["id"]
    invalid_evidence = deepcopy(posted_evidence)
    invalid_evidence["title"] = ""

    evidences_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
        self.tender_id, criterion["id"], rg["id"], requirement["id"], self.tender_token
    )
    response = self.app.post_json(evidences_path, {"data": invalid_evidence}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "title",
                "description": [f"This field is required (requirement {requirement['id']})"],
            }
        ],
    )

    response = self.app.post_json(evidences_path, {"data": posted_evidence})
    self.assertEqual(response.status, "201 Created")
    evidence_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences/{}?acc_token={}".format(
            self.tender_id, criterion["id"], rg["id"], requirement["id"], evidence_id, self.tender_token
        ),
        {"data": {"title": ""}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "title",
                "description": [f"This field is required (requirement {requirement['id']})"],
            }
        ],
    )

    rg_data = deepcopy(rg)
    del rg_data["id"]
    for rg_requirement in rg_data["requirements"]:
        rg_requirement["id"] = uuid4().hex
        rg_requirement["eligibleEvidences"] = [invalid_evidence]
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups?acc_token={}".format(
            self.tender_id, criterion["id"], self.tender_token
        ),
        {"data": rg_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": [
                    {
                        "eligibleEvidences": [
                            {"title": [f"This field is required (requirement {rg_data['requirements'][0]['id']})"]}
                        ]
                    }
                ],
            }
        ],
    )

    self.set_status("active.tendering")
    response = self.app.put_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
            self.tender_id, criterion["id"], rg["id"], requirement["id"], self.tender_token
        ),
        {"data": {"eligibleEvidences": [invalid_evidence]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "eligibleEvidences",
                "description": [{"title": [f"This field is required (requirement {requirement['id']})"]}],
            }
        ],
    )


def add_required_criteria(self, tender):
    lots = tender.get("lots", [])
    items = tender.get("items", [])
    criteria = []
    for criterion in self.default_criteria:
        if criterion["classification"]["id"] in SELECTION_CRITERIA_IDS:
            continue
        # lot related criteria are required for every lot, not for a single one
        related_lots = lots if criterion.get("relatesTo") == "lot" and lots else [None]
        for lot in related_lots:
            criteria.extend(set_tender_criteria([deepcopy(criterion)], [lot] if lot else lots, items))
    self.set_criteria_evidences_doc(criteria)
    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": criteria},
    )
    self.assertEqual(response.status, "201 Created")


def activate_tender_with_cancelled_selection_criterion_requirements(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    lots = tender["lots"]

    self.add_sign_doc(self.tender_id, self.tender_token)

    doc = self.mongodb.tenders.get(self.tender_id)
    doc["mainProcurementCategory"] = "services"
    self.mongodb.tenders.save(doc)

    add_required_criteria(self, tender)

    criteria = deepcopy(test_article_20_criteria[:2])
    set_tender_criteria(criteria, lots, tender.get("items", []))
    criteria[0]["relatedItem"] = lots[0]["id"]
    criteria[1]["relatedItem"] = lots[1]["id"]
    self.set_criteria_evidences_doc(criteria)

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": criteria},
    )
    self.assertEqual(response.status, "201 Created")
    criterion = response.json["data"][0]

    for rg in criterion["requirementGroups"]:
        for requirement in rg["requirements"]:
            response = self.app.patch_json(
                "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
                    self.tender_id, criterion["id"], rg["id"], requirement["id"], self.tender_token
                ),
                {"data": {"status": "cancelled"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": self.primary_tender_status}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": (
                    f"Tender must contain one of article 20 criteria for lot {lots[0]['id']}: "
                    f"{', '.join(sorted(SELECTION_CRITERIA_IDS))}"
                ),
            }
        ],
    )


def activate_tender_with_selection_criteria_per_lot(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    lots = tender["lots"]
    self.assertEqual(len(lots), 2)

    self.add_sign_doc(self.tender_id, self.tender_token)

    doc = self.mongodb.tenders.get(self.tender_id)
    doc["mainProcurementCategory"] = "services"
    self.mongodb.tenders.save(doc)

    add_required_criteria(self, tender)

    criteria_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)
    request_path = "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)

    first_criterion = deepcopy(test_article_20_criteria[:1])
    set_tender_criteria(first_criterion, lots, tender.get("items", []))
    first_criterion[0]["relatedItem"] = lots[0]["id"]
    self.set_criteria_evidences_doc(first_criterion)

    response = self.app.post_json(criteria_path, {"data": first_criterion})
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        request_path,
        {"data": {"status": self.primary_tender_status}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": (
                    f"Tender must contain one of article 20 criteria for lot {lots[1]['id']}: "
                    f"{', '.join(sorted(SELECTION_CRITERIA_IDS))}"
                ),
            }
        ],
    )

    third_criterion = deepcopy(test_article_20_criteria[2:3])
    set_tender_criteria(third_criterion, lots, tender.get("items", []))
    third_criterion[0]["relatedItem"] = lots[1]["id"]
    self.set_criteria_evidences_doc(third_criterion)

    response = self.app.post_json(criteria_path, {"data": third_criterion})
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(request_path, {"data": {"status": self.primary_tender_status}})
    self.assertEqual(response.json["data"]["status"], self.primary_tender_status)

    criteria = [
        criterion
        for criterion in response.json["data"]["criteria"]
        if criterion["classification"]["id"] in SELECTION_CRITERIA_IDS
    ]
    self.assertEqual(
        {(criterion["classification"]["id"], criterion["relatedItem"]) for criterion in criteria},
        {
            (test_article_20_criteria[0]["classification"]["id"], lots[0]["id"]),
            (test_article_20_criteria[2]["classification"]["id"], lots[1]["id"]),
        },
    )
