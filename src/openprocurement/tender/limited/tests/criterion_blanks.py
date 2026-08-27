from copy import deepcopy

from openprocurement.tender.core.tests.mock import patch_market_product, patch_market_category
from openprocurement.tender.core.tests.base import test_localization_criteria
from openprocurement.tender.core.tests.utils import set_tender_criteria


def tender_criteria_source_validation(self):
    request_path = f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}"

    tender = self.get_tender().json["data"]
    tender_document = self.mongodb.tenders.get(self.tender_id)
    tender_document["items"][0]["category"] = "foo"
    tender_document["items"][0]["product"] = "bar"
    self.mongodb.tenders.save(tender_document)

    criteria = deepcopy(test_localization_criteria)
    set_tender_criteria(
        criteria,
        tender.get("lots", []),
        tender.get("items", []),
    )

    response = self.app.post_json(request_path, {"data": criteria}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "source", "description": ["Value must be one of ['procuringEntity']."]}],
    )

    criteria[0]["source"] = "procuringEntity"

    response = self.app.post_json(request_path, {"data": criteria})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    criterion_id = response.json["data"][0]["id"]

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/criteria/{criterion_id}?acc_token={self.tender_token}",
        {"data": {"source": "winner"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "source", "description": ["Value must be one of ['procuringEntity']."]}],
    )


def patch_criteria_rg(self):
    request_path = f"/tenders/{self.tender_id}/criteria/{self.criteria_id}/requirement_groups/{self.rg_id}?acc_token={self.tender_token}"

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

    with patch_market_product(self.product), patch_market_category(self.category):
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

    put_fields = {
        "title": "Фізична особа",
        "expectedValue": False,
    }
    response = self.app.get(get_url.format(self.tender_id, self.criteria_id, self.rg_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.requirement_id = response.json["data"][0]["id"]

    with patch_market_product(self.product), patch_market_category(self.category):
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

    with patch_market_product(self.product), patch_market_category(self.category):
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
