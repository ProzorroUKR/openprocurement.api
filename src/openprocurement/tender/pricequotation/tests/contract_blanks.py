# -*- coding: utf-8 -*-
from datetime import timedelta
from copy import deepcopy
from openprocurement.api.utils import get_now


def create_tender_contract_invalid(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/some_id/contracts",
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    request_path = "/tenders/{}/contracts".format(self.tender_id)

    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Content-Type header should be one of ['application/json']",
                u"location": u"header",
                u"name": u"Content-Type",
            }
        ],
    )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"No JSON object could be decoded", u"location": u"body", u"name": u"data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"awardID": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"awardID should be one of awards"], u"location": u"body", u"name": u"awardID"}],
    )


def create_tender_contract(self):
    self.app.authorization = ("Basic", ("token", ""))
    contract_items = deepcopy(self.award_items)
    for item in contract_items:
        item["quantity"] += 0.5

    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {
            "data": {
                "title": "contract title",
                "description": "contract description",
                "awardID": self.award_id,
                "value": {
                    "amount": self.award_value["amount"],
                    "valueAddedTaxIncluded": self.award_value["valueAddedTaxIncluded"],
                    "currency": self.award_value["currency"],
                    "amountNet": self.award_value["amount"],
                },
                "suppliers": self.award_suppliers,
                "items": contract_items,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.assertIn("id", contract)
    self.assertIn("value", contract)
    self.assertIn("suppliers", contract)
    self.assertIn(contract["id"], response.headers["Location"])
    self.assertEqual(contract["items"], contract_items)

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "terminated"
    self.db.save(tender)

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add contract in current (unsuccessful) tender status"
    )

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (unsuccessful) tender status"
    )


def create_tender_contract_in_complete_status(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.assertIn("id", contract)
    self.assertIn(contract["id"], response.headers["Location"])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "terminated"
    self.db.save(tender)

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add contract in current (complete) tender status"
    )

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )


def patch_tender_contract(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    self.assertEqual(contract["value"]["amount"], contract["value"]["amountNet"])

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("complete", {"status": "active.awarded"})

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amountNet": contract["value"]["amount"] - 1}}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {
            "data": {
                "contractID": "myselfID",
                "items": [{"description": "New Description"}],
                "suppliers": [{"name": "New Name"}],
            }
        },
    )

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.json["data"]["contractID"], contract["contractID"])
    self.assertEqual(response.json["data"]["items"], contract["items"])
    self.assertEqual(response.json["data"]["suppliers"], contract["suppliers"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"dateSigned": one_hour_in_furure}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Contract signature date can't be in the future"],
                u"location": u"body",
                u"name": u"dateSigned",
            }
        ],
    )

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"dateSigned": custom_signature_date}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 232}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"contractID": "myselfID"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"items": [{"description": "New Description"}]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"suppliers": [{"name": "New Name"}]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.patch_json(
        "/tenders/some_id/contracts/some_id?acc_token={}".format(self.tender_token),
        {"data": {"status": "active"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["contractID"], contract["contractID"])
    self.assertEqual(response.json["data"]["items"], contract["items"])
    self.assertEqual(response.json["data"]["suppliers"], contract["suppliers"])
    self.assertEqual(response.json["data"]["dateSigned"], custom_signature_date)


def patch_tender_contract_value(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 501}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount should be less or equal to awarded amount")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 502, "amountNet": 501}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount should be less or equal to awarded amount")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 238}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 100, "amountNet": 80}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 238, "amountNet": 238}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 100, "amountNet": 85}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 100)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 85)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")


def patch_tender_contract_value_vat_not_included(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 468}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 600, "amountNet": 600}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount should be less or equal to awarded amount")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 400, "amountNet": 400}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 400)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": True}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )


def get_tender_contract(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], contract)

    response = self.app.get("/tenders/{}/contracts/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.get("/tenders/some_id/contracts/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def get_tender_contracts(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][-1], contract)

    response = self.app.get("/tenders/some_id/contracts", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )



# TenderContractDocumentResourceTest


def not_found(self):
    response = self.app.post(
        "/tenders/some_id/contracts/some_id/documents?acc_token={}".format(self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.post(
        "/tenders/{}/contracts/some_id/documents?acc_token={}".format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        status=404,
        upload_files=[("invalid_value", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.get("/tenders/some_id/contracts/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get("/tenders/{}/contracts/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.get("/tenders/some_id/contracts/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get("/tenders/{}/contracts/some_id/documents/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/some_id".format(self.tender_id, self.contract_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    response = self.app.put(
        "/tenders/some_id/contracts/some_id/documents/some_id?acc_token={}".format(self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.put(
        "/tenders/{}/contracts/some_id/documents/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/some_id?acc_token={}".format(
            self.tender_id, self.contract_id, self.tender_token
        ),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )


def create_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get("/tenders/{}/contracts/{}/documents?all=true".format(self.tender_id, self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?download=some_id".format(self.tender_id, self.contract_id, doc_id),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
    )

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, "content")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add document in current ({}) tender status".format(
            self.forbidden_contract_document_modification_actions_status
        ),
    )


def put_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content2")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content3")

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document in current ({}) tender status".format(
            self.forbidden_contract_document_modification_actions_status
        ),
    )


def patch_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document in current ({}) tender status".format(
            self.forbidden_contract_document_modification_actions_status
        ),
    )
