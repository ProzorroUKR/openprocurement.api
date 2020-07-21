# -*- coding: utf-8 -*-
from datetime import timedelta
from openprocurement.api.utils import get_now


def patch_tender_contract(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

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


def patch_tender_contract_value_vat_not_included(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False, 'amountNet': contract['value']['amount']}}},
    )
    self.assertEqual(response.status, "200 OK")


    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 467}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 22600, "amountNet": 22600}}},
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
