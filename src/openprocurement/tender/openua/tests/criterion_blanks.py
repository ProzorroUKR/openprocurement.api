from copy import deepcopy
from datetime import timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

from openprocurement.api.constants import ARTICLE_16
from openprocurement.api.utils import get_now
from openprocurement.tender.core.constants import CRITERION_TECHNICAL_FEATURES
from openprocurement.tender.core.tests.base import (
    get_criteria_by_ids,
    test_article_16_criteria,
    test_criteria_all,
    test_exclusion_criteria,
    test_language_criteria,
    test_lcc_tender_criteria,
    test_requirement_groups,
    test_tech_feature_criteria,
)
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.core.tests.utils import set_tender_criteria
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_category,
    test_tender_pq_short_profile,
)


def create_tender_criteria_valid(self):
    request_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)
    criteria = deepcopy(test_exclusion_criteria)

    criterion = deepcopy(criteria[0])
    criterion["classification"]["id"] = "CRITERION.NO.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION"

    response = self.app.post_json(request_path, {"data": criteria})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response3 = self.app.post_json(request_path, {"data": [criterion, criterion]}, status=403)
    self.assertEqual(response3.status, "403 Forbidden")
    self.assertEqual(response3.content_type, "application/json")
    self.assertEqual(response3.json["status"], "error")
    self.assertEqual(
        response3.json["errors"], [{"location": "body", "name": "data", "description": "Criteria are not unique"}]
    )
    # try to PATCH criteria via tender
    if "stage2" not in self.initial_data["procurementMethodType"]:
        response3 = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"criteria": [criterion, criterion]}},
            status=403,
        )
        self.assertEqual(
            response3.json["errors"], [{"location": "body", "name": "data", "description": "Criteria are not unique"}]
        )
    response3 = self.app.post_json(request_path, {"data": [criterion]})
    self.assertEqual(response3.status, "201 Created")
    self.assertEqual(response3.content_type, "application/json")
    criterion_id = response3.json["data"][0]["id"]
    criterion_data = response3.json["data"][0]

    response3 = self.app.patch_json(
        "/tenders/{}/criteria/{}?acc_token={}".format(self.tender_id, criterion_id, self.tender_token),
        {
            "data": {
                "classification": {
                    **criterion_data["classification"],
                    "id": criteria[0]["classification"]["id"],
                }
            }
        },
        status=403,
    )
    self.assertEqual(response3.status, "403 Forbidden")
    self.assertEqual(response3.content_type, "application/json")
    self.assertEqual(response3.json["status"], "error")
    self.assertEqual(
        response3.json["errors"], [{"location": "body", "name": "data", "description": "Criteria are not unique"}]
    )

    try:
        lot_id = self.app.get("/tenders/{}".format(self.tender_id)).json["data"]["lots"][0]["id"]
    except KeyError:
        pass
    else:
        criterion["classification"]["id"] = 'CRITERION.NO1.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION'
        criterion2 = deepcopy(criterion)
        criterion["relatesTo"] = "lot"
        criterion["relatedItem"] = lot_id

        response2 = self.app.post_json(request_path, {"data": [criterion, criterion2]}, status=201)
        self.assertEqual(response2.status, "201 Created")
        self.assertEqual(response2.content_type, "application/json")

    response2 = self.app.post_json(request_path, {"data": test_exclusion_criteria}, status=403)
    self.assertEqual(response2.status, "403 Forbidden")
    self.assertEqual(response2.content_type, "application/json")
    self.assertEqual(response2.json["status"], "error")
    self.assertEqual(
        response2.json["errors"], [{"location": "body", "name": "data", "description": "Criteria are not unique"}]
    )

    criterion = deepcopy(criteria[0])
    self.assertIn("requirementGroups", criterion)
    for requirementGroup in criterion["requirementGroups"]:
        self.assertIn("requirements", requirementGroup)

    lang_criterion = deepcopy(test_language_criteria)
    response = self.app.post_json(request_path, {"data": lang_criterion})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    existed_id = response.json["data"][0]["id"]

    criterion["classification"]["id"] = 'CRITERION.CONVICTIONS.OTHER'
    criterion["id"] = existed_id
    response = self.app.post_json(request_path, {"data": [criterion]}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': 'Criterion id should be uniq for all criterions',
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    # Try to create criterion without legislation

    invalid_criteria = deepcopy(test_exclusion_criteria)
    legislation = invalid_criteria[0].pop('legislation')
    response = self.app.post_json(request_path, {"data": invalid_criteria}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "legislation", "description": ["This field is required."]}],
    )


def create_tender_criteria_invalid(self):
    invalid_criteria = deepcopy(test_exclusion_criteria)
    invalid_criteria[0]["relatesTo"] = "lot"

    request_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)

    response = self.app.post_json(request_path, {"data": []}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "data", "description": "Data not available"}]
    )

    response = self.app.post_json(request_path, {"data": ["some text"]}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "data", "description": "Data not available"}]
    )

    response = self.app.post_json(request_path, {"data": invalid_criteria}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["This field is required."],
                "location": "body",
                "name": "relatedItem",
            }
        ],
    )

    invalid_criteria[0]["relatedItem"] = "0" * 32
    response = self.app.post_json(request_path, {"data": invalid_criteria}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["relatedItem should be one of lots"],
                "location": "body",
                "name": "relatedItem",
            }
        ],
    )

    invalid_criteria[0]["relatesTo"] = "item"
    response = self.app.post_json(request_path, {"data": invalid_criteria}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["relatedItem should be one of items"],
                "location": "body",
                "name": "relatedItem",
            }
        ],
    )

    invalid_criteria[0]["relatesTo"] = "tenderer"
    del invalid_criteria[0]["relatedItem"]

    requirement_1 = invalid_criteria[0]["requirementGroups"][0]["requirements"][0]
    requirement_1["expectedValue"] = 100
    requirement_1["relatedFeature"] = "0" * 32
    response = self.app.post_json(request_path, {"data": invalid_criteria}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'requirementGroups',
                'description': [
                    {
                        'requirements': [
                            {
                                'relatedFeature': ['relatedFeature should be one of features'],
                                'expectedValue': ['Must be either true or false.'],
                            }
                        ]
                    }
                ],
            }
        ],
    )

    requirement_1["minValue"] = "min some text"
    requirement_1["maxValue"] = 100
    requirement_1["dataType"] = "number"
    del requirement_1["relatedFeature"]
    response = self.app.post_json(request_path, {"data": invalid_criteria}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'requirementGroups',
                "description": [
                    {
                        "requirements": [
                            {
                                "minValue": [
                                    "Number 'min some text' failed to convert to a decimal.",
                                ],
                                "expectedValue": [
                                    "expectedValue conflicts with ['minValue', 'maxValue', 'expectedValues']",
                                ],
                            }
                        ]
                    }
                ],
            }
        ],
    )

    lang_criterion = deepcopy(test_language_criteria)
    lang_criterion[0]["requirementGroups"][0]["requirements"][0]["eligibleEvidences"] = [
        {"description": "Довідка в довільній формі", "type": "document", "title": "Документальне підтвердження"}
    ]

    response = self.app.post_json(request_path, {"data": lang_criterion}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'requirementGroups',
                'description': [
                    {"eligibleEvidences": ["This field is forbidden for current criterion"]},
                ],
            }
        ],
    )

    lang_criterion = deepcopy(test_language_criteria)
    del lang_criterion[0]["relatesTo"]
    response = self.app.post_json(request_path, {"data": lang_criterion}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{'location': 'body', 'name': 'relatesTo', 'description': ['This field is required.']}]
    )


def patch_tender_criteria_valid(self):
    criteria_data = deepcopy(test_exclusion_criteria)
    criteria_data[0]["classification"]["id"] = "CRITERION.OTHER"

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token), {"data": criteria_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    criteria_id = response.json["data"][0]["id"]

    request_path = "/tenders/{}/criteria/{}?acc_token={}".format(self.tender_id, criteria_id, self.tender_token)

    updated_data = {
        "title": "Оновлена назва",
        "title_en": "Updated title",
        "title_ru": "Обновлённое название",
        "description": "Оновлений опис",
    }
    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
    )

    criteria = response.json["data"]

    self.assertEqual(criteria["title"], updated_data["title"])
    self.assertEqual(criteria["title_en"], updated_data["title_en"])
    self.assertEqual(criteria["title_ru"], updated_data["title_ru"])
    self.assertEqual(criteria["description"], updated_data["description"])

    updated_data = {
        "classification": {**criteria["classification"], "id": criteria_data[1]["classification"]["id"]},
    }

    response = self.app.patch_json(request_path, {"data": updated_data}, status=403)
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "data", "description": "Criteria are not unique"}]
    )

    updated_data["relatesTo"] = "tenderer"
    self.app.patch_json(request_path, {"data": updated_data}, status=200)


def patch_tender_criteria_invalid(self):
    criteria_data = deepcopy(test_exclusion_criteria)
    criteria_data[0]["classification"]["id"] = "CRITERION.OTHER"

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token), {"data": criteria_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    criteria_id = response.json["data"][0]["id"]
    criteria_not_editable_id = response.json["data"][1]["id"]

    request_path = "/tenders/{}/criteria/{}?acc_token={}".format(self.tender_id, criteria_id, self.tender_token)

    updated_data = {
        "title": "Оновлена назва",
        "title_en": "Updated title",
        "title_ru": "Обновлённое название",
        "description": "Оновлений опис",
    }

    response = self.app.patch_json(
        "/tenders/{}/criteria/{}?acc_token={}".format(self.tender_id, criteria_not_editable_id, self.tender_token),
        {"data": updated_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Can't update exclusion ecriteria objects",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    updated_data["relatesTo"] = "lot"
    response = self.app.patch_json(request_path, {"data": updated_data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["This field is required."],
                "location": "body",
                "name": "relatedItem",
            }
        ],
    )

    updated_data["relatedItem"] = "0" * 32
    response = self.app.patch_json(request_path, {"data": updated_data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["relatedItem should be one of lots"],
                "location": "body",
                "name": "relatedItem",
            }
        ],
    )

    updated_data["relatesTo"] = "item"

    response = self.app.patch_json(request_path, {"data": updated_data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["relatedItem should be one of items"],
                "location": "body",
                "name": "relatedItem",
            }
        ],
    )


def get_tender_criteria(self):
    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_exclusion_criteria}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    criteria_id = response.json["data"][0]["id"]

    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    criteria = response.json["data"]

    self.assertIn("requirementGroups", criteria[0])
    self.assertEqual(len(test_exclusion_criteria[0]["requirementGroups"]), len(criteria[0]["requirementGroups"]))

    for i, criterion in enumerate(criteria):
        for k, v in criterion.items():
            if k not in ["id", "requirementGroups"]:
                self.assertEqual(test_exclusion_criteria[i][k], v)

    response = self.app.get("/tenders/{}/criteria/{}".format(self.tender_id, criteria_id))
    criterion = response.json["data"]

    for k, v in criterion.items():
        if k not in ["id", "requirementGroups"]:
            self.assertEqual(test_exclusion_criteria[0][k], v)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_category",
    Mock(return_value=test_tender_pq_category),
)
@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
    Mock(return_value=test_tender_pq_short_profile),
)
@patch(
    "openprocurement.tender.core.procedure.criteria.get_tender_category",
    Mock(return_value=test_tender_pq_category),
)
@patch(
    "openprocurement.tender.core.procedure.criteria.get_tender_profile",
    Mock(return_value=test_tender_pq_short_profile),
)
def activate_tender(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    request_path = "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)
    self.add_sign_doc(self.tender_id, self.tender_token)

    required_tech_features = False
    required_criteria = deepcopy(self.required_criteria)
    if CRITERION_TECHNICAL_FEATURES in required_criteria:
        required_tech_features = True
        required_criteria.remove(CRITERION_TECHNICAL_FEATURES)

    # If there are required criteria
    if required_criteria:
        doc = self.mongodb.tenders.get(self.tender_id)
        doc["mainProcurementCategory"] = "services"
        self.mongodb.tenders.save(doc)
        tender_criteria = {
            criterion["classification"]["id"]
            for criterion in doc.get("criteria", "")
            if criterion.get("classification")
        }

        criteria_ids = self.required_criteria
        test_criteria = deepcopy(test_criteria_all)
        test_criteria = get_criteria_by_ids(test_criteria, criteria_ids)
        set_tender_criteria(test_criteria, tender.get("lots", []), tender.get("items", []))

        # Try to activate without criteria
        response = self.app.patch_json(
            request_path,
            {"data": {"status": self.primary_tender_status}},
            status=403,
        )

        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("errors", response.json)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': (
                        f"Tender must contain all required criteria: "
                        f"{', '.join(sorted(self.required_criteria - tender_criteria))}"
                    ),
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

        # Add required criteria (except one)
        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_criteria[:-1]},
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc = self.mongodb.tenders.get(self.tender_id)
        tender_criteria = {
            criterion["classification"]["id"]
            for criterion in doc.get("criteria", "")
            if criterion.get("classification")
        }

        # Try to activate once again (still not all required criteria)
        response = self.app.patch_json(
            request_path,
            {"data": {"status": self.primary_tender_status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("errors", response.json)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': (
                        f"Tender must contain all required criteria: "
                        f"{', '.join(sorted(self.required_criteria - tender_criteria))}"
                    ),
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

        # Try to add already added criteria
        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_criteria[:1]},
            status=403,
        )

        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': 'Criteria are not unique',
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

        doc = self.mongodb.tenders.get(self.tender_id)
        tender_criteria = {
            criterion["classification"]["id"]
            for criterion in doc.get("criteria", "")
            if criterion.get("classification")
        }

        response = self.app.patch_json(
            request_path,
            {"data": {"status": self.primary_tender_status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("errors", response.json)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': (
                        f"Tender must contain all required criteria: "
                        f"{', '.join(sorted(self.required_criteria - tender_criteria))}"
                    ),
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

        # Add missing required criteria
        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_criteria[-1:]},
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    article_16_criteria_required = getattr(self, "article_16_criteria_required", False)
    if article_16_criteria_required:

        response = self.app.patch_json(
            request_path,
            {"data": {"status": self.primary_tender_status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("errors", response.json)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': (f"Tender must contain one of article 16 criteria: {', '.join(sorted(ARTICLE_16))}"),
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

        test_criteria_article_16 = test_article_16_criteria[:1]
        set_tender_criteria(test_criteria_article_16, tender.get("lots", []), tender.get("items", []))
        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_criteria_article_16},
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    if required_tech_features:
        response = self.app.patch_json(
            request_path,
            {"data": {"status": self.primary_tender_status}},
            status=403,
        )
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Tender must contain all profile or category criteria: CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES",
                }
            ],
        )

        criteria_ids = self.required_criteria
        test_criteria = deepcopy(test_tech_feature_criteria)
        test_criteria = get_criteria_by_ids(test_criteria, criteria_ids)
        set_tender_criteria(test_criteria, tender.get("lots", []), tender.get("items", []))

        # Add missing required criteria
        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_criteria},
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        request_path,
        {"data": {"status": self.primary_tender_status}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], self.primary_tender_status)
    self.assertEqual(
        len(response.json["data"].get("criteria", [])),
        len(self.required_criteria) + (1 if article_16_criteria_required else 0),
    )


def create_criteria_rg(self):
    request_path = "/tenders/{}/criteria/{}/requirement_groups?acc_token={}".format(
        self.tender_id, self.criteria_id, self.tender_token
    )

    for req in test_requirement_groups[0]["requirements"]:
        req["expectedValue"] = True
    response = self.app.post_json(request_path, {"data": test_requirement_groups[0]})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    rg = response.json["data"]

    self.assertEqual("Підтверджується, що", rg["description"])
    self.assertIn("requirements", rg)
    for requirement in rg["requirements"]:
        self.assertEqual("boolean", requirement["dataType"])
        self.assertEqual(True, requirement["expectedValue"])


def patch_criteria_rg(self):
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))

    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.tender_token
    )

    updated_fields = {
        "description": "Оновлений опис",
        "description_en": "Updated requirement description",
    }

    response = self.app.patch_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}?acc_token={}".format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, self.tender_token
        ),
        {"data": updated_fields},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Can't update exclusion ecriteria objects",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    response = self.app.patch_json(request_path, {"data": updated_fields})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_rg = response.json["data"]

    for k, v in updated_fields.items():
        self.assertIn(k, updated_rg)
        self.assertEqual(updated_rg[k], v)


def get_criteria_rg(self):
    requirement_group_data = deepcopy(test_requirement_groups[0])

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups?acc_token={}".format(
            self.tender_id, self.criteria_id, self.tender_token
        ),
    )
    rgs = response.json["data"]
    rgs_count = len(rgs)

    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups?acc_token={}".format(
            self.tender_id, self.criteria_id, self.tender_token
        ),
        {"data": requirement_group_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rg_id = response.json["data"]["id"]
    rgs_count += 1

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups?acc_token={}".format(
            self.tender_id, self.criteria_id, self.tender_token
        ),
    )
    rgs = response.json["data"]
    self.assertEqual(len(rgs), rgs_count)
    self.assertIn("requirements", rgs[-1])

    del requirement_group_data["requirements"]

    for k, v in requirement_group_data.items():
        self.assertEqual(rgs[-1][k], v)

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}?acc_token={}".format(
            self.tender_id, self.criteria_id, rg_id, self.tender_token
        ),
    )
    rg = response.json["data"]
    for k, v in requirement_group_data.items():
        self.assertEqual(rg[k], v)


def create_rg_requirement_valid(self):
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.tender_token
    )

    response = self.app.post_json(request_path, {"data": self.test_requirement_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    requirement = response.json["data"]

    self.assertEqual(requirement["title"], self.test_requirement_data["title"])
    self.assertEqual(requirement["description"], self.test_requirement_data["description"])
    self.assertEqual(requirement["dataType"], self.test_requirement_data["dataType"])
    self.assertEqual(requirement["expectedValue"], self.test_requirement_data["expectedValue"])

    requirement_data = deepcopy(self.test_requirement_data)
    requirement_data["id"] = requirement["id"]


def create_rg_requirement_invalid(self):
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.tender_token
    )

    exclusion_request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
        self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, self.tender_token
    )

    requirement_data = deepcopy(self.test_requirement_data)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_type = response.json["data"]["procurementMethodType"]
    if tender_type not in ("belowThreshold", "closeFrameworkAgreementSelectionUA", "requestForProposal"):
        response = self.app.post_json(exclusion_request_path, {"data": requirement_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': "Can't update exclusion ecriteria objects",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

    requirement_data["dataType"] = "string"
    requirement_data["minValue"] = 2
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "minValue",
                "description": [
                    "minValue must be integer or number",
                ],
            },
            {
                "location": "body",
                "name": "expectedValue",
                "description": [
                    "expectedValue conflicts with ['minValue', 'maxValue', 'expectedValues']",
                ],
            },
        ],
    )

    del requirement_data["minValue"]
    del requirement_data["expectedValue"]
    requirement_data["maxValue"] = "sdasas"
    requirement_data["dataType"] = "integer"

    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Value 'sdasas' is not int."],
                "location": "body",
                "name": "maxValue",
            },
        ],
    )

    del requirement_data["maxValue"]
    requirement_data["expectedValue"] = "some text"
    requirement_data["dataType"] = "number"
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Number 'some text' failed to convert to a decimal."],
                "location": "body",
                "name": "expectedValue",
            }
        ],
    )

    requirement_data.update({"expectedValue": 10, "dataType": "number", "relatedFeature": "0" * 32})
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["relatedFeature should be one of features"],
                "location": "body",
                "name": "relatedFeature",
            }
        ],
    )


def validate_rg_requirement_strict_rules(self):
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.tender_token
    )

    # BOOLEAN
    requirement_data = {
        "title": "Характеристика Так/Ні",
        "description": "?",
        "dataType": "boolean",
        "expectedValues": [True, False],
    }
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": "only expectedValue is allowed for dataType boolean",
            }
        ],
    )

    del requirement_data["expectedValues"]
    requirement_data["minValue"] = 1
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "minValue", "description": ["minValue must be integer or number"]},
        ],
    )

    del requirement_data["minValue"]
    requirement_data["unit"] = {"code": "HUR", "name": "година"}
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": "unit is forbidden for dataType boolean",
            }
        ],
    )

    # boolean requirement can exist without expectedValue - successful case
    del requirement_data["unit"]
    self.app.post_json(request_path, {"data": requirement_data})

    # STRING
    requirement_data = {
        "title": "Характеристика довідник",
        "description": "?",
        "dataType": "string",
        "expectedValue": "foo",
    }
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": "expectedValues is required when dataType is string",
            }
        ],
    )

    del requirement_data["expectedValue"]
    requirement_data["expectedValues"] = ["Foo", "Bar"]
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": "expectedMinItems is required and should be equal to 1 for dataType string",
            }
        ],
    )

    requirement_data["expectedMinItems"] = 1
    requirement_data["expectedMaxItems"] = 3
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "expectedValues",
                "description": ["expectedMaxItems couldn't be higher then count of items in expectedValues"],
            }
        ],
    )

    requirement_data["expectedValues"] = ["Foo", "Bar", "Bar"]
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": "expectedValues should be unique",
            }
        ],
    )

    requirement_data["expectedMaxItems"] = 2
    requirement_data["expectedValues"] = ["Foo", "Bar"]
    requirement_data["unit"] = {"code": "HUR", "name": "година"}
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": "unit is forbidden for dataType string",
            }
        ],
    )

    del requirement_data["unit"]
    self.app.post_json(request_path, {"data": requirement_data})

    # NUMBER/INTEGER
    for data_type in ("number", "integer"):
        requirement_data = {
            "title": f"Характеристика {data_type}",
            "description": "?",
            "dataType": data_type,
        }
        response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "requirements",
                    "description": f"expectedValue or minValue is required for dataType {data_type}",
                }
            ],
        )

        requirement_data["expectedValues"] = 10
        response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "requirements",
                    "description": "expectedValues is allowed only for dataType string",
                }
            ],
        )

        del requirement_data["expectedValues"]
        requirement_data["expectedValue"] = 1
        requirement_data["maxValue"] = 20
        response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "expectedValue",
                    "description": ["expectedValue conflicts with ['minValue', 'maxValue', 'expectedValues']"],
                }
            ],
        )

        del requirement_data["expectedValue"]
        requirement_data["minValue"] = -10
        requirement_data["maxValue"] = -1
        response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "requirements",
                    "description": f"unit is required for dataType {data_type}",
                }
            ],
        )

        requirement_data["unit"] = {"code": "HUR", "name": "година"}
        self.app.post_json(request_path, {"data": requirement_data})


def validate_rg_requirement_data_schema(self):
    self.set_status("draft")
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.tender_token
    )

    # BOOLEAN
    requirement_data = {
        "title": "Мова",
        "description": "?",
        "dataType": "boolean",
        "expectedValue": True,
        "dataSchema": "ISO 639-3",
    }
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": "dataSchema is allowed only for dataType string",
            }
        ],
    )

    requirement_data = {
        "title": "Мова",
        "description": "?",
        "dataType": "string",
        "expectedMinItems": 1,
        "expectedValues": ["Українська"],
        "dataSchema": "",
    }
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "dataSchema",
                "description": ["Value must be one of ['ISO 639-3', 'ISO 3166-1 alpha-2']."],
            }
        ],
    )

    requirement_data["dataSchema"] = "ISO 639-3"
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": "expectedValues should have ISO 639-3 format and include codes from standards",
            }
        ],
    )

    requirement_data["expectedValues"] = ["eng", "ukr", "fra"]
    response = self.app.post_json(request_path, {"data": requirement_data})
    req_id = response.json["data"]["id"]

    # PATCH
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/criteria/{self.criteria_id}/requirement_groups/{self.rg_id}/requirements/{req_id}?acc_token={self.tender_token}",
        {"data": {"dataSchema": "ISO 3166-1 alpha-2"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirements",
                "description": "expectedValues should have ISO 3166-1 alpha-2 format and include codes from standards",
            }
        ],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/criteria/{self.criteria_id}/requirement_groups/{self.rg_id}/requirements/{req_id}?acc_token={self.tender_token}",
        {"data": {"dataSchema": "ISO 3166-1 alpha-2", "expectedValues": ["UA", "CA", "GB"]}},
    )
    self.assertEqual(response.status, "200 OK")


def patch_rg_requirement(self):
    self.set_status("draft")
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.tender_token
        ),
        {"data": self.test_requirement_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    requirement_id = response.json["data"]["id"]

    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, requirement_id, self.tender_token
    )

    updated_fields = {
        "title": "Updated requirement title",
        "description": "Updated requirement description",
        "expectedValue": False,
        "dataType": "boolean",
    }

    response = self.app.patch_json(request_path, {"data": updated_fields})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_requirement = response.json["data"]

    for k, v in updated_fields.items():
        self.assertIn(k, updated_requirement)
        self.assertEqual(updated_requirement[k], v)


def put_rg_requirement_valid(self):
    put_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"
    get_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements"
    self.set_status("active.tendering")

    # Test put non exclusion criteria
    put_fields = {
        "title": "Фізична особа",
        "expectedValue": False,
    }
    response = self.app.get(get_url.format(self.tender_id, self.criteria_id, self.rg_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.requirement_id = response.json["data"][0]["id"]

    response = self.app.put_json(
        put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
        {"data": put_fields},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "active")
    self.assertEqual(response.json["data"][1]["status"], "cancelled")
    self.assertEqual(set(response.json["data"][1].keys()), {"id", "status", "dateModified", "datePublished"})
    response = self.app.get(get_url.format(self.tender_id, self.criteria_id, self.rg_id))
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "cancelled")
    self.assertIsNotNone(response.json["data"][0]["dateModified"])
    self.assertEqual(response.json["data"][1]["status"], "active")
    self.assertEqual(response.json["data"][1]["id"], self.requirement_id)
    self.assertEqual(response.json["data"][1]["title"], put_fields["title"])
    self.assertEqual(response.json["data"][1]["expectedValue"], put_fields["expectedValue"])
    self.assertIsNone(response.json["data"][1].get("dateModified"))
    self.assertNotEqual(response.json["data"][0]["datePublished"], response.json["data"][1]["datePublished"])

    put_fields = {
        "title": "Фізична особа 2",
        "expectedValue": None,
    }
    response = self.app.get(get_url.format(self.tender_id, self.criteria_id, self.rg_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.requirement_id = response.json["data"][1]["id"]

    response = self.app.put_json(
        put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
        {"data": put_fields},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "active")
    self.assertEqual(response.json["data"][1]["status"], "cancelled")
    self.assertEqual(set(response.json["data"][1].keys()), {"id", "status", "dateModified", "datePublished"})
    response = self.app.get(get_url.format(self.tender_id, self.criteria_id, self.rg_id))
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(response.json["data"][1]["status"], "cancelled")
    self.assertIsNotNone(response.json["data"][1]["dateModified"])
    self.assertEqual(response.json["data"][2]["status"], "active")
    self.assertEqual(response.json["data"][2]["id"], self.requirement_id)
    self.assertEqual(response.json["data"][2]["title"], put_fields["title"])
    self.assertNotIn("expectedValue", response.json["data"][2])
    self.assertIsNone(response.json["data"][2].get("dateModified"))
    self.assertNotEqual(response.json["data"][1]["datePublished"], response.json["data"][2]["datePublished"])

    # Test put exclusion criteria
    response = self.app.get(
        get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, self.tender_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    exc_requirement_id = response.json["data"][1]["id"]

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "active")
    self.assertIsNone(response.json["data"][0].get("eligibleEvidences"))

    put_data = {
        "eligibleEvidences": [
            {
                "description": "Довідка в довільній формі",
                "type": "document",
                "title": "Документальне підтвердження",
                'id': '32cd3841bf59486c85d7fbfa0b756872',
            }
        ]
    }
    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": put_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(response.json["data"][1]["status"], "cancelled")
    self.assertIsNotNone(response.json["data"][1]["dateModified"])
    self.assertEqual(response.json["data"][2]["status"], "active")
    self.assertEqual(response.json["data"][2]["id"], exc_requirement_id)
    self.assertEqual(response.json["data"][2]["title"], response.json["data"][1]["title"])
    self.assertEqual(response.json["data"][2]["expectedValue"], response.json["data"][1]["expectedValue"])
    self.assertIsNone(response.json["data"][2].get("dateModified"))
    self.assertEqual(response.json["data"][2]["eligibleEvidences"], put_data["eligibleEvidences"])

    put_data = {
        "eligibleEvidences": [
            {
                "description": "changed",
                "type": "document",
                "title": "changed",
                'id': '32cd3841bf59486c85d7fbfa0b756872',
            },
            {
                "description": "Довідка в довільній формі",
                "type": "document",
                "title": "Документальне підтвердження",
                'id': '32cd3841bf59486c85d7fbfa0b756845',
            },
        ]
    }
    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": put_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(response.json["data"][-1]["eligibleEvidences"], put_data["eligibleEvidences"])

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {"eligibleEvidences": []}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertIsNone(response.json["data"][-1].get("eligibleEvidences"))

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 5)
    self.assertEqual(response.json["data"][3]["status"], "cancelled")

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {"status": "active", "eligibleEvidences": []}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 6)
    self.assertEqual(response.json["data"][4]["status"], "cancelled")
    self.assertEqual(response.json["data"][5]["status"], "active")
    self.assertNotEqual(response.json["data"][5]["datePublished"], response.json["data"][4]["datePublished"])
    self.assertIsNone(response.json["data"][5].get("dateModified"))
    # self.assertIsNone(response.json["data"][3].get("eligibleEvidences"))

    # put_exclusion_ignore_data = {
    #     "title": "111",
    #     "title_en": "",
    #     "title_ru": "",
    #     "description": "",
    #     "description_en": "",
    #     "description_ru": "",
    #     "dataType": "string",
    #     "minValue": "",
    #     "maxValue": "",
    #     "period": {
    #         "maxExtendDate": "2030-10-22T11:14:18.511585+03:00",
    #         "durationInDays": 1,
    #         "duration": "days"
    #     },
    #     "expectedValue": "",
    #     "datePublished": "2020-10-22T11:14:18.511585+03:00",
    #     "dateModified": "2020-10-22T11:14:18.511585+03:00",
    # }
    #
    # response = self.app.put_json(
    #     put_url.format(
    #         self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
    #     ),
    #     {"data": put_exclusion_ignore_data},
    # )
    # self.assertEqual(response.status, "200 OK")
    # self.assertEqual(response.content_type, "application/json")
    # response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    # self.assertEqual(len(response.json["data"]), 4)
    # for field in put_exclusion_ignore_data:
    #     self.assertNotEqual(put_exclusion_ignore_data.get(field), response.json["data"][4].get(field))


@patch(
    "openprocurement.tender.core.procedure.criteria.get_tender_profile",
    Mock(return_value={"id": "test", "status": "active"}),
)
def put_rg_requirement_valid_value_change(self):
    post_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}"
    put_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"

    for classification_id in ("CRITERION.OTHER", CRITERION_TECHNICAL_FEATURES):

        doc = self.mongodb.tenders.get(self.tender_id)

        if classification_id == CRITERION_TECHNICAL_FEATURES:
            items = doc["items"]
            tech_item = items[0].copy()
            tech_item["id"] = uuid4().hex
            tech_item["profile"] = "1" * 32
            tech_item["category"] = "1" * 32

            items.append(tech_item)

        for criterion in doc.get("criteria", []):
            if criterion["id"] == self.criteria_id:
                criterion["classification"]["id"] = classification_id
                if classification_id == CRITERION_TECHNICAL_FEATURES:
                    criterion["relatedItem"] = tech_item["id"]

        self.mongodb.tenders.save(doc)

        for field in ("minValue", "maxValue", "expectedValue"):

            # 0 -> 1

            test_requirement_data = {
                "title": f"Фізична особа, яка є учасником процедури закупівлі {classification_id} {field}",
                "description": "?",
                "dataType": "integer",
                "unit": {"code": "H87", "name": "штук"},
                field: 0,
            }
            if field == "maxValue":
                test_requirement_data["minValue"] = 0

            response = self.app.post_json(
                post_url.format(self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
                {"data": test_requirement_data},
            )
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.content_type, "application/json")
            requirement_id = response.json["data"]["id"]

            put_fields = {
                field: 1,
            }

            response = self.app.put_json(
                put_url.format(self.tender_id, self.criteria_id, self.rg_id, requirement_id, self.tender_token),
                {"data": put_fields},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")

            # 1 -> 0

            test_requirement_data = {
                "title": f"Фізична особа, яка є учасником процедури закупівлі {classification_id} {field} 2",
                "description": "?",
                "dataType": "integer",
                "unit": {"code": "H87", "name": "штук"},
                field: 1,
            }

            if field == "maxValue":
                test_requirement_data["minValue"] = 0

            response = self.app.post_json(
                post_url.format(self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
                {"data": test_requirement_data},
            )
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.content_type, "application/json")
            requirement_id = response.json["data"]["id"]

            put_fields = {
                field: 0,
            }

            response = self.app.put_json(
                put_url.format(self.tender_id, self.criteria_id, self.rg_id, requirement_id, self.tender_token),
                {"data": put_fields},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")

            # 1 -> None

            test_requirement_data = {
                "title": f"Фізична особа, яка є учасником процедури закупівлі {classification_id} {field} 3",
                "description": "?",
                "dataType": "integer",
                "unit": {"code": "H87", "name": "штук"},
                field: 1,
            }

            if field == "maxValue":
                test_requirement_data["minValue"] = 0

            response = self.app.post_json(
                post_url.format(self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
                {"data": test_requirement_data},
            )
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.content_type, "application/json")
            requirement_id = response.json["data"]["id"]

            put_fields = {
                field: None,
            }

            if classification_id == CRITERION_TECHNICAL_FEATURES:
                response = self.app.put_json(
                    put_url.format(self.tender_id, self.criteria_id, self.rg_id, requirement_id, self.tender_token),
                    {"data": put_fields},
                    status=422,
                )
                self.assertEqual(response.status, "422 Unprocessable Entity")
                self.assertEqual(response.content_type, "application/json")
                self.assertEqual(response.json["status"], "error")
                self.assertEqual(
                    response.json["errors"],
                    [
                        {
                            "location": "body",
                            "name": "data",
                            "description": f"Disallowed remove {field} field and set other value fields.",
                        }
                    ],
                )
            elif field == "maxValue":
                response = self.app.put_json(
                    put_url.format(self.tender_id, self.criteria_id, self.rg_id, requirement_id, self.tender_token),
                    {"data": put_fields},
                )
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.content_type, "application/json")
            else:
                response = self.app.put_json(
                    put_url.format(self.tender_id, self.criteria_id, self.rg_id, requirement_id, self.tender_token),
                    {"data": put_fields},
                    status=422,
                )
                self.assertEqual(response.status, "422 Unprocessable Entity")
                self.assertEqual(response.content_type, "application/json")
                self.assertEqual(response.json["status"], "error")
                self.assertEqual(
                    response.json["errors"],
                    [
                        {
                            "location": "body",
                            "name": "requirements",
                            "description": "expectedValue or minValue is required for dataType integer",
                        }
                    ],
                )


def put_rg_requirement_invalid(self):
    post_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}"
    put_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"
    response = self.app.post_json(
        post_url.format(self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
        {"data": self.test_requirement_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.requirement_id = response.json["data"]["id"]

    put_fields = {
        "title": "Фізична особа",
        "expectedValues": [False, True],
    }

    response = self.app.put_json(
        put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
        {"data": put_fields},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "expectedValue",
                "description": ["expectedValue conflicts with ['minValue', 'maxValue', 'expectedValues']"],
            },
            {
                "location": "body",
                "name": "expectedValues",
                "description": ["expectedValues conflicts with ['minValue', 'maxValue', 'expectedValue']"],
            },
        ],
    )

    with patch(
        "openprocurement.tender.core.procedure.state.criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
        get_now() + timedelta(days=1),
    ):
        response = self.app.put_json(
            put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
            {"data": {"title": "title"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{'description': 'Forbidden', 'location': 'body', 'name': 'data'}],
        )

    with patch(
        "openprocurement.tender.core.procedure.state.criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
        get_now() - timedelta(days=1),
    ):
        self.set_status("active.auction")
        response = self.app.put_json(
            put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
            {"data": {"title": "title"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Can't put object if tender not in {} statuses".format(self.allowed_put_statuses),
                }
            ],
        )


def get_rg_requirement(self):
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.tender_token
        ),
        {"data": self.test_requirement_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    requirement_id = response.json["data"]["id"]

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.tender_token
        ),
    )
    requirements = response.json["data"]
    self.assertEqual(len(requirements), 2)

    for k, v in self.test_requirement_data.items():
        self.assertEqual(requirements[1][k], v)

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, requirement_id, self.tender_token
        ),
    )
    requirement = response.json["data"]
    for k, v in self.test_requirement_data.items():
        self.assertEqual(requirement[k], v)


def create_requirement_evidence_valid(self):
    self.set_status("draft")
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
    )

    response = self.app.post_json(request_path, {"data": self.test_evidence_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence = response.json["data"]

    self.assertEqual(evidence["title"], self.test_evidence_data["title"])
    self.assertEqual(evidence["description"], self.test_evidence_data["description"])
    self.assertEqual(evidence["type"], self.test_evidence_data["type"])


def create_requirement_evidence_invalid(self):
    self.set_status("draft")
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
    )

    evidence_data = deepcopy(self.test_evidence_data)
    evidence_data["type"] = "another_type"
    del evidence_data["title"]

    response = self.app.post_json(request_path, {"data": evidence_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Value must be one of ['document', 'statement']."],
                "location": "body",
                "name": "type",
            },
        ],
    )


def patch_requirement_evidence(self):
    self.set_status("draft")
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
        {"data": self.test_evidence_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences/{}?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, evidence_id, self.tender_token
    )

    updated_fields = {
        "title": "Updated requirement title",
        "description": "Updated requirement description",
        "type": "statement",
    }

    response = self.app.patch_json(request_path, {"data": updated_fields})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_evidence = response.json["data"]

    for k, v in updated_fields.items():
        self.assertIn(k, updated_evidence)
        self.assertEqual(updated_evidence[k], v)


def create_patch_delete_evidences_from_requirement(self):
    self.set_status("draft")
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
        self.tender_id,
        self.exclusion_criteria_id,
        self.exclusion_rg_id,
        self.exclusion_requirement_id,
        self.tender_token,
    )
    # add
    response = self.app.patch_json(
        request_path,
        {"data": {"expectedValue": 100, "eligibleEvidences": [self.test_evidence_data, self.test_evidence_data]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "expectedValue", "description": "Rogue field"},
        ],
    )

    response = self.app.patch_json(
        request_path, {"data": {"eligibleEvidences": [self.test_evidence_data, self.test_evidence_data]}}
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["title"], "Changed title")
    self.assertNotEqual("expectedValue", "100")
    evidences = response.json["data"]["eligibleEvidences"]
    self.assertEqual(len(evidences), 2)

    # add third
    response = self.app.patch_json(
        request_path, {"data": {"eligibleEvidences": [evidences[0], evidences[1], self.test_evidence_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidences = response.json["data"]["eligibleEvidences"]
    self.assertEqual(len(evidences), 3)

    # patch first and third

    evidences[0]["title"] = "Evidence 1"
    evidences[2]["title"] = "Evidence 3"

    response = self.app.patch_json(request_path, {"data": {"eligibleEvidences": evidences}})

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidences = response.json["data"]["eligibleEvidences"]
    self.assertEqual(evidences[0]["title"], "Evidence 1")
    self.assertEqual(evidences[1]["title"], "Документальне підтвердження")
    self.assertEqual(evidences[2]["title"], "Evidence 3")

    # delete second

    response = self.app.patch_json(request_path, {"data": {"eligibleEvidences": [evidences[0], evidences[2]]}})

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidences = response.json["data"]["eligibleEvidences"]
    self.assertEqual(evidences[0]["title"], "Evidence 1")
    self.assertEqual(evidences[1]["title"], "Evidence 3")


def delete_requirement_evidence(self):
    self.set_status("draft")
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
        {"data": self.test_evidence_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    base_request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences".format(
        self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, evidence_id, self.tender_token
    )

    response = self.app.delete("{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token))

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
        {"data": self.test_evidence_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    self.set_status("active.tendering")

    with patch(
        "openprocurement.tender.core.procedure.state.criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
        get_now() - timedelta(days=1),
    ):
        response = self.app.delete(
            "{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': "Can't delete object if tender not in "
                    "['draft', 'draft.pending', 'draft.stage2'] statuses",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

    self.set_status("active.auction")
    with patch(
        "openprocurement.tender.core.procedure.state.criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
        get_now() + timedelta(days=1),
    ):
        response = self.app.delete(
            "{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': "Can't delete object if tender not in "
                    "['draft', 'draft.pending', 'draft.stage2', 'active.tendering'] statuses",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

    with patch(
        "openprocurement.tender.core.procedure.state.criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
        get_now() - timedelta(days=1),
    ):
        response = self.app.delete(
            "{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': "Can't delete object if tender not in "
                    "['draft', 'draft.pending', 'draft.stage2'] statuses",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )


def get_requirement_evidence(self):
    self.set_status("draft")
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
        {"data": self.test_evidence_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    evidences = response.json["data"]

    self.assertEqual(len(evidences), 1)
    for k, v in self.test_evidence_data.items():
        self.assertEqual(evidences[0][k], v)

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences/{}?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, evidence_id, self.tender_token
        ),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidence = response.json["data"]

    for k, v in self.test_evidence_data.items():
        self.assertEqual(evidence[k], v)


def validate_requirement_evidence_document(self):
    self.set_status("draft")
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token
        ),
        {"data": self.test_evidence_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences/{}?acc_token={}"
    response = self.app.patch_json(
        url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, evidence_id, self.tender_token),
        {"data": {"relatedDocument": {"id": "", "title": "Any Document"}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': ['relatedDocument.id should be one of tender documents'],
                'location': 'body',
                'name': 'relatedDocument',
            }
        ],
    )


def lcc_criterion_valid(self):
    # create lcc tender draft
    data = deepcopy(self.initial_data)
    data["awardCriteria"] = "lifeCycleCost"
    data["status"] = "draft"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.assertEqual(tender["awardCriteria"], data["awardCriteria"])
    self.tender_token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # add mandatory criteria
    add_criteria(self)

    # post lcc criteria 1 item
    lcc_criteria = deepcopy(test_lcc_tender_criteria)
    for criterion in lcc_criteria:
        criterion["relatesTo"] = "lot"
        criterion["relatedItem"] = tender["lots"][0]["id"]
    criteria_request_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)
    response = self.app.post_json(criteria_request_path, {"data": [lcc_criteria[0]]}, status=201)

    # patch tender to active.tendering
    self.add_sign_doc(self.tender_id, self.tender_token)
    tender_request_path = "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)
    response = self.app.patch_json(tender_request_path, {"data": {"status": "active.tendering"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # post lcc criteria 3 items
    response = self.app.post_json(criteria_request_path, {"data": lcc_criteria[1:4]}, status=201)
    criteria_id = response.json["data"][0]["id"]
    requirement_group_id = response.json["data"][0]["requirementGroups"][0]["id"]
    requirement_id = response.json["data"][0]["requirementGroups"][0]["requirements"][0]["id"]

    # patch lcc criteria:rgs:r:status = cancelled
    requirement_request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
        self.tender_id,
        criteria_id,
        requirement_group_id,
        requirement_id,
        self.tender_token,
    )
    response = self.app.patch_json(requirement_request_path, {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # post criteria:rgs:r:evidence {data}
    evidences_request_path = (
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id,
            criteria_id,
            requirement_group_id,
            requirement_id,
            self.tender_token,
        )
    )
    evidence_data = {
        "description": "Довідка в довільній формі",
        "type": "document",
        "title": "Документальне підтвердження",
    }
    response = self.app.post_json(evidences_request_path, {"data": evidence_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["description"], evidence_data["description"])
    self.assertEqual(response.json["data"]["type"], evidence_data["type"])
    self.assertEqual(response.json["data"]["title"], evidence_data["title"])
    evidence_id = response.json["data"]["id"]

    # patch criteria:rgs:r:evidence {data}
    evidence_request_path = (
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences/{}?acc_token={}".format(
            self.tender_id,
            criteria_id,
            requirement_group_id,
            requirement_id,
            evidence_id,
            self.tender_token,
        )
    )
    new_evidence_data = {
        "description": "new description",
        "type": "statement",
        "title": "new_title",
    }
    response = self.app.patch_json(evidence_request_path, {"data": new_evidence_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["description"], new_evidence_data["description"])
    self.assertEqual(response.json["data"]["type"], new_evidence_data["type"])
    self.assertEqual(response.json["data"]["title"], new_evidence_data["title"])


def lcc_criterion_invalid(self):
    # create lcc tender draft
    data = deepcopy(self.initial_data)
    data["awardCriteria"] = "lifeCycleCost"
    data["status"] = "draft"
    data.pop("lots", None)
    for milestone in data["milestones"]:
        milestone.pop("relatedLot", None)
    data["items"][0].pop("relatedLot", None)
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_token = response.json["access"]["token"]
    self.tender_id = tender["id"]
    item_id = tender["items"][0]["id"]

    # post lcc criteria 1 item
    for restricted_relatesTo_choice in ["item", "tenderer"]:
        lcc_criteria = deepcopy(test_lcc_tender_criteria)
        lcc_criteria[0]["relatesTo"] = restricted_relatesTo_choice
        if restricted_relatesTo_choice == "item":
            lcc_criteria[0]["relatedItem"] = item_id

        criteria_request_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)

        response = self.app.post_json(criteria_request_path, {"data": [lcc_criteria[0]]}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "relatesTo",
                    "description": [
                        "{} criteria relatesTo should be `tender` if tender has no lots".format(
                            lcc_criteria[0]["classification"]["id"]
                        )
                    ],
                }
            ],
        )

    # create lcc tender draft with lots
    data = deepcopy(self.initial_data)
    data["awardCriteria"] = "lifeCycleCost"
    data["status"] = "draft"
    data["lots"] = self.initial_lots
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_token = response.json["access"]["token"]
    self.tender_id = tender["id"]
    item_id = tender["items"][0]["id"]

    # post lcc criteria 1 item
    for restricted_relatesTo_choice in ["tender", "item", "tenderer"]:
        lcc_criteria = deepcopy(lcc_criteria)
        lcc_criteria[0]["relatesTo"] = restricted_relatesTo_choice
        if restricted_relatesTo_choice == "item":
            lcc_criteria[0]["relatedItem"] = item_id

        criteria_request_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)

        response = self.app.post_json(criteria_request_path, {"data": [lcc_criteria[0]]}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "relatesTo",
                    "description": [
                        "{} criteria relatesTo should be `lot` if tender has lots".format(
                            lcc_criteria[0]["classification"]["id"],
                        )
                    ],
                }
            ],
        )


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_category",
    Mock(return_value={"id": "1" * 32, "criteria": []}),
)
@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
    Mock(return_value={"id": "1" * 32, "relatedCategory": "1" * 32, "criteria": []}),
)
@patch(
    "openprocurement.tender.core.procedure.criteria.get_tender_category",
    Mock(return_value={"id": "1" * 32, "criteria": []}),
)
@patch(
    "openprocurement.tender.core.procedure.criteria.get_tender_profile",
    Mock(return_value={"id": "1" * 32, "relatedCategory": "1" * 32, "criteria": []}),
)
def tech_feature_criterion(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    items = tender["items"]
    tech_item = items[0].copy()
    tech_item["profile"] = "1" * 32
    tech_item["category"] = "1" * 32

    del tech_item["id"]
    items.append(tech_item)

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    items = response.json["data"]["items"]

    criteria_data = deepcopy(test_tech_feature_criteria)
    set_tender_criteria(criteria_data, tender["lots"], items)
    criteria_data[0]["relatedItem"] = items[0]["id"]

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
        {"data": criteria_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "For technical feature criteria item should have category or profile",
            }
        ],
    )

    criteria_data[0]["relatedItem"] = items[1]["id"]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
        {"data": criteria_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    criterion_id = response.json["data"][0]["id"]

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/criteria/{criterion_id}?acc_token={self.tender_token}",
        {"data": {"relatedItem": items[0]["id"]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "For technical feature criteria item should have category or profile",
            },
        ],
    )

    items[1]["category"] = None
    items[1]["profile"] = None
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.assertNotIn("category", response.json["data"]["items"][1])
    self.assertNotIn("profile", response.json["data"]["items"][1])
    criterion_req = response.json["data"]["criteria"][0]["requirementGroups"][0]["requirements"][0]
    self.assertEqual(criterion_req["status"], "cancelled")


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_category",
    Mock(return_value={"id": "0" * 32, "criteria": []}),
)
@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
    Mock(return_value={"id": "1" * 32, "relatedCategory": "0" * 32, "criteria": []}),
)
def criterion_from_market_profile(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    items = tender["items"]
    tech_item = items[0].copy()
    tech_item["profile"] = "1" * 32
    tech_item["category"] = "0" * 32

    del tech_item["id"]
    items.append(tech_item)

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    items = response.json["data"]["items"]

    criteria_data = deepcopy(test_tech_feature_criteria)
    set_tender_criteria(criteria_data, tender["lots"], items)
    criteria_data[0]["relatedItem"] = items[1]["id"]
    criteria_data[0]["requirementGroups"][0]["requirements"] = [
        {
            "title": "Діагонaль екрану",
            "dataType": "integer",
            "expectedValue": 15,
            "unit": {"code": "INH", "name": "дюйм"},
        }
    ]

    market_tech_feature = deepcopy(test_tech_feature_criteria)
    market_tech_feature[0]["requirementGroups"] = [
        {
            "description": "Діагоніль екрану",
            "requirements": [
                {
                    "title": "Діагонaль екрану",
                    "dataType": "integer",
                    "expectedValue": 10,
                    "unit": {"code": "INH", "name": "дюйм"},
                }
            ],
        }
    ]

    with patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_category",
        Mock(return_value={"id": "0" * 32, "criteria": []}),
    ), patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_profile",
        Mock(return_value={"id": "1" * 32, "relatedCategory": "0" * 32, "criteria": market_tech_feature}),
    ):
        # expectedValue in profile requirements != expectedValue in tender requirement
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'expectedValue' for 'Діагонaль екрану' should be equal "
                    "in tender and market requirement",
                },
            ],
        )

    market_tech_feature[0]["requirementGroups"] = [
        {
            "description": "Діагоніль екрану",
            "requirements": [
                {
                    "title": "Діагонaль",
                    "dataType": "integer",
                    "expectedValue": 15,
                    "unit": {"code": "INH", "name": "дюйм"},
                }
            ],
        }
    ]

    with patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_category",
        Mock(return_value={"id": "0" * 32, "criteria": []}),
    ), patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_profile",
        Mock(return_value={"id": "1" * 32, "relatedCategory": "0" * 32, "criteria": market_tech_feature}),
    ):
        # title in profile requirements != title in tender requirement
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "For criterion CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES "
                    "there are requirements that don't exist in profile or archived: {'Діагонaль екрану'}",
                },
            ],
        )

        # dataType in profile requirements != dataType in tender requirement
        criteria_data[0]["requirementGroups"][0]["requirements"][0]["title"] = "Діагонaль"
        criteria_data[0]["requirementGroups"][0]["requirements"][0]["dataType"] = "number"

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'dataType' for 'Діагонaль' should be equal in tender and market requirement",
                },
            ],
        )

        # no expectedValue in tender requirement
        criteria_data[0]["requirementGroups"][0]["requirements"][0]["dataType"] = "integer"
        del criteria_data[0]["requirementGroups"][0]["requirements"][0]["expectedValue"]
        criteria_data[0]["requirementGroups"][0]["requirements"][0]["minValue"] = 0

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'expectedValue' for 'Діагонaль' should be equal in tender and market requirement",
                },
            ],
        )

    del criteria_data[0]["requirementGroups"][0]["requirements"][0]["minValue"]
    criteria_data[0]["requirementGroups"][0]["requirements"][0]["expectedValue"] = 15
    market_tech_feature[0]["requirementGroups"][0]["requirements"].append(
        {
            "title": "Req 2",
            "dataType": "string",
            "expectedValues": ["value1", "value2"],
            "expectedMinItems": 1,
            "expectedMaxItems": 2,
        }
    )

    with patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_category",
        Mock(return_value={"id": "0" * 32, "criteria": []}),
    ), patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_profile",
        Mock(return_value={"id": "1" * 32, "relatedCategory": "0" * 32, "criteria": market_tech_feature}),
    ):
        # title in profile requirements != title in tender requirement
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Criterion CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES lacks requirements from profile {'Req 2'}",
                },
            ],
        )

        # no expectedValue in tender requirement
        criteria_data[0]["requirementGroups"][0]["requirements"].append(
            {
                "title": "Req 2",
                "dataType": "string",
                "expectedValues": ["value2", "value1", "value3"],
                "expectedMinItems": 1,
                "expectedMaxItems": 2,
            }
        )

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'expectedValues' for 'Req 2' should have the same values in tender and market requirement",
                },
            ],
        )

        criteria_data[0]["requirementGroups"][0]["requirements"][1]["expectedValues"] = ["value1", "value2"]
        criteria_data[0]["requirementGroups"][0]["requirements"][1]["expectedMaxItems"] = 1
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'expectedMaxItems' for 'Req 2' should be equal in tender and market requirement",
                },
            ],
        )

        criteria_data[0]["requirementGroups"][0]["requirements"][1]["expectedMaxItems"] = 2
        criteria_data[0]["requirementGroups"][0]["requirements"].append(
            {
                "title": "Req 3",
                "dataType": "number",
                "minValue": 1,
                "unit": {"code": "INH", "name": "дюйм"},
            }
        )
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "For criterion CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES there are "
                    "requirements that don't exist in profile or archived: {'Req 3'}",
                },
            ],
        )
        criteria_data[0]["requirementGroups"][0]["requirements"] = criteria_data[0]["requirementGroups"][0][
            "requirements"
        ][:-1]
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
        )
        criterion_id = response.json["data"][0]["id"]
        req_group_id = response.json["data"][0]["requirementGroups"][0]["id"]
        req_id = response.json["data"][0]["requirementGroups"][0]["requirements"][-1]["id"]

        # try to patch requirement via requirements endpoint
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/criteria/{criterion_id}/requirement_groups/{req_group_id}/requirements/{req_id}?acc_token={self.tender_token}",
            {"data": {"expectedMaxItems": 1}},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'expectedMaxItems' for 'Req 2' should be equal in tender and market requirement",
                },
            ],
        )

        # try to patch criteria via tender endpoint
        response = self.app.get(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
        )

        tender_criteria = response.json["data"]
        tender_criteria[0]["requirementGroups"][0]["requirements"][-1]["expectedValues"] = ["value 4", "value 5"]
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"criteria": tender_criteria}},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'expectedValues' for 'Req 2' should have the same values in tender and market requirement",
                },
            ],
        )


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_category",
    Mock(return_value={"id": "0" * 32, "criteria": []}),
)
@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
    Mock(return_value={"id": "1" * 32, "relatedCategory": "0" * 32, "criteria": []}),
)
def criterion_from_market_category(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    items = tender["items"]
    tech_item = items[0].copy()
    tech_item["profile"] = "1" * 32
    tech_item["category"] = "0" * 32

    del tech_item["id"]
    items.append(tech_item)

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    items = response.json["data"]["items"]

    criteria_data = deepcopy(test_tech_feature_criteria)
    set_tender_criteria(criteria_data, tender["lots"], items)
    criteria_data[0]["relatedItem"] = items[1]["id"]
    criteria_data[0]["requirementGroups"][0]["requirements"] = [
        {
            "title": "Діагонaль екрану",
            "dataType": "integer",
            "expectedValue": 15,
            "unit": {"code": "INH", "name": "дюйм"},
        }
    ]

    market_tech_feature = deepcopy(test_tech_feature_criteria)
    market_tech_feature[0]["requirementGroups"] = [
        {
            "description": "Діагонaль екрану",
            "requirements": [
                {
                    "title": "Діагонaль",
                    "dataType": "integer",
                    "expectedValue": 15,
                    "unit": {"code": "INH", "name": "дюйм"},
                }
            ],
        }
    ]

    with patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_category",
        Mock(return_value={"id": "0" * 32, "criteria": market_tech_feature}),
    ), patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_profile",
        Mock(return_value={"id": "1" * 32, "relatedCategory": "0" * 32, "criteria": [], "status": "general"}),
    ):
        # title in category requirements != title in tender requirement
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data[0]},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "For criterion CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES "
                    "there are requirements that don't exist in category or archived: {'Діагонaль екрану'}",
                },
            ],
        )

        # dataType in category requirements != dataType in tender requirement
        criteria_data[0]["requirementGroups"][0]["requirements"][0]["title"] = "Діагонaль"
        criteria_data[0]["requirementGroups"][0]["requirements"][0]["dataType"] = "number"

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'dataType' for 'Діагонaль' should be equal in tender and market requirement",
                },
            ],
        )
        criteria_data[0]["requirementGroups"][0]["requirements"][0]["dataType"] = "integer"

    market_tech_feature[0]["requirementGroups"][0]["requirements"].append(
        {
            "title": "Req 2",
            "dataType": "string",
            "expectedValues": ["value1", "value2"],
            "expectedMinItems": 1,
            "expectedMaxItems": 2,
        }
    )

    with patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_category",
        Mock(return_value={"id": "0" * 32, "criteria": market_tech_feature}),
    ), patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_profile",
        Mock(return_value={"id": "1" * 32, "relatedCategory": "0" * 32, "criteria": [], "status": "general"}),
    ):

        # no expectedValue in tender requirement
        criteria_data[0]["requirementGroups"][0]["requirements"].append(
            {
                "title": "Req 2",
                "dataType": "string",
                "expectedValues": ["value1", "value3"],
                "expectedMinItems": 1,
                "expectedMaxItems": 2,
            }
        )

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Requirement 'Req 2' expectedValues should have values from category requirement",
                },
            ],
        )

        criteria_data[0]["requirementGroups"][0]["requirements"][1]["expectedValues"] = ["value1", "value2"]
        criteria_data[0]["requirementGroups"][0]["requirements"][1]["expectedMaxItems"] = 1
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'expectedMaxItems' for 'Req 2' should be equal in tender and market requirement",
                },
            ],
        )

        criteria_data[0]["requirementGroups"][0]["requirements"][1]["expectedMaxItems"] = 2
        criteria_data[0]["requirementGroups"][0]["requirements"].append(
            {
                "title": "Req 3",
                "dataType": "number",
                "minValue": 1,
                "unit": {"code": "INH", "name": "дюйм"},
            }
        )
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "For criterion CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES there are "
                    "requirements that don't exist in category or archived: {'Req 3'}",
                },
            ],
        )

    market_tech_feature[0]["requirementGroups"][0]["requirements"].append(
        {
            "title": "Req 3",
            "dataType": "number",
            "minValue": 0,
            "unit": {"code": "INH", "name": "дюйм"},
        }
    )

    with patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_category",
        Mock(return_value={"id": "0" * 32, "criteria": market_tech_feature}),
    ), patch(
        "openprocurement.tender.core.procedure.criteria.get_tender_profile",
        Mock(return_value={"id": "1" * 32, "relatedCategory": "0" * 32, "criteria": [], "status": "general"}),
    ):
        # not all requirements from category should be in tender
        criteria_data[0]["requirementGroups"][0]["requirements"] = criteria_data[0]["requirementGroups"][0][
            "requirements"
        ][:-1]
        criteria_data[0]["requirementGroups"][0]["requirements"][1]["expectedMinItems"] = 1
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
            {"data": criteria_data},
        )

        # try to patch requirement via requirementGroups endpoint
        criterion_id = response.json["data"][0]["id"]
        req_group_id = response.json["data"][0]["requirementGroups"][0]["id"]
        req_data = {
            "title": "Req 3",
            "dataType": "integer",
            "minValue": 0,
            "unit": {"code": "INH", "name": "дюйм"},
        }

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/criteria/{criterion_id}/requirement_groups/{req_group_id}?acc_token={self.tender_token}",
            {"data": {"requirements": [req_data]}},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'dataType' for 'Req 3' should be equal in tender and market requirement",
                },
            ],
        )

        # try to post new requirement via requirements endpoint
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/criteria/{criterion_id}/requirement_groups/{req_group_id}/requirements?acc_token={self.tender_token}",
            {"data": req_data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Field 'dataType' for 'Req 3' should be equal in tender and market requirement",
                },
            ],
        )

        req_data["dataType"] = "number"
        self.app.post_json(
            f"/tenders/{self.tender_id}/criteria/{criterion_id}/requirement_groups/{req_group_id}/requirements?acc_token={self.tender_token}",
            {"data": req_data},
        )
