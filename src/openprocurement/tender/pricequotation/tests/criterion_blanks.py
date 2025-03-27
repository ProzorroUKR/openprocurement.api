from copy import deepcopy
from datetime import timedelta
from unittest.mock import ANY, patch

from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.utils import set_tender_criteria
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_criteria,
    test_tender_pq_item,
    test_tender_pq_short_profile,
)


def create_tender_criteria_multi_profile(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    items = tender["items"]

    items.append(deepcopy(test_tender_pq_item))
    items[1]["profile"] = "655361-30230000-889652-40000777"

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {
            "data": {"items": items},
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    item_ids = [item["id"] for item in tender["items"]]
    criteria = deepcopy(test_tender_pq_short_profile["criteria"])

    criteria[0]["relatesTo"] = "item"
    criteria[0]["relatedItem"] = "invalid"
    response = self.app.patch_json(
        f"/tenders/{tender['id']}?acc_token={self.tender_token}", {"data": {"criteria": criteria}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"relatedItem": ['Hash value is wrong length.']},
                "location": "body",
                "name": "criteria",
            }
        ],
    )

    criteria[0]["relatesTo"] = "item"
    criteria[0]["relatedItem"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    response = self.app.patch_json(
        f"/tenders/{tender['id']}?acc_token={self.tender_token}", {"data": {"criteria": criteria}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedItem": ['relatedItem should be one of items']}],
                "location": "body",
                "name": "criteria",
            }
        ],
    )

    for i, cr in enumerate(criteria):
        cr["relatesTo"] = "item"
        cr["relatedItem"] = item_ids[i % 2]
    response = self.app.patch_json(
        f"/tenders/{tender['id']}?acc_token={self.tender_token}",
        {"data": {"criteria": criteria}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    expected_criteria = deepcopy(criteria)
    for c in expected_criteria:
        c.update(id=ANY)

        for g in c.get("requirementGroups"):
            g.update(id=ANY)

            for r in g.get("requirements"):
                r.update(id=ANY)
                r.update(status=ANY)
                r.update(datePublished=ANY)

    self.assertEqual(tender["criteria"], expected_criteria)


def create_tender_criteria_invalid(self):
    invalid_criteria = deepcopy(test_tender_pq_criteria)
    invalid_criteria[0]["classification"][
        "id"
    ] = "CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.TECHNICAL.EQUIPMENT"
    invalid_criteria[0]["relatesTo"] = "lot"
    invalid_criteria[0]["requirementGroups"][0]["requirements"][0] = {
        "dataType": "number",
        "id": "a" * 32,
        "minValue": 23.8,
        "title": "Діагональ екрану",
        "unit": {"code": "INH", "name": "дюйм"},
    }

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


def get_tender_criteria(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    test_criteria = deepcopy(test_tender_pq_criteria)
    set_tender_criteria(test_criteria, tender.get("lots", []), tender.get("items", []))

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_criteria}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(f"/tenders/{self.tender_id}/criteria")
    criteria = response.json["data"]

    self.assertIn("requirementGroups", criteria[0])
    self.assertEqual(
        len(criteria[0]["requirementGroups"]),
        len(test_criteria[0]["requirementGroups"]),
    )
    criteria_id = criteria[0]["id"]

    for i, criterion in enumerate(criteria):
        for k, v in criterion.items():
            if k not in ["id", "requirementGroups"]:
                self.assertEqual(test_criteria[i][k], v)

    response = self.app.get(f"/tenders/{self.tender_id}/criteria/{criteria_id}")
    criterion = response.json["data"]

    for k, v in criterion.items():
        if k not in ["id", "requirementGroups"]:
            self.assertEqual(test_criteria[0][k], v)


def put_rg_requirement_valid(self):
    response = self.app.get(f"/tenders/{self.tender_id}/criteria")
    criteria = response.json["data"]
    criteria_id = criteria[0]["id"]
    rg_id = criteria[0]["requirementGroups"][0]["id"]
    req_id = criteria[0]["requirementGroups"][0]["requirements"][0]["id"]

    test_put_data = {"minValue": 1}

    put_url = (
        f"/tenders/{self.tender_id}/criteria/{criteria_id}/requirement_groups/{rg_id}"
        f"/requirements/{req_id}?acc_token={self.tender_token}"
    )

    response = self.app.put_json(put_url, {"data": test_put_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't put object if tender not in ['active.tendering'] statuses",
            }
        ],
    )

    self.set_status("active.tendering")

    response = self.app.put_json(put_url, {"data": test_put_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't put object if tender not in ['draft'] statuses"}],
    )


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
                    'description': "Can't delete object if tender not in " "['draft'] statuses",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )

    self.set_status("active.auction")

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
                    'description': "Can't delete object if tender not in " "['draft'] statuses",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )


def patch_criteria_rg(self):
    response = self.app.get(f"/tenders/{self.tender_id}/criteria")
    criteria = response.json["data"]
    criteria_id = criteria[0]["id"]
    rg_id = criteria[0]["requirementGroups"][0]["id"]

    request_path = (
        f"/tenders/{self.tender_id}/criteria/{criteria_id}" f"/requirement_groups/{rg_id}?acc_token={self.tender_token}"
    )

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
