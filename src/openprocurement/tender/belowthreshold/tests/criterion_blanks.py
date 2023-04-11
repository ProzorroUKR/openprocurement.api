# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import timedelta

import mock

from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import test_exclusion_criteria


def activate_tender(self):
    request_path = "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)

    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.enquiries"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.enquiries")


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
        "relatesTo": "lot",
    }

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

    response = self.app.patch_json(request_path, {"data": updated_fields})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_rg = response.json["data"]

    for k, v in updated_fields.items():
        self.assertIn(k, updated_rg)
        self.assertEqual(updated_rg[k], v)


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

    self.set_status("active.enquiries")

    with mock.patch("openprocurement.tender.belowthreshold.validation.CRITERION_REQUIREMENT_STATUSES_FROM",
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
                                "['draft'] statuses",
                'location': 'body',
                'name': 'data',
            }]
        )

        self.set_status("active.auction")
        with mock.patch("openprocurement.tender.belowthreshold.procedure.state"
                        ".criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
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
                                    "['draft', 'active.enquiries'] statuses",
                    'location': 'body',
                    'name': 'data',
                }]
            )
            with mock.patch("openprocurement.tender.belowthreshold.procedure.state"
                            ".criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
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
                                        "['draft'] statuses",
                        'location': 'body',
                        'name': 'data',
                    }]
                )


def put_rg_requirement_invalid(self):
    post_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}"
    put_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"
    response = self.app.post_json(post_url.format(self.tender_id, self.criteria_id, self.rg_id, self.tender_token),
                                  {"data": self.test_requirement_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.requirement_id = response.json["data"]["id"]

    with mock.patch("openprocurement.tender.belowthreshold.procedure.state."
                    "criterion_rg_requirement.CRITERION_REQUIREMENT_STATUSES_FROM",
                    get_now() + timedelta(days=1)):
        response = self.app.put_json(
            put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
            {"data": {}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{'description': 'Forbidden', 'location': 'body', 'name': 'data'}],
        )

    with mock.patch("openprocurement.tender.belowthreshold.validation.CRITERION_REQUIREMENT_STATUSES_FROM",
                    get_now() - timedelta(days=1)):
        self.set_status("active.auction")
        response = self.app.put_json(
            put_url.format(self.tender_id, self.criteria_id, self.rg_id, self.requirement_id, self.tender_token),
            {"data": {}},
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


@mock.patch("openprocurement.tender.belowthreshold.validation.CRITERION_REQUIREMENT_STATUSES_FROM", get_now() - timedelta(days=1))
@mock.patch("openprocurement.tender.core.models.CRITERION_REQUIREMENT_STATUSES_FROM", get_now() - timedelta(days=1))
def put_rg_requirement_valid(self):
    put_fields = {
        "title": "Фізична особа",
        "expectedValue": "false",
        # "datePublished": "2030-10-22T11:14:18.511585+03:00",
        # "dateModified": "2030-10-22T11:14:18.511585+03:00",
        # "id": "11111111111111111111111111111111",
    }
    put_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"
    get_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements"
    self.set_status("active.enquiries")

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

    response = self.app.get(get_url.format(self.tender_id, self.criteria_id, self.rg_id))
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "cancelled")
    self.assertIsNotNone(response.json["data"][0]["dateModified"])
    self.assertEqual(response.json["data"][1]["status"], "active")
    self.assertEqual(response.json["data"][1]["id"], self.requirement_id)
    self.assertEqual(response.json["data"][1]["title"], put_fields["title"])
    self.assertEqual(response.json["data"][1]["expectedValue"], put_fields["expectedValue"])
    self.assertIsNone(response.json["data"][1].get("dateModified"))

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
        {"data": put_fields})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "cancelled")
    self.assertEqual(response.json["data"][1]["status"], "active")
    self.assertIsNone(response.json["data"][1].get("eligibleEvidences"))

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
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(response.json["data"][1]["status"], "cancelled")
    self.assertIsNotNone(response.json["data"][1]["dateModified"])
    self.assertEqual(response.json["data"][2]["status"], "active")
    self.assertEqual(response.json["data"][2]["id"], exc_requirement_id)
    self.assertEqual(response.json["data"][2]["title"], response.json["data"][1]["title"])
    self.assertEqual(response.json["data"][2]["expectedValue"], response.json["data"][1]["expectedValue"])
    self.assertIsNone(response.json["data"][2].get("dateModified"))
    self.assertEqual(response.json["data"][2]["eligibleEvidences"], put_data["eligibleEvidences"])

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
    self.assertEqual(response.json["data"][3]["eligibleEvidences"], put_data["eligibleEvidences"])

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {"eligibleEvidences": []}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertIsNone(response.json["data"][4].get("eligibleEvidences"))

    response = self.app.put_json(
        put_url.format(
            self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id, exc_requirement_id, self.tender_token
        ),
        {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(get_url.format(self.tender_id, self.exclusion_criteria_id, self.exclusion_rg_id))
    self.assertEqual(len(response.json["data"]), 5)
    self.assertEqual(response.json["data"][0]["status"], "cancelled")
    self.assertEqual(response.json["data"][1]["status"], "cancelled")


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
