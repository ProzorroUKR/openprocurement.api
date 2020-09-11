# -*- coding: utf-8 -*-

from copy import deepcopy
from openprocurement.tender.belowthreshold.tests.base import test_criteria


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
    criteria_data = deepcopy(test_criteria)
    criteria_data[0]["classification"]["id"] = "CRITERION.OTHER"

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}&bulk=true".format(self.tender_id, self.tender_token),
        {"data": criteria_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    criteria_id = response.json["data"][0]["id"]
    criteria_not_editable_id = response.json["data"][1]["id"]

    request_path = "/tenders/{}/criteria/{}?acc_token={}".format(self.tender_id, criteria_id, self.tender_token)

    updated_data = {
        "title": u"Оновлена назва",
        "title_en": u"Updated title",
        "title_ru": u"Обновлённое название",
        "description": u"Оновлений опис",
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
                u"description": [u"This field is required."],
                u"location": u"body",
                u"name": u"relatedItem",
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
                u"description": [u"relatedItem should be one of lots"],
                u"location": u"body",
                u"name": u"relatedItem",
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
                u"description": [u"relatedItem should be one of items"],
                u"location": u"body",
                u"name": u"relatedItem",
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
        "description": u"Оновлений опис",
        "description_en": u"Updated requirement description",
    }

    response = self.app.patch_json(request_path, {"data": updated_fields})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_rg = response.json["data"]

    for k, v in updated_fields.items():
        self.assertIn(k, updated_rg)
        self.assertEqual(updated_rg[k], v)


def delete_requirement_evidence(self):
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

    self.set_status("active.auction")

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
            u'description': u"Can't delete object if tender not in "
                            u"['draft', 'active.enquiries'] statuses",
            u'location': u'body',
            u'name': u'data',
        }]
    )