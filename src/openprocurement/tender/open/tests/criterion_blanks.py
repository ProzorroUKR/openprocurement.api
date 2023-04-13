# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta

import mock

from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_requirement_groups,
    test_language_criteria,
    test_lcc_lot_criteria,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_criteria

def create_tender_criteria_valid(self):

    request_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)
    criteria = deepcopy(test_exclusion_criteria)
    criterion = deepcopy(test_exclusion_criteria)[0]
    criterion["classification"]["id"] = "CRITERION.NO.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION"

    response = self.app.post_json(request_path, {"data": criteria})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response3 = self.app.post_json(request_path, {"data": [criterion, criterion]}, status=403)
    self.assertEqual(response3.status, "403 Forbidden")
    self.assertEqual(response3.content_type, "application/json")
    self.assertEqual(response3.json["status"], "error")
    self.assertEqual(
        response3.json["errors"],
        [{"location": "body", "name": "data", "description": "Criteria are not unique"}]
    )
    response3 = self.app.post_json(request_path, {"data": [criterion]})
    self.assertEqual(response3.status, "201 Created")
    self.assertEqual(response3.content_type, "application/json")
    criterion_id = response3.json["data"][0]["id"]
    criterion_data = response3.json["data"][0]

    response3 = self.app.patch_json(
        "/tenders/{}/criteria/{}?acc_token={}".format(self.tender_id, criterion_id, self.tender_token),
        {"data": {"classification": {**criterion_data["classification"], "id": test_exclusion_criteria[0]["classification"]["id"]}}},
        status=403
    )
    self.assertEqual(response3.status, "403 Forbidden")
    self.assertEqual(response3.content_type, "application/json")
    self.assertEqual(response3.json["status"], "error")
    self.assertEqual(
        response3.json["errors"],
        [{"location": "body", "name": "data", "description": "Criteria are not unique"}]
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
        response2.json["errors"],
        [{"location": "body", "name": "data", "description": "Criteria are not unique"}]
    )

    criteria = response.json["data"][0]
    self.assertEqual("Вчинення злочинів, учинених з корисливих мотивів", criteria["title"])
    self.assertEqual("tenderer", criteria["source"])
    self.assertIn("requirementGroups", criteria)
    for requirementGroup in criteria["requirementGroups"]:
        self.assertIn("requirements", requirementGroup)

    lang_criterion = deepcopy(test_language_criteria)
    response = self.app.post_json(request_path, {"data": lang_criterion})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def create_tender_criteria_invalid(self):

    invalid_criteria = deepcopy(test_exclusion_criteria)
    invalid_criteria[0]["relatesTo"] = "lot"

    request_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)

    response = self.app.post_json(request_path, {"data": []}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Data not available"}]
    )

    response = self.app.post_json(request_path, {"data": ["some text"]}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Data not available"}]
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

    invalid_criteria[0]["relatedItem"] = "0"*32
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
        [{
            'location': 'body',
            'name': 'requirementGroups',
            'description': [{
                'requirements': [
                    {
                        'relatedFeature': ['relatedFeature should be one of features'],
                        'expectedValue': ['Must be either true or false.'],
                    }
                ]
            }]
        }]
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
        [{
            'location': 'body',
            'name': 'requirementGroups',
            'description': [{'requirements': [['expectedValue conflicts with ["minValue", "maxValue"]']]}]
        }],
    )

    lang_criterion = deepcopy(test_language_criteria)
    lang_criterion[0]["requirementGroups"][0]["requirements"][0]["expectedValue"] = False
    response = self.app.post_json(request_path, {"data": lang_criterion}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "requirementGroups",
            "description": [{
                "expectedValue": ["Value must be true"],
            }],
        }],
    )

    lang_criterion[0]["requirementGroups"][0]["requirements"][0]["expectedValue"] = True
    lang_criterion[0]["requirementGroups"][0]["requirements"][0]["dataType"] = "string"
    response = self.app.post_json(request_path, {"data": lang_criterion}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            'location': 'body',
            'name': 'requirementGroups',
            'description': [{
                "dataType": [
                    "dataType must be boolean"
                ]
            }],
        }],
    )

    lang_criterion[0]["requirementGroups"][0]["requirements"][0]["dataType"] = "boolean"
    lang_criterion[0]["requirementGroups"][0]["requirements"][0]["eligibleEvidences"] = [
        {
            "description": "Довідка в довільній формі",
            "type": "document",
            "title": "Документальне підтвердження"
        }
    ]

    response = self.app.post_json(request_path, {"data": lang_criterion}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            'location': 'body',
            'name': 'requirementGroups',
            'description': [{
                "eligibleEvidences": [
                    "This field is forbidden for current criterion"
                ]},
            ],
        }],
    )

    lang_criterion = deepcopy(test_language_criteria)
    del lang_criterion[0]["relatesTo"]
    response = self.app.post_json(request_path, {"data": lang_criterion}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{'location': 'body', 'name': 'relatesTo', 'description': ['This field is required.']}]
    )


def patch_tender_criteria_valid(self):
    criteria_data = deepcopy(test_exclusion_criteria)
    criteria_data[0]["classification"]["id"] = "CRITERION.OTHER"

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": criteria_data}
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
        "classification": {
            **criteria["classification"],
            "id": criteria_data[1]["classification"]["id"]
        },
    }

    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
        status=403
    )
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Criteria are not unique"}]
    )

    updated_data["relatesTo"] = "tender"
    self.app.patch_json(
        request_path,
        {"data": updated_data},
        status=200
    )


def patch_tender_criteria_invalid(self):
    criteria_data = deepcopy(test_exclusion_criteria)
    criteria_data[0]["classification"]["id"] = "CRITERION.OTHER"

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": criteria_data}
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
        status=403
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            'description': "Can't update exclusion ecriteria objects",
            'location': 'body',
            'name': 'data',
        }]
    )

    updated_data["relatesTo"] = "lot"
    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
        status=422
    )

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
    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
        status=422
    )

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

    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
        status=422
    )

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
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_exclusion_criteria}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    criteria_id = response.json["data"][0]["id"]

    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    criteria = response.json["data"]

    self.assertIn("requirementGroups", criteria[0])
    self.assertEqual(
        len(test_exclusion_criteria[0]["requirementGroups"]),
        len(criteria[0]["requirementGroups"])
    )

    for i, criterion in enumerate(criteria):
        for k, v in criterion.items():
            if k not in ["id", "requirementGroups"]:
                self.assertEqual(test_exclusion_criteria[i][k], v)

    response = self.app.get("/tenders/{}/criteria/{}".format(self.tender_id, criteria_id))
    criterion = response.json["data"]

    for k, v in criterion.items():
        if k not in ["id", "requirementGroups"]:
            self.assertEqual(test_exclusion_criteria[0][k], v)


def activate_tender(self):
    request_path = "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)

    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.tendering"}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{'description': "Tender must contain all required `EXCLUSION` criteria: "
                         "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY, "
                         "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION, "
                         "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING, "
                         "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION, "
                         "CRITERION.EXCLUSION.CONVICTIONS.FRAUD, "
                         "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION, "
                         "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION, "
                         "CRITERION.EXCLUSION.NATIONAL.OTHER",
          'location': 'body',
          'name': 'data'}],
    )

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_exclusion_criteria[:8]},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.tendering"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{'description': "Tender must contain all required `EXCLUSION` criteria: "
                         "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY, "
                         "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION, "
                         "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING, "
                         "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION, "
                         "CRITERION.EXCLUSION.CONVICTIONS.FRAUD, "
                         "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION, "
                         "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION, "
                         "CRITERION.EXCLUSION.NATIONAL.OTHER",
          'location': 'body',
          'name': 'data'}],
    )

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_exclusion_criteria[:1]},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.tendering"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{'description': "Tender must contain all required `EXCLUSION` criteria: "
                         "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY, "
                         "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION, "
                         "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING, "
                         "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION, "
                         "CRITERION.EXCLUSION.CONVICTIONS.FRAUD, "
                         "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION, "
                         "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION, "
                         "CRITERION.EXCLUSION.NATIONAL.OTHER",
          'location': 'body',
          'name': 'data'}],
    )

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_exclusion_criteria[8:]},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_language_criteria},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.tendering"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertEqual(len(response.json["data"]["criteria"]), 10)


def create_criteria_rg(self):
    request_path = "/tenders/{}/criteria/{}/requirement_groups?acc_token={}".format(
        self.tender_id, self.criteria_id, self.tender_token)

    response = self.app.post_json(request_path, {"data": test_requirement_groups[0]})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    rg = response.json["data"]

    self.assertEqual("Учасник фізична особа підтверджує, що", rg["description"])
    self.assertIn("requirements", rg)
    for requirement in rg["requirements"]:
        self.assertEqual("boolean", requirement["dataType"])
        self.assertEqual("true", requirement["expectedValue"])


def patch_criteria_rg(self):
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    rg_id = response.json["data"][0]["requirementGroups"][0]["id"]

    criteria_not_editable_id = response.json["data"][1]["id"]
    rg_not_editable_id = response.json["data"][1]["requirementGroups"][0]["id"]

    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}?acc_token={}".format(
        self.tender_id, self.criteria_id, rg_id, self.tender_token)

    updated_fields = {
        "description": "Оновлений опис",
        "description_en": "Updated requirement description",
    }

    response = self.app.patch_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}?acc_token={}".format(
            self.tender_id, criteria_not_editable_id, rg_not_editable_id, self.tender_token),
        {"data": updated_fields},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            'description': "Can't update exclusion ecriteria objects",
            'location': 'body',
            'name': 'data',
        }]
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

    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups?acc_token={}".format(
            self.tender_id, self.criteria_id, self.tender_token),
        {"data": requirement_group_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rg_id = response.json["data"]["id"]

    response = self.app.get("/tenders/{}/criteria/{}/requirement_groups?acc_token={}".format(
        self.tender_id, self.criteria_id, self.tender_token),
    )
    rgs = response.json["data"]
    self.assertEqual(len(rgs), 3)
    self.assertIn("requirements", rgs[2])

    del requirement_group_data["requirements"]

    for k, v in requirement_group_data.items():
        self.assertEqual(rgs[2][k], v)

    response = self.app.get("/tenders/{}/criteria/{}/requirement_groups/{}?acc_token={}".format(
        self.tender_id, self.criteria_id, rg_id, self.tender_token),
    )
    rg = response.json["data"]
    for k, v in requirement_group_data.items():
        self.assertEqual(rg[k], v)


def create_rg_requirement_valid(self):
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.tender_token)

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
        self.tender_id, self.criteria_id, self.rg_id, self.tender_token)

    exclusion_request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
        self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, self.tender_token)

    requirement_data = deepcopy(self.test_requirement_data)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_type = response.json["data"]["procurementMethodType"]
    if tender_type not in ("belowThreshold", "closeFrameworkAgreementSelectionUA"):
        response = self.app.post_json(exclusion_request_path, {"data": requirement_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{
                'description': "Can't update exclusion ecriteria objects",
                'location': 'body',
                'name': 'data',
            }]
        )

    requirement_data["minValue"] = 2
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["minValue must be integer or number"],
                "location": "body",
                "name": "minValue",
            }
        ],
    )

    del requirement_data["minValue"]
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
            {
                'description': ["Value 'true' is not int."],
                'location': 'body',
                'name': 'expectedValue',
            }
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

    requirement_data.update({
        "expectedValue": 10,
        "dataType": "number",
        "relatedFeature": "0"*32
    })
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


def patch_rg_requirement(self):
    self.set_status("draft")
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
        {"data": self.test_requirement_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    requirement_id = response.json["data"]["id"]

    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, requirement_id,  self.tender_token)

    updated_fields = {
        "title": "Updated requirement title",
        "description": "Updated requirement description",
        "expectedValue": "False",
        "dataType": "boolean",
    }

    response = self.app.patch_json(request_path, {"data": updated_fields})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_requirement = response.json["data"]

    for k, v in updated_fields.items():
        self.assertIn(k, updated_requirement)
        self.assertEqual(updated_requirement[k], v)


@mock.patch("openprocurement.tender.core.validation.CRITERION_REQUIREMENT_STATUSES_FROM", get_now() - timedelta(days=1))
@mock.patch("openprocurement.tender.core.models.CRITERION_REQUIREMENT_STATUSES_FROM", get_now() - timedelta(days=1))
def put_rg_requirement_valid(self):
    put_fields = {
        "title": "Фізична особа",
        "expectedValue": "false",
    }
    put_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"
    get_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements"
    self.set_status("active.tendering")

    # Test put non exclusion criteria
    response = self.app.get(get_url.format(self.tender_id, self.criteria_id, self.rg_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.requirement_id = response.json["data"][0]["id"]

    response = self.app.put_json(
        put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
        {"data": put_fields})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "active")
    self.assertEqual(response.json["data"][1]["status"], "cancelled")
    self.assertEqual(
        set(response.json["data"][1].keys()),
        {"id", "status", "dateModified", "datePublished"}
    )
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

    # Test put exclusion criteria
    response = self.app.get(
        get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, self.tender_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    exc_requirement_id = response.json["data"][0]["id"]

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {"status": "active"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 1)
    self.assertEqual(response.json["data"][0]["status"], "active")
    self.assertIsNone(response.json["data"][0].get("eligibleEvidences"))

    put_data = {"eligibleEvidences": [
        {
            "description": "Довідка в довільній формі",
            "type": "document",
            "title": "Документальне підтвердження",
            'id': '32cd3841bf59486c85d7fbfa0b756872'
        }
    ]}
    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": put_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "cancelled")
    self.assertIsNotNone(response.json["data"][0]["dateModified"])
    self.assertEqual(response.json["data"][1]["status"], "active")
    self.assertEqual(response.json["data"][1]["id"], exc_requirement_id)
    self.assertEqual(response.json["data"][1]["title"], response.json["data"][0]["title"])
    self.assertEqual(response.json["data"][1]["expectedValue"], response.json["data"][0]["expectedValue"])
    self.assertIsNone(response.json["data"][1].get("dateModified"))
    self.assertEqual(response.json["data"][1]["eligibleEvidences"], put_data["eligibleEvidences"])

    put_data = {"eligibleEvidences": [
        {
            "description": "changed",
            "type": "document",
            "title": "changed",
            'id': '32cd3841bf59486c85d7fbfa0b756872'
        },
        {
            "description": "Довідка в довільній формі",
            "type": "document",
            "title": "Документальне підтвердження",
            'id': '32cd3841bf59486c85d7fbfa0b756845'
        }
    ]}
    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": put_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(response.json["data"][2]["eligibleEvidences"], put_data["eligibleEvidences"])

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {"eligibleEvidences": []}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertIsNone(response.json["data"][3].get("eligibleEvidences"))

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 4)
    self.assertEqual(response.json["data"][3]["status"], "cancelled")

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {
            "status": "active",
            "eligibleEvidences": []
        }}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 5)
    self.assertEqual(response.json["data"][3]["status"], "cancelled")
    self.assertEqual(response.json["data"][4]["status"], "active")
    self.assertNotEqual(response.json["data"][4]["datePublished"], response.json["data"][3]["datePublished"])
    self.assertIsNone(response.json["data"][4].get("dateModified"))


def put_rg_requirement_invalid(self):
    post_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}"
    put_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"
    response = self.app.post_json(post_url.format(self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
                                  {"data": self.test_requirement_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.requirement_id = response.json["data"]["id"]

    with mock.patch("openprocurement.tender.core.procedure.state."
                    "criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
                    get_now() + timedelta(days=1)):
        response = self.app.put_json(
            put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
            {"data": {"title": "title"}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{'description': 'Forbidden', 'location': 'body', 'name': 'data'}],
        )

    with mock.patch("openprocurement.tender.core.procedure.state."
                    "criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
                    get_now() - timedelta(days=1)):
        self.set_status("active.auction")
        response = self.app.put_json(
            put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
            {"data": {"title": "title"}},
            status=403
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
                    "description": "Can't put object if tender not in {} statuses".format(self.allowed_put_statuses)
                }
            ],
        )


def get_rg_requirement(self):
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
        {"data": self.test_requirement_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    requirement_id = response.json["data"]["id"]

    response = self.app.get("/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
    )
    requirements = response.json["data"]
    self.assertEqual(len(requirements), 2)

    for k, v in self.test_requirement_data.items():
        self.assertEqual(requirements[1][k], v)

    response = self.app.get("/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, requirement_id, self.tender_token),
    )
    requirement = response.json["data"]
    for k, v in self.test_requirement_data.items():
        self.assertEqual(requirement[k], v)


def create_requirement_evidence_valid(self):
    self.set_status("draft")
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token)

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
        self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token)

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
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
        {"data": self.test_evidence_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences/{}?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, evidence_id, self.tender_token)

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
        self.tender_token
    )
    # add
    response = self.app.patch_json(
        request_path,
        {"data": {
            "expectedValue": 100,
            "eligibleEvidences": [self.test_evidence_data, self.test_evidence_data]
        }},
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
                "description": "Rogue field"
            },
        ]
    )

    response = self.app.patch_json(
        request_path,
        {"data": {
            "eligibleEvidences": [self.test_evidence_data, self.test_evidence_data]
        }}
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["title"], "Changed title")
    self.assertNotEqual("expectedValue", "100")
    evidences = response.json["data"]["eligibleEvidences"]
    self.assertEqual(len(evidences), 2)

    # add third
    response = self.app.patch_json(
        request_path,
        {"data": {
            "eligibleEvidences": [evidences[0], evidences[1], self.test_evidence_data]
        }}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidences = response.json["data"]["eligibleEvidences"]
    self.assertEqual(len(evidences), 3)

    # patch first and third

    evidences[0]["title"] = "Evidence 1"
    evidences[2]["title"] = "Evidence 3"

    response = self.app.patch_json(
        request_path,
        {"data": {
            "eligibleEvidences": evidences
        }}
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidences = response.json["data"]["eligibleEvidences"]
    self.assertEqual(evidences[0]["title"], "Evidence 1")
    self.assertEqual(evidences[1]["title"], "Документальне підтвердження")
    self.assertEqual(evidences[2]["title"], "Evidence 3")

    # delete second

    response = self.app.patch_json(
        request_path,
        {"data": {
            "eligibleEvidences": [evidences[0], evidences[2]]
        }}
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidences = response.json["data"]["eligibleEvidences"]
    self.assertEqual(evidences[0]["title"], "Evidence 1")
    self.assertEqual(evidences[1]["title"], "Evidence 3")


def delete_requirement_evidence(self):
    self.set_status("draft")
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
        {"data": self.test_evidence_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    base_request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences".format(
        self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, evidence_id, self.tender_token)

    response = self.app.delete("{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token))

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
        {"data": self.test_evidence_data}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    self.set_status("active.tendering")

    with mock.patch("openprocurement.tender.core.procedure.state."
                    "criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.delete(
            "{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{
                'description': "Can't delete object if tender not in "
                                "['draft', 'draft.pending', 'draft.stage2'] statuses",
                'location': 'body',
                'name': 'data',
            }]
        )

    self.set_status("active.auction")
    with mock.patch("openprocurement.tender.core.procedure.state."
                    "criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
                    get_now() + timedelta(days=1)):
        response = self.app.delete(
            "{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{
                'description': "Can't delete object if tender not in "
                                "['draft', 'draft.pending', 'draft.stage2', 'active.tendering'] statuses",
                'location': 'body',
                'name': 'data',
            }]
        )

    with mock.patch("openprocurement.tender.core.validation.CRITERION_REQUIREMENT_STATUSES_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.delete(
            "{}/{}?acc_token={}".format(base_request_path, evidence_id, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{
                'description': "Can't delete object if tender not in "
                                "['draft', 'draft.pending', 'draft.stage2'] statuses",
                'location': 'body',
                'name': 'data',
            }]
        )


def get_requirement_evidence(self):
    self.set_status("draft")
    response = self.app.post_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
        {"data": self.test_evidence_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    evidences = response.json["data"]

    self.assertEqual(len(evidences), 2)
    for k, v in self.test_evidence_data.items():
        self.assertEqual(evidences[0][k], v)

    response = self.app.get(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences/{}?acc_token={}".format(
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, evidence_id, self.tender_token),
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
            self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
        {"data": self.test_evidence_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences/{}?acc_token={}"
    response = self.app.patch_json(
        url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, evidence_id, self.tender_token),
        {"data": {"relatedDocument": {"id": "", "title": "Any Document"}}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{'description': ['relatedDocument.id should be one of tender documents'],
          'location': 'body', 'name': 'relatedDocument'}],
    )


def lcc_criterion_valid(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["awardCriteria"], "lifeCycleCost")

    # add mandatory criteria
    add_criteria(self)

    # post lcc criteria 1 item
    test_lcc_criteria = deepcopy(test_lcc_lot_criteria)
    set_tender_criteria(
        test_lcc_criteria,
        self.initial_data.get("lots", []),
        self.initial_data.get("items", []),
    )
    criteria_request_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)
    response = self.app.post_json(criteria_request_path, {"data": [test_lcc_criteria[0]]}, status=201)

    # patch tender to active.tendering
    tender_request_path = "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)
    response = self.app.patch_json(
        tender_request_path,
        {"data": {
            "status": "active.tendering"
        }}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # post lcc criteria 3 items
    response = self.app.post_json(criteria_request_path, {"data": test_lcc_criteria[1:4]}, status=201)
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
    response = self.app.patch_json(
        requirement_request_path,
        {"data": {
            "status": "cancelled"
        }}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # post criteria:rgs:r:evidence {data}
    evidences_request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences?acc_token={}".format(
        self.tender_id,
        criteria_id,
        requirement_group_id,
        requirement_id,
        self.tender_token,
    )
    evidence_data = {
        "description": "Довідка в довільній формі",
        "type": "document",
        "title": "Документальне підтвердження",
    }
    response = self.app.post_json(
        evidences_request_path,
        {"data": evidence_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["description"], evidence_data["description"])
    self.assertEqual(response.json["data"]["type"], evidence_data["type"])
    self.assertEqual(response.json["data"]["title"], evidence_data["title"])
    evidence_id = response.json["data"]["id"]

    # patch criteria:rgs:r:evidence {data}
    evidence_request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}/evidences/{}?acc_token={}".format(
        self.tender_id,
        criteria_id,
        requirement_group_id,
        requirement_id,
        evidence_id,
        self.tender_token,
    )
    new_evidence_data = {
        "description": "new description",
        "type": "statement",
        "title": "new_title",
    }
    response = self.app.patch_json(
        evidence_request_path,
        {"data": new_evidence_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["description"], new_evidence_data["description"])
    self.assertEqual(response.json["data"]["type"], new_evidence_data["type"])
    self.assertEqual(response.json["data"]["title"], new_evidence_data["title"])


def lcc_criterion_invalid(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["awardCriteria"], "lifeCycleCost")

    item_id = tender["items"][0]["id"]

    # post lcc criteria 1 item
    for restricted_relatesTo_choice in ["tender", "item", "tenderer"]:
        test_lcc_criteria = deepcopy(test_lcc_lot_criteria)
        test_lcc_criteria[0]["relatesTo"] = restricted_relatesTo_choice
        if restricted_relatesTo_choice == "item":
            test_lcc_criteria[0]["relatedItem"] = item_id

        criteria_request_path = "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token)

        response = self.app.post_json(criteria_request_path, {"data": [test_lcc_criteria[0]]}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{
                "location": "body",
                "name": "relatesTo",
                "description": [
                    "{} criteria relatesTo should be `lot` if tender has lots"
                        .format(
                            test_lcc_criteria[0]["classification"]["id"],
                        )
                ]
            }]
        )
