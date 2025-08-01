from copy import deepcopy
from uuid import uuid4

from openprocurement.contracting.core.procedure.models.change import RATIONALE_TYPES


def not_found(self):
    response = self.app.get("/contracts/some_id/changes", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get(f"/contracts/{self.contract['id']}/changes/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "change_id"}])


def get_change(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "Опис причини змін контракту",
                "rationale_en": "Contract change cause",
                "modifications": {"title": "New title of contract"},
                "rationaleTypes": ["priceReduction"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)

    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(f"/contracts/{self.contract['id']}/changes/{change['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    change_data = response.json["data"]
    self.assertEqual(change_data, change)

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertIn("changes", response.json["data"])
    self.assertEqual(len(response.json["data"]["changes"]), 1)
    self.assertEqual(
        set(response.json["data"]["changes"][0].keys()),
        {"id", "date", "status", "rationaleTypes", "rationale", "rationale_en", "modifications", "author"},
    )

    self.app.authorization = None
    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        {"id", "date", "status", "rationaleTypes", "rationale", "rationale_en", "modifications", "author"},
    )


def create_change(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["qualityImprovement"],
                "modifications": {"title": "New title of contract"},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)

    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "трататата",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"title": "New"},
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't create new contract change while any (pending) change exists",
            }
        ],
    )

    self.activate_change(change['id'])
    response = self.app.get(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "трататата",
                "rationaleTypes": ["non-existing-rationale"],
                "modifications": {"title": "New"},
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "rationaleTypes",
                "description": [[f"Value must be one of {RATIONALE_TYPES}."]],
            }
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "трататата",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"title": "New title of contract"},
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "No changes detected between contract and current modifications",
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "трататата",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"title": "New title 2"},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    change2 = response.json["data"]
    self.assertEqual(change2["status"], "pending")

    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)


def create_change_invalid(self):
    response = self.app.post(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}", "data", status=415
    )
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Content-Type header should be one of ['application/json']",
                "location": "header",
                "name": "Content-Type",
            }
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}", {"data": {}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "rationale", "description": ["This field is required."]},
            {"location": "body", "name": "rationaleTypes", "description": ["This field is required."]},
            {"location": "body", "name": "modifications", "description": ["This field is required."]},
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale": "", "rationaleTypes": ["volumeCuts"], "modifications": {"title": "New title"}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "rationale", "description": ["String value is too short."]}],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale": "причина зміни укр", "rationaleTypes": ["volumeCuts"], "modifications": {}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "modifications", "description": "Contract modifications are empty"}],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationaleTypes": ["volumeCuts"],
                "modifications": {"value": {"currency": "UAH"}},
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "modifications",
                "description": {"value": {"amount": ["This field is required."]}},
            }
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationaleTypes": ["volumeCuts"],
                "modifications": {"value": {"currency": "USD", "amount": 500}},
            }
        },
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "value",
                "description": "Can't update currency for contract value",
            }
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale_ua": ""}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "rationale_ua", "description": "Rogue field"}]
    )
    self.app.authorization = None
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale_ua": "aaa"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes", {"data": {"rationale_ua": "aaa"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.get(f"/contracts/{self.contract['id']}?acc_token={self.contract_token}")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("changes", response.json["data"])


def patch_change(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"title": "New"},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {}},
        status=405,
    )
    self.assertEqual(response.status, "405 Method Not Allowed")


def activation_of_change(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"value": {"amount": 235, "amountNet": 200}},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    change = response.json["data"]

    # add signature for buyer
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    self.app.post_json(
        f"/contracts/{self.contract_id}/changes/{change['id']}/documents?acc_token={self.contract_token}",
        {"data": contract_sign_data},
    )

    response = self.app.get(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    # add signature for supplier
    self.app.post_json(
        f"/contracts/{self.contract_id}/changes/{change['id']}/documents?acc_token={self.bid_token}",
        {"data": contract_sign_data},
    )
    response = self.app.get(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def cancellation_of_change(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"value": {"amount": 235, "amountNet": 200}},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    change_1 = response.json["data"]
    self.assertEqual(change_1["status"], "pending")

    # cancel change
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes/{change_1['id']}/cancellations?acc_token={self.contract_token}",
        {"data": {}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "reason", "description": ["This field is required."]},
            {"location": "body", "name": "reasonType", "description": ["This field is required."]},
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes/{change_1['id']}/cancellations?acc_token={self.contract_token}",
        {
            "data": {"reason": "Not actual", "reasonType": "Not actual"},
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "reasonType",
                "description": ["Value must be one of ['noDemand', 'unFixable', 'forceMajeure', 'expensesCut']."],
            }
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes/{change_1['id']}/cancellations?acc_token={self.contract_token}",
        {
            "data": {"reason": "Not actual", "reasonType": "noDemand"},
        },
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]
    response = self.app.get(
        f"/contracts/{self.contract['id']}/changes/{change_1['id']}?acc_token={self.contract_token}",
    )
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertEqual(response.json["data"]["cancellations"][0]["status"], "active")
    self.assertEqual(response.json["data"]["cancellations"][0]["author"], "buyer")
    self.assertNotEqual(response.json["data"]["date"], change_1["date"])

    response = self.app.get(
        f"/contracts/{self.contract['id']}/changes/{change_1['id']}/cancellations?acc_token={self.contract_token}",
    )
    self.assertEqual(response.json["data"][0]["status"], "active")
    self.assertEqual(response.json["data"][0]["author"], "buyer")

    response = self.app.get(
        f"/contracts/{self.contract['id']}/changes/{change_1['id']}/cancellations/{cancellation_id}?acc_token={self.contract_token}",
    )
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["author"], "buyer")

    # try to patch cancellation
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change_1['id']}/cancellations/{cancellation_id}?acc_token={self.contract_token}",
        {"data": {"rerason": "New"}},
        status=405,
    )
    self.assertEqual(response.status, "405 Method Not Allowed")

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"value": {"amount": 235, "amountNet": 200}},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    change_2 = response.json["data"]
    self.assertEqual(change_2["status"], "pending")

    self.activate_change(change_2['id'])
    response = self.app.get(
        f"/contracts/{self.contract['id']}/changes/{change_2['id']}?acc_token={self.contract_token}",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # try to patch active change
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes/{change_2['id']}/cancellations?acc_token={self.contract_token}",
        {
            "data": {"reason": "Not actual", "reasonType": "noDemand"},
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update contract change in current (active) status",
            }
        ],
    )


def change_contract_wo_amount_net(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"value": {"currency": "UAH", "amount": self.contract["value"]["amount"] - 1}},
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"description": {"amountNet": "This field is required."}, "location": "body", "name": "value"}],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"value": {"amount": 235, "amountNet": 200}},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")


def change_contract_value_amount(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"value": {**self.contract["value"], "amount": 235, "amountNet": 237}},
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"value": {"amount": 235, "amountNet": 100}},
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"value": {"amount": 235, "amountNet": 201}},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    contract_modifications = response.json["data"]["modifications"]
    self.assertEqual(contract_modifications["value"]["amount"], 235)
    self.assertEqual(contract_modifications["value"]["amountNet"], 201)
    self.assertEqual(contract_modifications["value"]["currency"], "UAH")
    self.assertEqual(contract_modifications["value"]["valueAddedTaxIncluded"], True)


def change_contract_value_vat_change(self):
    # check that contract.value.valueAddedTaxIncluded is True
    self.assertEqual(
        self.contract["value"]["valueAddedTaxIncluded"],
        True,
    )

    # check contract.items.unit.value.valueAddedTaxIncluded is False
    for item in self.contract["items"]:
        self.assertEqual(
            item["unit"]["value"]["valueAddedTaxIncluded"],
            False,
        )
    contract_items = deepcopy(self.contract["items"])
    contract_items[0]["unit"]["value"]["amount"] = 21.64
    contract_items[0]["quantity"] = 11  # 11 * 21.64 = 238.04

    # change contract.value.valueAddedTaxIncluded from True to False
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.bid_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {
                    "value": {"valueAddedTaxIncluded": False, "amount": 238, "amountNet": 238},
                    "items": contract_items,
                },
            },
        },
    )
    contract_modifications = response.json["data"]["modifications"]
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(contract_modifications["value"]["amount"], 238)
    self.assertEqual(contract_modifications["value"]["amountNet"], 238)

    # check that contract.value.valueAddedTaxIncluded is False
    self.assertEqual(
        contract_modifications["value"]["valueAddedTaxIncluded"],
        False,
    )

    # check contract.items.unit.value.valueAddedTaxIncluded
    # updated from contract.value.valueAddedTaxIncluded
    for item in contract_modifications["items"]:
        self.assertEqual(
            item["unit"]["value"]["valueAddedTaxIncluded"],
            contract_modifications["value"]["valueAddedTaxIncluded"],
        )

    # TODO: don't forget about this equality when amountPaid will be patched (in future eContracting tasks)
    # check contract.amountPaid.valueAddedTaxIncluded
    # was not updated with contract.value.valueAddedTaxIncluded
    # self.assertNotEqual(
    #     self.contract["amountPaid"]["valueAddedTaxIncluded"],
    #     contract_modifications["value"]["valueAddedTaxIncluded"],
    # )
    # response = self.app.post_json(
    #     f"/contracts/{self.contract['id']}/changes?acc_token={self.bid_token}",
    #     {
    #         "data": {
    #             "rationale": "причина зміни укр",
    #             "rationale_en": "change cause en",
    #             "rationaleTypes": ["priceReduction"],
    #             "modifications": {
    #                 "amountPaid": {"valueAddedTaxIncluded": False, "amount": 238, "amountNet": 239}
    #             }
    #         },
    #     },
    #     status=403,
    # )
    # self.assertEqual(response.status, "403 Forbidden")
    # self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")


def change_contract_period(self):
    previous_period = {
        "startDate": "2016-02-20T18:47:47.155143+02:00",
        "endDate": "2016-06-15T18:47:47.155143+02:00",
    }

    contract_doc = self.mongodb.contracts.get(self.contract["id"])
    contract_doc['period'] = previous_period
    self.mongodb.contracts.save(contract_doc)

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.bid_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {
                    "period": {
                        "startDate": "2016-06-10T18:47:47.155143+02:00",
                    },
                },
            }
        },
    )
    change = response.json["data"]
    self.assertNotEqual(
        change["modifications"]["period"]["startDate"],
        previous_period["startDate"],
    )
    self.activate_change(change['id'])

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.bid_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {
                    "period": {
                        "endDate": "2016-06-20T18:47:47.155143+02:00",
                    },
                },
            }
        },
    )
    change_2 = response.json["data"]
    self.assertNotEqual(
        change_2["modifications"]["period"]["endDate"],
        previous_period["endDate"],
    )
    self.activate_change(change_2['id'])

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.bid_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {
                    "period": {
                        "endDate": "2016-06-01T18:47:47.155143+02:00",
                    },
                },
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "period should begin before its end",
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.bid_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {
                    "period": {
                        "startDate": "2016-03-20T18:47:47.155143+02:00",
                        "endDate": "2016-06-20T18:47:47.155143+02:00",
                    },
                },
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["modifications"]["period"]["startDate"], "2016-03-20T18:47:47.155143+02:00")


def change_for_pending_contract_forbidden(self):
    contract_doc = self.mongodb.contracts.get(self.contract["id"])
    contract_doc["status"] = "pending"
    self.mongodb.contracts.save(contract_doc)

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.bid_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"title": "new contract"},
            },
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't add contract change in current (pending) contract status",
            }
        ],
    )


def contract_token_invalid(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={'fake token'}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"title": "new contract"},
            },
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={'токен з кирилицею'}",
        {
            "data": {},
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'UnicodeEncodeError',
                'description': "'latin-1' codec can't encode characters in position 10-14: ordinal not in range(256)",
            }
        ],
    )


def change_documents(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "modifications": {"value": {"amount": 235, "amountNet": 200}},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    change = response.json["data"]

    contract_sign_data = {
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/changes/{change['id']}/documents?acc_token={self.contract_token}",
        {"data": contract_sign_data},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Only contractSignature documentType is allowed"
            }
        ],
    )

    contract_sign_data["documentType"] = "contractSignature"
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/changes/{change['id']}/documents?acc_token={self.contract_token}",
        {"data": contract_sign_data},
    )
    doc_id = response.json["data"]["id"]

    # try to patch
    self.app.patch_json(
        f"/contracts/{self.contract_id}/changes/{change['id']}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"title": "sign2.p7s"}},
        status=404,
    )

    # try to put
    self.app.put_json(
        f"/contracts/{self.contract_id}/changes/{change['id']}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": contract_sign_data},
        status=404,
    )

    response = self.app.get(
        f"/contracts/{self.contract_id}/changes/{change['id']}/documents/{doc_id}?acc_token={self.contract_token}",
    )
    self.assertEqual(response.json["data"]["title"], "sign.p7s")

    response = self.app.get(
        f"/contracts/{self.contract_id}/changes/{change['id']}/documents?acc_token={self.contract_token}",
    )
    self.assertEqual(response.json["data"][0]["title"], "sign.p7s")
