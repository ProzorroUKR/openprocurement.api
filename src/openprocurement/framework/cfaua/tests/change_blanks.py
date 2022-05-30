from copy import deepcopy
from datetime import timedelta

from mock import patch

from openprocurement.api.utils import get_now
from openprocurement.framework.cfaua.models.agreement import Agreement


def no_items_agreement_change(self):
    data = deepcopy(self.initial_data)
    del data["items"]
    response = self.app.post_json("/agreements", {"data": data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    agreement = response.json["data"]
    self.assertEqual(agreement["status"], "active")
    self.assertNotIn("items", agreement)
    tender_token = data["tender_token"]

    response = self.app.patch_json(
        "/agreements/{}/credentials?acc_token={}".format(agreement["id"], tender_token), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(agreement["id"], token),
        {"data": {"rationale": "test", "rationaleType": "taxRate"}},
    )
    self.assertEqual(response.status, "201 Created")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(agreement["id"], change["id"], token),
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Modifications are required for change activation."}],
    )

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(agreement["id"], change["id"], token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(agreement["id"], token),
        {"data": {"status": "terminated", "description": "test description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")

    response = self.app.get("/agreements/{}".format(agreement["id"]))
    self.assertNotIn("items", response.json["data"])


def not_found(self):
    response = self.app.get("/agreements/some_id/changes", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )

    response = self.app.get("/agreements/{}/changes".format(self.agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/agreements/{}/changes/some_id".format(self.agreement["id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "change_id"}]
    )

    response = self.app.patch_json(
        "/agreements/{}/changes/some_id".format(self.agreement["id"]), {"data": {}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "change_id"}]
    )


def get_change(self):
    data = deepcopy(self.initial_change)
    data["rationale_ru"] = "Анна Каренина"
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)

    response = self.app.get("/agreements/{}/changes".format(self.agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/agreements/{}/changes/{}".format(self.agreement["id"], change["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    change_data = response.json["data"]
    self.assertEqual(change_data, change)

    response = self.app.get("/agreements/{}".format(self.agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("changes", response.json["data"])
    self.assertEqual(len(response.json["data"]["changes"]), 1)
    self.assertEqual(
        set(response.json["data"]["changes"][0].keys()),
        {"id", "date", "status", "rationaleType", "rationale", "rationale_ru", "rationale_en", "agreementNumber"},
    )

    self.app.authorization = None
    response = self.app.get("/agreements/{}/changes".format(self.agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        {"id", "date", "status", "rationaleType", "rationale", "rationale_ru", "rationale_en", "agreementNumber"},
    )


def create_change_invalid(self):
    response = self.app.post(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), "data", status=415
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
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": {}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [{"description": "Can't add change without rationaleType", "location": "body", "name": "data"}],
    )

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": {"rationaleType": "fake"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "rationaleType should be one of ['taxRate', 'itemPriceVariation', 'thirdParty', 'partyWithdrawal']",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": {"rationale": "", "rationaleType": "taxRate"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "rationale", "description": ["String value is too short."]}],
    )

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": {"rationaleType": "taxRate", "rationale_ua": ""}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "rationale_ua", "description": "Rogue field"}]
    )

    item_id = self.agreement["items"][0]["id"]
    invalid_value = [
        unit_price["value"]["amount"]
        for contract in self.agreement["contracts"]
        for unit_price in contract["unitPrices"]
    ][0] * -2
    data = deepcopy(self.initial_change)
    data.update({"modifications": [{"itemId": item_id, "addend": invalid_value}]})

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token),
        {"data": data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "unitPrice:value:amount can't be equal or less than 0.",
                "location": "body",
                "name": "data",
            }
        ],
    )

    data["modifications"][0]["itemId"] = "3" * 32
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token),
        {"data": data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Item id should be uniq for all modifications and one of agreement:items"],
                "location": "body",
                "name": "modifications",
            }
        ],
    )

    data.update({"modifications": [{"contractId": "2" * 32}], "rationaleType": "partyWithdrawal"})
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token),
        {"data": data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Contract id should be uniq for all modifications and one of agreement:contracts"],
                "location": "body",
                "name": "modifications",
            }
        ],
    )

    data.update({"modifications": [{"itemId": item_id, "addend": 30, "factor": 0.95}], "rationaleType": "taxRate"})
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token),
        {"data": data},
        status=422,
    )
    self.assertEqual((response.status, response.content_type), ("422 Unprocessable Entity", "application/json"))
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Change with taxRate rationaleType, can have only factor or only addend"],
                "location": "body",
                "name": "modifications",
            }
        ],
    )

    self.app.authorization = None
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/agreements/{}/changes".format(self.agreement["id"]), {"data": {"rationale_ua": "aaa"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": {"changes": [deepcopy(self.initial_change)]}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/agreements/{}?acc_token={}".format(self.agreement["id"], self.agreement_token))
    self.assertEqual(response.status, "200 OK")


def create_change(self):
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)
    self.assertNotIn("warnings", response.json)

    response = self.app.get("/agreements/{}/changes".format(self.agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't create new agreement change while any (pending) change exists",
            }
        ],
    )
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {
            "data": {
                "status": "active",
                "dateSigned": get_now().isoformat(),
                "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    data = deepcopy(self.initial_change)
    del data["rationaleType"]
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Can't add change without rationaleType", "location": "body", "name": "data"}],
    )

    data["rationaleType"] = "partyWithdrawal"
    data["modifications"] = [{"contractId": self.agreement["contracts"][0]["id"]}]
    data["dateSigned"] = get_now().isoformat()
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
    )
    self.assertEqual(response.status, "201 Created")
    change2 = response.json["data"]
    self.assertEqual(change2["status"], "pending")
    self.assertIn("warnings", response.json)
    self.assertEqual(response.json["warnings"], ["Min active contracts in FrameworkAgreement less than 3."])

    response = self.app.get("/agreements/{}/changes".format(self.agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)


def create_change_item_price_variation_modifications_boundaries(self):
    data = deepcopy(self.initial_change)
    data.update({"rationaleType": "itemPriceVariation"})

    for x in (0.9, 0.91, 0.901, 0.9001, 0.89995, 1.1, 1.09, 1.009, 1.0009, 1.100005):
        data.update({"modifications": [{"factor": x, "itemId": self.agreement["items"][0]["id"]}]})
        response = self.app.post_json(
            "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
        )
        self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
        change = response.json["data"]
        self.assertEqual(change["status"], "pending")
        self.assertEqual(change["modifications"][0]["factor"], round(x, 4))
        self.assertIn("date", change)

        real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
        preview_agreement = self.app.get("/agreements/{}/preview".format(self.agreement_id)).json["data"]
        real_unit_prices = [
            unit_price["value"]["amount"]
            for contract in real_agreement["contracts"]
            for unit_price in contract["unitPrices"]
            if unit_price["relatedItem"] == self.agreement["items"][0]["id"]
        ]
        preview_unit_prices = [
            unit_price["value"]["amount"]
            for contract in preview_agreement["contracts"]
            for unit_price in contract["unitPrices"]
            if unit_price["relatedItem"] == self.agreement["items"][0]["id"]
        ]
        self.assertNotEqual(real_unit_prices, preview_unit_prices)
        for i, v in enumerate(real_unit_prices):
            self.assertEqual(preview_unit_prices[i], round(v * round(x, 4), 2))

        response = self.app.patch_json(
            "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
            {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
        )
        self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    for x in (0.89, 0.899, 0.8999, 0.89994, 1.11, 1.101, 1.1001, 1.10006):
        data.update({"modifications": [{"factor": x, "itemId": self.agreement["items"][0]["id"]}]})
        response = self.app.post_json(
            "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
            {"data": data},
            status=422,
        )

        self.assertEqual((response.status, response.content_type), ("422 Unprocessable Entity", "application/json"))
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": ["Modification factor should be in range 0.9 - 1.1"],
                    "location": "body",
                    "name": "modifications",
                }
            ],
        )


def patch_change(self):
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertEqual(change["agreementNumber"], "№ 146")
    creation_date = change["date"]

    now = get_now().isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"date": now}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.body, b"null")

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"rationale_ru": "шота на руськом"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("rationale_ru", response.json["data"])
    first_patch_date = response.json["data"]["date"]
    self.assertEqual(first_patch_date, creation_date)

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"rationale_en": "another cause desctiption"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["rationale_en"], "another cause desctiption")
    second_patch_date = response.json["data"]["date"]
    self.assertEqual(first_patch_date, second_patch_date)

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"rationaleType": "thirdParty"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.body, b"null")

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"id": "1234" * 8}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.body, b"null")

    self.app.authorization = None
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"rationale_en": "la-la-la"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/agreements/{}/changes/{}".format(self.agreement["id"], change["id"]),
        {"data": {"rationale_en": "la-la-la"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {
            "data": {
                "status": "active",
                "dateSigned": get_now().isoformat(),
                "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotEqual(response.json["data"]["date"], creation_date)
    self.assertNotEqual(response.json["data"]["date"], first_patch_date)
    self.assertNotEqual(response.json["data"]["date"], second_patch_date)

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    # testing changes validators
    data = deepcopy(self.initial_change)
    data.update({"rationaleType": "itemPriceVariation", "modifications": [{"itemId": "1" * 32, "addend": 0.01}]})
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": data},
        status=422,
    )

    self.assertEqual((response.status, response.content_type), ("422 Unprocessable Entity", "application/json"))
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Only factor is allowed for itemPriceVariation type of change"],
                "location": "body",
                "name": "modifications",
            }
        ],
    )

    data.update({"modifications": [{"factor": "0.0100"}]})
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": data},
        status=422,
    )

    self.assertEqual((response.status, response.content_type), ("422 Unprocessable Entity", "application/json"))
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Modification factor should be in range 0.9 - 1.1"],
                "location": "body",
                "name": "modifications",
            }
        ],
    )

    data = deepcopy(self.initial_change)
    data.update({"rationaleType": "thirdParty", "modifications": [{"itemId": "1" * 32, "addend": 0.01}]})
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": data},
        status=422,
    )

    self.assertEqual((response.status, response.content_type), ("422 Unprocessable Entity", "application/json"))
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Only factor is allowed for thirdParty type of change"],
                "location": "body",
                "name": "modifications",
            }
        ],
    )

    data = deepcopy(self.initial_change)
    data.update(
        {"rationaleType": "thirdParty", "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.0}]}
    )
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": data},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "unitPrice:value:amount can't be equal or less than 0.",
                "location": "body",
                "name": "data",
            }
        ],
    )

    data["modifications"] = [{"itemId": "1" * 32, "factor": 0.01}, {"itemId": "1" * 32, "factor": 0.02}]
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": data},
        status=422,
    )

    self.assertEqual((response.status, response.content_type), ("422 Unprocessable Entity", "application/json"))
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Item id should be uniq for all modifications and one of agreement:items"],
                "location": "body",
                "name": "modifications",
            }
        ],
    )


def change_date_signed(self):
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertEqual(change["agreementNumber"], "№ 146")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update agreement change status. 'dateSigned' is required.",
            }
        ],
    )

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"dateSigned": "12-14-11"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "dateSigned", "description": ["Could not parse 12-14-11. Should be ISO8601."]}],
    )

    valid_date1_raw = get_now()
    valid_date1 = valid_date1_raw.isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"dateSigned": valid_date1}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date1)

    one_day_in_past = (get_now() - timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"dateSigned": one_day_in_past}},
        status=403,
    )
    self.assertIn("can't be earlier than agreement dateSigned", response.json["errors"][0]["description"])

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"status": "active", "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}]}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"dateSigned": get_now().isoformat()}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update agreement change in current (active) status",
            }
        ],
    )

    response = self.app.get("/agreements/{}/changes/{}".format(self.agreement["id"], change["id"]))
    change1 = response.json["data"]
    self.assertEqual(change1["dateSigned"], valid_date1)

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change2 = response.json["data"]
    self.assertEqual(change["status"], "pending")

    one_day_in_future = (get_now() + timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change2["id"], self.agreement_token),
        {"data": {"dateSigned": one_day_in_future}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "dateSigned",
                "description": ["Agreement signature date can't be in the future"],
            }
        ],
    )
    smaller_than_last_change = (valid_date1_raw - timedelta(seconds=1)).isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change2["id"], self.agreement_token),
        {"data": {"dateSigned": smaller_than_last_change}},
        status=403,
    )
    self.assertEqual(
        "Change dateSigned ({}) can't be earlier than last active change dateSigned ({})".format(
            smaller_than_last_change, valid_date1
        ),
        response.json["errors"][0]["description"],
    )

    date = get_now().isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change2["id"], self.agreement_token),
        {"data": {"dateSigned": date}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], date)
    # date update request
    valid_date2_raw = get_now()
    valid_date2 = valid_date2_raw.isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change2["id"], self.agreement_token),
        {"data": {"dateSigned": valid_date2}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date2)

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change2["id"], self.agreement_token),
        {"data": {"status": "active", "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date2)

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
    )
    self.assertEqual(response.status, "201 Created")
    change3 = response.json["data"]
    self.assertEqual(change["status"], "pending")

    smaller_than_last_change = (valid_date2_raw - timedelta(seconds=1)).isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change3["id"], self.agreement_token),
        {"data": {"dateSigned": smaller_than_last_change}},
        status=403,
    )
    self.assertEqual(
        "Change dateSigned ({}) can't be earlier than last active change dateSigned ({})".format(
            smaller_than_last_change, valid_date2
        ),
        response.json["errors"][0]["description"],
    )
    date = get_now().isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change3["id"], self.agreement_token),
        {"data": {"dateSigned": date}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], date)

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change3["id"], self.agreement_token),
        {"data": {"status": "active", "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}]}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": {"status": "terminated"}},
    )
    self.assertEqual(response.status, "200 OK")


def date_signed_on_change_creation(self):
    # test create change with date signed
    one_day_in_past = (get_now() - timedelta(days=1)).isoformat()
    data = deepcopy(self.initial_change)
    data["dateSigned"] = one_day_in_past
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": data},
        status=403,
    )
    self.assertIn("can't be earlier than agreement dateSigned", response.json["errors"][0]["description"])
    one_day_in_future = (get_now() + timedelta(days=1)).isoformat()
    data["dateSigned"] = one_day_in_future
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "dateSigned",
                "description": ["Agreement signature date can't be in the future"],
            }
        ],
    )
    date = get_now().isoformat()
    data["dateSigned"] = date
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["dateSigned"], date)

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"status": "active", "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}]}},
    )
    self.assertEqual(response.status, "200 OK")


def change_date_signed_very_old_agreements_data(self):
    # prepare old agreement data
    agreement = self.mongodb.agreements.get(self.agreement["id"])
    agreement["dateSigned"] = None
    self.mongodb.agreements.save(Agreement(agreement))

    response = self.app.get("/agreements/{}?acc_token={}".format(self.agreement["id"], self.agreement_token))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("dateSigned", response.json["data"])

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update agreement change status. 'dateSigned' is required.",
            }
        ],
    )

    one_day_in_past = (get_now() - timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {
            "data": {
                "status": "active",
                "dateSigned": one_day_in_past,
                "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}],
            }
        },
    )
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["dateSigned"], one_day_in_past)

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change2 = response.json["data"]
    self.assertEqual(change["status"], "pending")

    two_days_in_past = (get_now() - timedelta(days=2)).isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change2["id"], self.agreement_token),
        {"data": {"dateSigned": two_days_in_past}},
        status=403,
    )
    self.assertEqual(
        "Change dateSigned ({}) can't be earlier than last active change dateSigned ({})".format(
            two_days_in_past, one_day_in_past
        ),
        response.json["errors"][0]["description"],
    )

    valid_date = get_now().isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change2["id"], self.agreement_token),
        {
            "data": {
                "status": "active",
                "dateSigned": valid_date,
                "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}],
            }
        },
    )
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date)

    # prepare old agreement change data
    agreement = self.mongodb.agreements.get(self.agreement["id"])
    last_change = agreement["changes"][-1]
    last_change["dateSigned"] = None
    self.mongodb.agreements.save(Agreement(agreement))

    response = self.app.get(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], last_change["id"], self.agreement_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("dateSigned", response.json["data"])

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": deepcopy(self.initial_change)},
    )
    self.assertEqual(response.status, "201 Created")
    change3 = response.json["data"]
    self.assertEqual(change["status"], "pending")

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change3["id"], self.agreement_token),
        {"data": {"dateSigned": two_days_in_past}},
        status=403,
    )
    self.assertEqual(
        "Change dateSigned ({}) can't be earlier than last active change dateSigned ({})".format(
            two_days_in_past, last_change["date"]
        ),
        response.json["errors"][0]["description"],
    )

    valid_date2 = get_now().isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change3["id"], self.agreement_token),
        {
            "data": {
                "status": "active",
                "dateSigned": valid_date2,
                "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}],
            }
        },
    )
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date2)


def date_signed_on_change_creation_for_very_old_agreements_data(self):
    # prepare old agreement data
    agreement = self.mongodb.agreements.get(self.agreement["id"])
    agreement["dateSigned"] = None
    self.mongodb.agreements.save(Agreement(agreement))

    response = self.app.get("/agreements/{}?acc_token={}".format(self.agreement["id"], self.agreement_token))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("dateSigned", response.json["data"])

    self.app.authorization = ("Basic", ("broker", ""))
    one_day_in_past = (get_now() - timedelta(days=1)).isoformat()
    data = deepcopy(self.initial_change)
    data["dateSigned"] = one_day_in_past
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
    )
    self.assertEqual(response.json["data"]["dateSigned"], one_day_in_past)
    change = response.json["data"]
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"status": "active", "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}]}},
    )
    self.assertEqual(response.json["data"]["status"], "active")

    # prepare old agreement change data
    agreement = self.mongodb.agreements.get(self.agreement["id"])
    last_change = agreement["changes"][-1]
    last_change["dateSigned"] = None
    self.mongodb.agreements.save(Agreement(agreement))

    response = self.app.get(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], last_change["id"], self.agreement_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("dateSigned", response.json["data"])

    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token),
        {"data": data},
        status=403,
    )
    self.assertEqual(
        "Change dateSigned ({}) can't be earlier than last active change dateSigned ({})".format(
            one_day_in_past, last_change["date"]
        ),
        response.json["errors"][0]["description"],
    )

    valid_date = get_now().isoformat()
    data["dateSigned"] = valid_date
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
    )
    self.assertEqual(response.json["data"]["dateSigned"], valid_date)


def multi_change(self):
    # first change
    data = deepcopy(self.initial_change)
    data["rationaleType"] = "itemPriceVariation"
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
    )
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    self.assertIn("rationaleType", response.json["data"])
    self.assertEqual(response.json["data"]["rationaleType"], "itemPriceVariation")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)

    # patch first change to be able to create second change
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {
            "data": {
                "status": "active",
                "dateSigned": get_now().isoformat(),
                "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}],
            }
        },
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    # second change with invalid itemId
    data = deepcopy(self.initial_change)
    data.update({"rationaleType": "taxRate", "modifications": [{"itemId": "1" * 32, "factor": "0.9"}]})
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token),
        {"data": data},
        status=422,
    )
    self.assertEqual((response.status, response.content_type), ("422 Unprocessable Entity", "application/json"))
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "modifications",
                "description": ["Item id should be uniq for all modifications and one of agreement:items"],
            }
        ],
    )

    data.update(
        {"rationaleType": "taxRate", "modifications": [{"itemId": self.agreement["items"][0]["id"], "factor": "0.9"}]}
    )
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
    )
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    self.assertIn("rationaleType", response.json["data"])
    self.assertEqual(response.json["data"]["rationaleType"], "taxRate")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)

    response = self.app.get("/agreements/{}".format(self.agreement["id"]))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(len(response.json["data"]["changes"]), 2)

    date_signed = get_now().isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"status": "active", "dateSigned": date_signed}},
    )

    change = deepcopy(self.initial_change)
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": change}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "pending")
    change_id = response.json["data"]["id"]

    response = self.app.get("/agreements/{}/changes".format(self.agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)

    date_signed = get_now().isoformat()
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change_id, self.agreement_token),
        {"data": {"status": "active", "dateSigned": date_signed}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Modifications are required for change activation.",
                "location": "body",
                "name": "data",
            }
        ],
    )


@patch("openprocurement.framework.cfaua.models.agreement.get_now")
def activate_change_after_1_cancelled(self, mocked_model_get_now):
    # first change
    data = deepcopy(self.initial_change)
    data["rationaleType"] = "itemPriceVariation"
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
    )
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    self.assertIn("rationaleType", response.json["data"])
    self.assertEqual(response.json["data"]["rationaleType"], "itemPriceVariation")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)

    date_signed = get_now() + timedelta(minutes=10)
    mocked_model_get_now.return_value = date_signed
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": {"status": "cancelled", "dateSigned": date_signed.isoformat()}},
    )
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertEqual(response.json["data"]["dateSigned"], date_signed.isoformat())
    cancelled_change = response.json["data"]

    now = get_now().isoformat()
    data = deepcopy(self.initial_change)
    data["rationaleType"] = "itemPriceVariation"
    data["dateSigned"] = now
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement["id"], self.agreement_token), {"data": data}
    )

    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    self.assertIn("rationaleType", response.json["data"])
    self.assertEqual(response.json["data"]["rationaleType"], "itemPriceVariation")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)
    self.assertEqual(change["dateSigned"], now)

    self.assertLess(change["dateSigned"], cancelled_change["dateSigned"])

    data = {"status": "active"}
    data["dateSigned"] = (get_now() - timedelta(days=90)).isoformat()
    data["modifications"] = [{"itemId": self.agreement["items"][0]["id"], "factor": 0.9}]
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement["id"], change["id"], self.agreement_token),
        {"data": data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Change dateSigned ({}) can't be earlier than agreement dateSigned ({})".format(
                    data["dateSigned"], self.agreement["dateSigned"]
                ),
                "location": "body",
                "name": "data",
            }
        ],
    )
