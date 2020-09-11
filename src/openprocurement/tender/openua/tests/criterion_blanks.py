# -*- coding: utf-8 -*-
from copy import deepcopy

from openprocurement.tender.belowthreshold.tests.base import test_criteria, test_requirement_groups


def create_tender_criteria_valid(self):

    request_path = "/tenders/{}/criteria?acc_token={}&bulk=true".format(self.tender_id, self.tender_token)

    response = self.app.post_json(request_path, {"data": test_criteria})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    criteria = response.json["data"][0]
    self.assertEqual(u"Вчинення злочинів, учинених з корисливих мотивів", criteria["title"])
    self.assertEqual("tenderer", criteria["source"])
    self.assertIn("requirementGroups", criteria)
    for requirementGroup in criteria["requirementGroups"]:
        self.assertIn("requirements", requirementGroup)


def create_tender_criteria_invalid(self):

    invalid_criteria = deepcopy(test_criteria)
    invalid_criteria[0]["relatesTo"] = "lot"

    request_path = "/tenders/{}/criteria?acc_token={}&bulk=true".format(self.tender_id, self.tender_token)
    response = self.app.post_json(request_path, {"data": invalid_criteria}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u"relatedItem": [u"This field is required."]},
                u"location": u"body",
                u"name": 0,
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
                u"description": {u"relatedItem": [u"relatedItem should be one of lots"]},
                u"location": u"body",
                u"name": 0,
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
                u"description": {u"relatedItem": [u"relatedItem should be one of items"]},
                u"location": u"body",
                u"name": 0,
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
                u"description": {
                    u'requirementGroups': [
                        {
                            u'requirements': [
                                {
                                    u'expectedValue': [u'Must be either true or false.'],
                                    u'relatedFeature': [u'relatedFeature should be one of features'],
                                }
                            ],
                        }
                    ],
                },
                u"location": u"body",
                u"name": 0,
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
                u"description": {
                    u'requirementGroups': [
                        {u'requirements': [[u'expectedValue conflicts with ["minValue", "maxValue"]']]}
                    ]
                },
                u"location": u"body",
                u"name": 0,
            }
        ],
    )


def patch_tender_criteria_valid(self):
    criteria_data = deepcopy(test_criteria)
    criteria_data[0]["classification"]["id"] = "CRITERION.OTHER"

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}&bulk=true".format(self.tender_id, self.tender_token),
        {"data": criteria_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    criteria_id = response.json["data"][0]["id"]

    request_path = "/tenders/{}/criteria/{}?acc_token={}".format(self.tender_id, criteria_id, self.tender_token)

    updated_data = {
        "title": u"Оновлена назва",
        "title_en": u"Updated title",
        "title_ru": u"Обновлённое название",
        "description": u"Оновлений опис",
        "requirementGroups": [
            {
                "description": "Not added requirementGroup",
            }
        ]
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
    self.assertNotEqual(criteria["requirementGroups"], updated_data["requirementGroups"])
    for rg in criteria["requirementGroups"]:
        self.assertNotEqual(rg["description"], updated_data["requirementGroups"][0]["description"])


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
            u'description': u"Can't update exclusion ecriteria objects",
            u'location': u'body',
            u'name': u'data',
        }]
    )

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


def get_tender_criteria(self):
    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}&bulk=true".format(self.tender_id, self.tender_token),
        {"data": test_criteria}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    criteria_id = response.json["data"][0]["id"]

    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    criteria = response.json["data"]

    self.assertIn("requirementGroups", criteria[0])
    self.assertEqual(
        len(test_criteria[0]["requirementGroups"]),
        len(criteria[0]["requirementGroups"])
    )

    for i, criterion in enumerate(criteria):
        for k, v in criterion.items():
            if k not in ["id", "requirementGroups"]:
                self.assertEqual(test_criteria[i][k], v)

    response = self.app.get("/tenders/{}/criteria/{}".format(self.tender_id, criteria_id))
    criterion = response.json["data"]

    for k, v in criterion.items():
        if k not in ["id", "requirementGroups"]:
            self.assertEqual(test_criteria[0][k], v)


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
        [{u'description': u'Tender must contain all 9 `EXCLUSION` criteria',
          u'location': u'body',
          u'name': u'data'}],
    )

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_criteria[:8]},
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
        [{u'description': u'Tender must contain all 9 `EXCLUSION` criteria',
          u'location': u'body',
          u'name': u'data'}],
    )

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_criteria[:1]},
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
        [{u'description': u'Tender must contain all 9 `EXCLUSION` criteria',
          u'location': u'body',
          u'name': u'data'}],
    )

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_criteria[8:]},
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

    self.assertEqual(u"Учасник фізична особа підтверджує, що", rg["description"])
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
        "description": u"Оновлений опис",
        "description_en": u"Updated requirement description",
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
            u'description': u"Can't update exclusion ecriteria objects",
            u'location': u'body',
            u'name': u'data',
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


def create_rg_requirement_invalid(self):
    request_path = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, self.tender_token)

    requirement_data = deepcopy(self.test_requirement_data)

    # response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    # self.assertEqual(response.status, "422 Unprocessable Entity")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["status"], "error")
    # self.assertEqual(
    #     response.json["errors"],
    #     [
    #         {
    #             u"description": [u"This field is required."],
    #             u"location": u"body",
    #             u"name": u"relatedItem",
    #         }
    #     ],
    # )

    requirement_data["minValue"] = 2
    response = self.app.post_json(request_path, {"data": requirement_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"minValue must be integer or number"],
                u"location": u"body",
                u"name": u"minValue",
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
                u"description": [u"Value 'sdasas' is not int."],
                u"location": u"body",
                u"name": u"maxValue",
            },
            {
                u'description': [u"Value 'true' is not int."],
                u'location': u'body',
                u'name': u'expectedValue',
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
                u"description": [u"Number 'some text' failed to convert to a decimal."],
                u"location": u"body",
                u"name": u"expectedValue",
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
                u"description": [u"relatedFeature should be one of features"],
                u"location": u"body",
                u"name": u"relatedFeature",
            }
        ],
    )


def patch_rg_requirement(self):
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
        "title": u"Updated requirement title",
        "description": u"Updated requirement description",
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
    self.assertEqual(len(requirements), 1)

    for k, v in self.test_requirement_data.items():
        self.assertEqual(requirements[0][k], v)

    response = self.app.get("/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
        self.tender_id, self.criteria_id, self.rg_id, requirement_id, self.tender_token),
    )
    requirement = response.json["data"]
    for k, v in self.test_requirement_data.items():
        self.assertEqual(requirement[k], v)


def create_requirement_evidence_valid(self):
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
                u"description": [u"Value must be one of ['document', 'statement']."],
                u"location": u"body",
                u"name": u"type",
            },
            {
                u"description": [u"This field is required."],
                u"location": u"body",
                u"name": u"title",
            }
        ],
    )


def patch_requirement_evidence(self):

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
        "title": u"Updated requirement title",
        "description": u"Updated requirement description",
        "type": u"statement",
    }

    response = self.app.patch_json(request_path, {"data": updated_fields})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_evidence = response.json["data"]

    for k, v in updated_fields.items():
        self.assertIn(k, updated_evidence)
        if k == "type":
            self.assertNotEqual(updated_evidence[k], v)
        else:
            self.assertEqual(updated_evidence[k], v)


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
                            u"['draft', 'draft.pending', 'draft.stage2', "
                            u"'active.tendering'] statuses",
            u'location': u'body',
            u'name': u'data',
        }]
    )


def get_requirement_evidence(self):
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
