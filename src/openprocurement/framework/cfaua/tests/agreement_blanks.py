import uuid
from copy import deepcopy
from datetime import datetime
from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.framework.cfaua.tests.data import TEST_DOCUMENTS


def create_agreement(self):
    data = self.initial_data
    data["id"] = uuid.uuid4().hex
    with change_auth(self.app, ("Basic", ("agreements", ""))) as app:
        response = self.app.post_json("/agreements", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["agreementID"], data["agreementID"])

    response = self.app.get("/agreements/{}".format(data["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["id"], data["id"])


def create_agreement_with_documents(self):
    data = deepcopy(self.initial_data)
    data["id"] = uuid.uuid4().hex
    data["documents"] = TEST_DOCUMENTS
    with change_auth(self.app, ("Basic", ("agreements", ""))) as app:
        response = self.app.post_json("/agreements", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["agreementID"], data["agreementID"])

    response = self.app.get("/agreements/{}".format(data["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["id"], data["id"])

    response = self.app.get("/agreements/{}/documents".format(data["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), len(TEST_DOCUMENTS))


def create_agreement_with_features(self):
    data = deepcopy(self.initial_data)
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item]
    data["features"] = self.features
    parameters = {"parameters": [{"code": i["code"], "value": i["enum"][0]["value"]} for i in data["features"]]}

    for contract in data["contracts"]:
        contract.update(parameters)

    with change_auth(self.app, ("Basic", ("agreements", ""))) as app:
        response = self.app.post_json("/agreements", {"data": data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    agreement = response.json["data"]
    self.assertEqual(agreement["features"], data["features"])
    for contract in agreement["contracts"]:
        self.assertEqual(contract["parameters"], parameters["parameters"])


def patch_agreement_features_invalid(self):
    data = deepcopy(self.initial_data)
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item]
    data["features"] = self.features

    with change_auth(self.app, ("Basic", ("agreements", ""))) as app:
        response = self.app.post_json("/agreements", {"data": data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    agreement = response.json["data"]
    self.assertEqual(agreement["features"], data["features"])
    agreement = response.json["data"]
    token = response.json["access"]["token"]

    new_features = deepcopy(data["features"])
    new_features[0]["code"] = "OCDS-NEW-CODE"
    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(agreement["id"], token), {"data": {"features": new_features}}, status=403
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["errors"][0]["description"], "Can't change features")


def get_agreements_by_id(self):
    response = self.app.get("/agreements/{}".format(self.agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["id"], self.agreement_id)

    bad_agreement_id = uuid.uuid4().hex
    response = self.app.get("/agreements/{}".format(bad_agreement_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")


def generate_credentials(self):
    tender_token = self.initial_data["tender_token"]
    response = self.app.get("/agreements/{}".format(self.agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement_id, tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/agreements/{}/credentials?acc_token={}".format(self.agreement_id, tender_token), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json.get("access", {}).get("token")
    self.assertIsNotNone(token)
    doc = self.mongodb.agreements.get(self.agreement_id)
    self.assertEqual(doc["owner_token"], token)


def agreement_patch_invalid(self):
    for data in [
        {"title": "new title"},
        {
            "items": [
                {
                    "description": "description",
                    "additionalClassifications": [
                        {"scheme": "ДКПП", "id": "01.11.83-00.00", "description": "Арахіс лущений"}
                    ],
                    "deliveryAddress": {
                        "postalCode": "11223",
                        "countryName": "Україна",
                        "streetAddress": "ываыпып",
                        "region": "Київська область",
                        "locality": "м. Київ",
                    },
                    "deliveryDate": {"startDate": "2016-05-16T00:00:00+03:00", "endDate": "2016-06-29T00:00:00+03:00"},
                }
            ]
        },
        {
            "procuringEntity": {
                "contactPoint": {"email": "mail@gmail.com"},
                "identifier": {
                    "scheme": "UA-EDR",
                    "id": "111111111111111",
                    "legalName": "Демо организатор (государственные торги)",
                },
                "name": "Демо организатор (государственные торги)",
                "kind": "other",
                "address": {"postalCode": "21027", "countryName": "Україна"},
            }
        },
    ]:
        response = self.app.patch_json("/agreements/{}?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": data})
        self.assertEqual(response.status, "200 OK")
        self.assertIsNone(response.json)

    agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertNotIn("changes", agreement)

    change_data = deepcopy(self.initial_change)
    change_data["rationaleType"] = "thirdParty"
    change_data["modifications"] = [{"itemId": agreement["items"][0]["id"], "factor": 0.001}]
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": change_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "pending")
    change_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": {"status": "terminated"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update agreement status with pending change.",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement_id, change_id, self.agreement_token),
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": {"status": "terminated"}}
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "terminated")
    response = self.app.patch_json(
        "/agreements/{}/credentials?acc_token={}".format(self.agreement_id, self.initial_data["tender_token"]),
        {"data": ""},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't generate credentials in current (terminated)" " agreement status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def empty_listing(self):
    response = self.app.get("/agreements")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertNotIn('{\n    "', response.body.decode())
    self.assertNotIn("callback({", response.body.decode())
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/agreements?opt_jsonp=callback")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertNotIn('{\n    "', response.body.decode())
    self.assertIn("callback({", response.body.decode())

    response = self.app.get("/agreements?opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())
    self.assertNotIn("callback({", response.body.decode())

    response = self.app.get("/agreements?opt_jsonp=callback&opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('{\n    "', response.body.decode())
    self.assertIn("callback({", response.body.decode())

    offset = datetime.fromisoformat("2015-01-01T00:00:00+02:00").timestamp()
    response = self.app.get(f"/agreements?offset={offset}&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])

    response = self.app.get("/agreements?offset=latest", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Invalid offset provided: latest",
          "location": "querystring", "name": "offset"}],
    )

    response = self.app.get("/agreements?descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])


def listing(self):
    response = self.app.get("/agreements")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    agreements = []

    for i in range(3):
        data = deepcopy(self.initial_data)
        data["id"] = uuid.uuid4().hex
        offset = get_now().timestamp()
        with change_auth(self.app, ("Basic", ("agreements", ""))) as app:
            response = self.app.post_json("/agreements", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        agreements.append(response.json["data"])

    ids = ",".join([i["id"] for i in agreements])

    response = self.app.get("/agreements")
    self.assertEqual(response.status, "200 OK")
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in agreements]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in agreements])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in agreements])
    )

    response = self.app.get(f"/agreements?offset={offset}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/agreements?limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/agreements", params=[("opt_fields", "agreementID")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "agreementID"})
    self.assertIn("opt_fields=agreementID", response.json["next_page"]["uri"])

    response = self.app.get("/agreements?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in agreements]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]],
        sorted([i["dateModified"] for i in agreements], reverse=True),
    )

    response = self.app.get("/agreements?descending=1&limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)

    test_agreement_data2 = deepcopy(self.initial_data)
    test_agreement_data2["mode"] = "test"
    with change_auth(self.app, ("Basic", ("agreements", ""))) as app:
        response = self.app.post_json("/agreements", {"data": test_agreement_data2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/agreements?mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/agreements?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)

    response = self.app.get("/agreements?mode=_all_&opt_fields=status")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def agreement_preview(self):
    response = self.app.get("/agreements/{}".format(self.agreement_id))
    agreement = response.json["data"]
    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    agreement_preview = response.json["data"]
    self.assertEqual(agreement, agreement_preview)

    unit_prices_before = [
        unit_price
        for contract in response.json["data"]["contracts"]
        for unit_price in contract["unitPrices"]
        if unit_price["relatedItem"] == agreement["items"][0]["id"]
    ]

    # create change
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token),
        {
            "data": {
                "rationale": "Принцеси .....",
                "rationale_ru": "ff",
                "rationale_en": "asdf",
                "agreementNumber": 12,
                "rationaleType": "taxRate",
                "modifications": [{"itemId": agreement["items"][0]["id"], "addend": "1.25"}],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("rationaleType", response.json["data"])
    self.assertEqual(response.json["data"]["rationaleType"], "taxRate")
    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))

    unit_prices_after = [
        unit_price
        for contract in response.json["data"]["contracts"]
        for unit_price in contract["unitPrices"]
        if unit_price["relatedItem"] == agreement["items"][0]["id"]
    ]
    self.assertNotEqual(unit_prices_after, unit_prices_before)


def agreement_change_tax_rate_preview(self):
    agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertNotIn("changes", agreement)

    change_data = deepcopy(self.initial_change)
    self.assertEqual(change_data["rationaleType"], "taxRate")
    change_data["modifications"] = [{"itemId": agreement["items"][0]["id"], "addend": 10}]

    # create taxRate change with addend
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": change_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertEqual(response.json["data"]["rationaleType"], "taxRate")
    self.assertEqual(response.json["data"]["modifications"], change_data["modifications"])
    self.assertNotIn("warnings", response.json)
    change_id = response.json["data"]["id"]

    real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertEqual(len(real_agreement["changes"]), 1)
    real_agreement.pop("changes")
    real_agreement.pop("dateModified")
    agreement.pop("dateModified")
    self.assertEqual(agreement, real_agreement)

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    self.assertNotIn("warnings", response.json)
    preview_agreement = response.json["data"]
    real_unit_prices = [
        unit_price["value"]["amount"]
        for contract in real_agreement["contracts"]
        for unit_price in contract["unitPrices"]
        if unit_price["relatedItem"] == agreement["items"][0]["id"]
    ]
    preview_unit_prices = [
        unit_price["value"]["amount"]
        for contract in preview_agreement["contracts"]
        for unit_price in contract["unitPrices"]
        if unit_price["relatedItem"] == agreement["items"][0]["id"]
    ]
    self.assertNotEqual(real_unit_prices, preview_unit_prices)
    for i, v in enumerate(real_unit_prices):
        self.assertEqual(preview_unit_prices[i], v + 10)

    # activate change
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement_id, change_id, self.agreement_token),
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotIn("warnings", response.json)

    # get real agreement
    real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertEqual(real_agreement["changes"][-1]["status"], "active")
    self.assertEqual(real_agreement["contracts"], preview_agreement["contracts"])

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    preview_agreement = response.json["data"]
    self.assertNotIn("warnings", response.json)
    self.assertEqual(real_agreement, preview_agreement)


def agreement_change_item_price_variation_preview(self):
    agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertNotIn("changes", agreement)

    change_data = deepcopy(self.initial_change)
    change_data["rationaleType"] = "itemPriceVariation"
    change_data["modifications"] = [{"itemId": agreement["items"][0]["id"], "factor": 0.9}]

    # create itemPriceVariation change with addend
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": change_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertEqual(response.json["data"]["rationaleType"], "itemPriceVariation")
    self.assertEqual(response.json["data"]["modifications"], change_data["modifications"])
    self.assertNotIn("warnings", response.json)
    change_id = response.json["data"]["id"]

    real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertEqual(len(real_agreement["changes"]), 1)
    real_agreement.pop("changes")
    real_agreement.pop("dateModified")
    agreement.pop("dateModified")
    self.assertEqual(agreement, real_agreement)

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    preview_agreement = response.json["data"]
    self.assertNotIn("warnings", response.json)
    real_unit_prices = [
        unit_price["value"]["amount"]
        for contract in real_agreement["contracts"]
        for unit_price in contract["unitPrices"]
        if unit_price["relatedItem"] == agreement["items"][0]["id"]
    ]
    preview_unit_prices = [
        unit_price["value"]["amount"]
        for contract in preview_agreement["contracts"]
        for unit_price in contract["unitPrices"]
        if unit_price["relatedItem"] == agreement["items"][0]["id"]
    ]
    self.assertNotEqual(real_unit_prices, preview_unit_prices)
    for i, v in enumerate(real_unit_prices):
        self.assertEqual(preview_unit_prices[i], v * 0.9)

    # activate change
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement_id, change_id, self.agreement_token),
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotIn("warnings", response.json)

    # get real agreement
    response = self.app.get("/agreements/{}".format(self.agreement_id))
    real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertEqual(real_agreement["changes"][-1]["status"], "active")
    self.assertEqual(real_agreement["contracts"], preview_agreement["contracts"])

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    preview_agreement = response.json["data"]
    self.assertNotIn("warnings", response.json)
    self.assertEqual(real_agreement, preview_agreement)


def agreement_change_third_party_preview(self):
    agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertNotIn("changes", agreement)

    change_data = deepcopy(self.initial_change)
    change_data["rationaleType"] = "thirdParty"
    change_data["modifications"] = [{"itemId": agreement["items"][0]["id"], "factor": 0.1}]

    # create thirdParty change with addend
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": change_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertEqual(response.json["data"]["rationaleType"], "thirdParty")
    self.assertEqual(response.json["data"]["modifications"], change_data["modifications"])
    self.assertNotIn("warnings", response.json)
    change_id = response.json["data"]["id"]

    real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertEqual(len(real_agreement["changes"]), 1)
    real_agreement.pop("changes")
    real_agreement.pop("dateModified")
    agreement.pop("dateModified")
    self.assertEqual(agreement, real_agreement)

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    preview_agreement = response.json["data"]
    self.assertNotIn("warnings", response.json)
    real_unit_prices = [
        unit_price["value"]["amount"]
        for contract in real_agreement["contracts"]
        for unit_price in contract["unitPrices"]
        if unit_price["relatedItem"] == agreement["items"][0]["id"]
    ]
    preview_unit_prices = [
        unit_price["value"]["amount"]
        for contract in preview_agreement["contracts"]
        for unit_price in contract["unitPrices"]
        if unit_price["relatedItem"] == agreement["items"][0]["id"]
    ]
    self.assertNotEqual(real_unit_prices, preview_unit_prices)
    for i, v in enumerate(real_unit_prices):
        self.assertEqual(preview_unit_prices[i], v * 0.1)

    # activate change
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement_id, change_id, self.agreement_token),
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotIn("warnings", response.json)

    # get real agreement
    real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertEqual(real_agreement["changes"][-1]["status"], "active")
    self.assertEqual(real_agreement["contracts"], preview_agreement["contracts"])

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    preview_agreement = response.json["data"]
    self.assertNotIn("warnings", response.json)
    self.assertEqual(real_agreement, preview_agreement)


def agreement_change_party_withdrawal_preview(self):
    agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertNotIn("changes", agreement)

    change_data = deepcopy(self.initial_change)
    change_data["rationaleType"] = "partyWithdrawal"
    change_data["modifications"] = [{"contractId": agreement["contracts"][0]["id"]}]

    # create partyWithdrawal change with addend
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": change_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertEqual(response.json["data"]["rationaleType"], "partyWithdrawal")
    self.assertEqual(response.json["data"]["modifications"], change_data["modifications"])
    self.assertIn("warnings", response.json)
    self.assertEqual(response.json["warnings"], ["Min active contracts in FrameworkAgreement less than 3."])
    change_id = response.json["data"]["id"]

    real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertEqual(len(real_agreement["changes"]), 1)
    real_agreement.pop("changes")
    real_agreement.pop("dateModified")
    agreement.pop("dateModified")
    self.assertEqual(agreement, real_agreement)

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    preview_agreement = response.json["data"]
    self.assertIn("warnings", response.json)
    self.assertEqual(response.json["warnings"], ["Min active contracts in FrameworkAgreement less than 3."])
    real_contracts = [contract["status"] == "active" for contract in real_agreement["contracts"]]
    preview_contracts = [contract["status"] == "active" for contract in preview_agreement["contracts"]]
    self.assertNotEqual(real_contracts, preview_contracts)

    # activate change
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement_id, change_id, self.agreement_token),
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotIn("warnings", response.json)

    # get real agreement
    real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertEqual(real_agreement["changes"][-1]["status"], "active")
    self.assertEqual(real_agreement["contracts"], preview_agreement["contracts"])
    self.assertEqual(real_agreement["contracts"][0]["status"], "unsuccessful")

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    preview_agreement = response.json["data"]
    self.assertNotIn("warnings", response.json)
    self.assertEqual(real_agreement, preview_agreement)
    self.assertEqual(preview_agreement["contracts"][0]["status"], "unsuccessful")


def agreement_change_party_withdrawal_cancelled_preview(self):
    agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertNotIn("changes", agreement)

    change_data = deepcopy(self.initial_change)
    change_data["rationaleType"] = "partyWithdrawal"
    change_data["modifications"] = [{"contractId": agreement["contracts"][0]["id"]}]

    # create partyWithdrawal change with addend
    response = self.app.post_json(
        "/agreements/{}/changes?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": change_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertEqual(response.json["data"]["rationaleType"], "partyWithdrawal")
    self.assertEqual(response.json["data"]["modifications"], change_data["modifications"])
    self.assertIn("warnings", response.json)
    self.assertEqual(response.json["warnings"], ["Min active contracts in FrameworkAgreement less than 3."])
    change_id = response.json["data"]["id"]

    real_agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertEqual(len(real_agreement["changes"]), 1)
    real_agreement.pop("changes")
    real_agreement.pop("dateModified")
    agreement.pop("dateModified")
    self.assertEqual(agreement, real_agreement)

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    preview_agreement = response.json["data"]
    self.assertIn("warnings", response.json)
    self.assertEqual(response.json["warnings"], ["Min active contracts in FrameworkAgreement less than 3."])
    real_contracts = [contract["status"] == "active" for contract in real_agreement["contracts"]]
    preview_contracts = [contract["status"] == "active" for contract in preview_agreement["contracts"]]
    self.assertNotEqual(real_contracts, preview_contracts)
    self.assertEqual(preview_agreement["contracts"][0]["status"], "unsuccessful")

    # cancel change
    response = self.app.patch_json(
        "/agreements/{}/changes/{}?acc_token={}".format(self.agreement_id, change_id, self.agreement_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertNotIn("warnings", response.json)

    # get real agreement
    response = self.app.get("/agreements/{}".format(self.agreement_id))
    real_agreement = response.json["data"]
    self.assertEqual(real_agreement["changes"][-1]["status"], "cancelled")
    self.assertNotEqual(real_agreement["contracts"], preview_agreement["contracts"])
    self.assertEqual(real_agreement["contracts"][0]["status"], "active")
    self.assertNotIn("warnings", response.json)

    response = self.app.get("/agreements/{}/preview".format(self.agreement_id))
    preview_agreement = response.json["data"]
    self.assertEqual(real_agreement, preview_agreement)
    self.assertEqual(preview_agreement["contracts"][0]["status"], "active")
    self.assertNotIn("warnings", response.json)


def agreement_changes_patch_from_agreements(self):
    agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertNotIn("changes", agreement)

    change_data = deepcopy(self.initial_change)
    change_data["rationaleType"] = "partyWithdrawal"
    change_data["modifications"] = [{"contractId": agreement["contracts"][0]["id"]}]

    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement_id, self.agreement_token),
        {"data": {"changes": [change_data]}},
    )
    self.assertEqual(response.status_code, 200)
    agreement = self.app.get("/agreements/{}".format(self.agreement_id)).json["data"]
    self.assertNotIn("changes", agreement)


def create_agreement_with_two_active_contracts(self):
    data = self.initial_data
    data["id"] = uuid.uuid4().hex
    data["contracts"][0]["status"] = "unsuccessful"
    with change_auth(self.app, ("Basic", ("agreements", ""))) as app:
        response = self.app.post_json("/agreements", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["agreementID"], data["agreementID"])

    response = self.app.get("/agreements/{}".format(data["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["id"], data["id"])
    self.assertEqual(
        response.json["data"]["numberOfContracts"], len([c["id"] for c in data["contracts"] if c["status"] == "active"])
    )


def agreement_token_invalid(self):
    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement_id, "fake token"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}]
    )

    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement_id, "токен з кирилицею"), {"data": {}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"], [
            {
                'location': 'body', 'name': 'UnicodeEncodeError',
                'description': "'latin-1' codec can't encode characters in position 10-14: ordinal not in range(256)"
            }
        ]
    )


def generate_credentials_invalid(self):
    response = self.app.patch_json(
        "/agreements/{0}/credentials?acc_token={1}".format(self.agreement_id, "fake token"), {"data": ""}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}]
    )

    response = self.app.patch_json(
        "/agreements/{0}/credentials?acc_token={1}".format(self.agreement_id, "токен з кирилицею"),
        {"data": ""},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"], [
            {
                'location': 'body', 'name': 'UnicodeEncodeError',
                'description': "'latin-1' codec can't encode characters in position 10-14: ordinal not in range(256)"
            }
        ]
    )


def skip_address_validation(self):
    data = deepcopy(self.initial_data)
    data["contracts"][1]["suppliers"][0]["address"]["countryName"] = "any country"
    data["contracts"][1]["suppliers"][0]["address"]["region"] = "any region"
    data["id"] = uuid.uuid4().hex

    with change_auth(self.app, ("Basic", ("agreements", ""))) as app:
        response = self.app.post_json("/agreements", {"data": data})
    self.assertEqual(response.status, "201 Created")



