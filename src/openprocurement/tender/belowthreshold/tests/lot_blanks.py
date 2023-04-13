import mock
from unittest.mock import patch
from copy import deepcopy
from datetime import timedelta
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_cancellation,
)


# Tender Lot Resouce Test


def create_tender_lot_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/lots", {"data": {"title": "lot title", "description": "lot description"}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    request_path = "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token)

    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
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

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {"description": ["This field is required."], "location": "body", "name": "title"},
            {"description": ["This field is required."], "location": "body", "name": "value"},
        ],
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"value": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Please use a mapping for this field or PostValue instance instead of str."],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "title": "lot title",
                "description": "lot description",
                "value": {"amount": "100.0"},
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "minimalStep"}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "title": "lot title",
                "description": "lot description",
                "value": {"amount": "100.0"},
                "minimalStep": {"amount": "500.0"},
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["value should be less than value of lot"], "location": "body", "name": "minimalStep"}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "title": "lot title",
                "description": "lot description",
                "value": {"amount": "500.0"},
                "minimalStep": {"amount": "15.0", "currency": "USD"},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    # but minimalStep currency stays unchanged
    response = self.app.get(request_path)
    self.assertEqual(response.content_type, "application/json")
    lots = response.json["data"]
    self.assertEqual(len(lots), 1 + len(getattr(self, 'initial_lots', None) or []))
    self.assertEqual(lots[-1]["minimalStep"]["currency"], "UAH")
    self.assertEqual(lots[-1]["minimalStep"]["amount"], 15)

    items = deepcopy(self.initial_data["items"])
    items[0]["relatedLot"] = "0" * 32
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedLot": ["relatedLot should be one of lots"]}],
                "location": "body",
                "name": "items",
            }
        ],
    )


def create_tender_lot(self):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["title"], "lot title")
    self.assertEqual(lot["description"], "lot description")
    self.assertIn("id", lot)
    self.assertIn(lot["id"], response.headers["Location"])
    self.assertNotIn("guarantee", lot)
    if "auctionPeriod" in lot:
        del lot["auctionPeriod"]

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertNotIn("guarantee", response.json["data"])

    lot2 = deepcopy(self.test_lots_data[0])
    lot2["guarantee"] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot2}
    )
    self.assertEqual(response.status, "201 Created")
    data = response.json["data"]
    self.assertIn("guarantee", data)
    self.assertEqual(data["guarantee"]["amount"], 100500)
    self.assertEqual(data["guarantee"]["currency"], "USD")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")
    self.assertNotIn("guarantee", response.json["data"]["lots"][0])

    # TODO: this validation is useless cause there are serializers core/models.py:2139-2163 and in core/procedure/models/lot.py:64-94
    # So no reason if we add lot from view to be different from tender values

    lot3 = deepcopy(self.test_lots_data[0])
    # lot3["guarantee"] = {"amount": 500, "currency": "UAH"}
    # response = self.app.post_json(
    #     "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot3}
    # )
    # self.assertEqual(response.status, "422 Unprocessable Entity")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["status"], "error")
    # self.assertEqual(
    #     response.json["errors"],
    #     [
    #         {
    #             "description": ["lot guarantee currency should be identical to tender guarantee currency"],
    #             "location": "body",
    #             "name": "lots",
    #         }
    #     ],
    # )


    #
    # lot3["guarantee"] = {"amount": 500}
    # response = self.app.post_json(
    #     "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot3}, status=422
    # )
    # self.assertEqual(response.status, "422 Unprocessable Entity")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["status"], "error")
    # self.assertEqual(
    #     response.json["errors"],
    #     [
    #         {
    #             "description": ["lot guarantee currency should be identical to tender guarantee currency"],
    #             "location": "body",
    #             "name": "lots",
    #         }
    #     ],
    # )

    lot3["guarantee"] = {"amount": 20, "currency": "USD"}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot3}
    )
    self.assertEqual(response.status, "201 Created")
    data = response.json["data"]
    self.assertIn("guarantee", data)
    self.assertEqual(data["guarantee"]["amount"], 20)
    self.assertEqual(data["guarantee"]["currency"], "USD")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500 + 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"guarantee": {"currency": "EUR", "amount": 20}}},
    )
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500 + 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "EUR")
    self.assertNotIn("guarantee", response.json["data"]["lots"][0])
    self.assertEqual(response.json["data"]["lots"][-2]["guarantee"]["amount"], 100500)
    self.assertEqual(response.json["data"]["lots"][-2]["guarantee"]["currency"], "EUR")
    self.assertEqual(response.json["data"]["lots"][-1]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["lots"][-1]["guarantee"]["currency"], "EUR")

    del lot["date"]
    if "minValue" in lot:
        del lot["minValue"]
    if "fundingKind" in lot:
        del lot["fundingKind"]

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Lot id should be uniq for all lots", "location": "body", "name": "lots"}],
    )

    self.set_status("{}".format(self.forbidden_lot_actions_status))

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": self.test_lots_data[0]},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add lot in current ({}) tender status".format(self.forbidden_lot_actions_status),
    )


def create_tender_lot_minimalstep_validation(self):
    data = deepcopy(self.test_lots_data)[0]
    data["minimalStep"]["amount"] = 35
    request_path = "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token)
    with mock.patch("openprocurement.tender.core.procedure.models.lot.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.post_json(request_path, {"data": data}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{"description": ["minimalstep must be between 0.5% and 3% of value (with 2 digits precision)."],
              "location": "body", "name": "minimalStep"}],
        )

    with mock.patch("openprocurement.tender.core.procedure.models.lot.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() + timedelta(days=1)):
        response = self.app.post_json(request_path, {"data": data}, status=201)
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


def patch_tender_lot(self):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"title": "new title"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["title"], "new title")

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"guarantee": {"amount": 12, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    guarantee = response.json["data"]["guarantee"]
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"guarantee": {**guarantee, "currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    # Deleted self.assertEqual(response.body, 'null') to make this test OK in other procedures, because there is a bug with invalidation bids at openua, openeu and openuadefence that makes body not null

    response = self.app.patch_json(
        "/tenders/{}/lots/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"title": "other title"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "lot_id"}])

    response = self.app.patch_json("/tenders/some_id/lots/some_id", {"data": {"title": "other title"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["title"], "new title")

    self.set_status("{}".format(self.forbidden_lot_actions_status))

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"title": "other title"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update lot in current ({}) tender status".format(self.forbidden_lot_actions_status),
    )


def patch_tender_lot_minimalstep_validation(self):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    with mock.patch("openprocurement.tender.core.procedure.models.lot.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.patch_json(
            "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
            {"data": {"minimalStep": {**lot["minimalStep"], "amount": 100.0}}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{"description": ["minimalstep must be between 0.5% and 3% of value (with 2 digits precision)."],
              "location": "body", "name": "minimalStep"}],
        )
    with mock.patch("openprocurement.tender.core.procedure.models.lot.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() + timedelta(days=1)):
        response = self.app.patch_json(
            "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
            {"data": {"minimalStep": {**lot["minimalStep"], "amount": 100.0}}},
            status=200,
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")


def patch_tender_currency(self):
    # create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["value"]["currency"], "UAH")

    # update tender currency without mimimalStep currency change
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"currency": "GBP", "amount": 1000}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["currency should be identical to currency of value of tender"],
                "location": "body",
                "name": "minimalStep",
            }
        ]
    )

    # update tender currency
    items = deepcopy(self.initial_data["items"])
    for i in items:
        i["unit"]["value"]["currency"] = "GBP"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {
            "value": {"currency": "GBP", "amount": 1000},
            "minimalStep": {"currency": "GBP", "amount": 1},
            "items": items,
        }},
    )
    self.assertEqual(response.status, "200 OK")
    lots_test = response.json["data"]["lots"]
    # log currency is updated too
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["value"]["currency"], "GBP")

    # try to update lot currency
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"value": {**lot["value"], "currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["value"]["currency"], "GBP")

    # try to update minimalStep currency
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"minimalStep": {**lot["minimalStep"], "currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["minimalStep"]["currency"], "GBP")

    # try to update lot minimalStep currency and lot value currency in single request
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {
            "value": {**lot["value"], "currency": "USD"},
            "minimalStep": {**lot["minimalStep"], "currency": "USD"},
        }},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["value"]["currency"], "GBP")
    self.assertEqual(lot["minimalStep"]["currency"], "GBP")


def patch_tender_vat(self):
    tender = self.initial_data
    # set tender VAT
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": True, "amount": tender["value"]["amount"]}}},
    )
    self.assertEqual(response.status, "200 OK")

    # create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertTrue(lot["value"]["valueAddedTaxIncluded"])

    # update tender VAT
    items = deepcopy(self.initial_data["items"])
    for i in items:
        i["unit"]["value"]["valueAddedTaxIncluded"] = False
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False, "amount": tender["value"]["amount"]},
                  "minimalStep": {"valueAddedTaxIncluded": False, "amount": tender["minimalStep"]["amount"]},
                  "items": items,
                  }},
    )
    self.assertEqual(response.status, "200 OK")
    # log VAT is updated too
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertFalse(lot["value"]["valueAddedTaxIncluded"])

    # try to update lot VAT
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"value": {**lot["value"], "valueAddedTaxIncluded": True}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertFalse(lot["value"]["valueAddedTaxIncluded"])

    # try to update minimalStep VAT
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"minimalStep": {**lot["minimalStep"], "valueAddedTaxIncluded": True}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertFalse(lot["minimalStep"]["valueAddedTaxIncluded"])

    # try to update minimalStep VAT and value VAT in single request
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {
            "value": {**lot["value"], "valueAddedTaxIncluded": True},
            "minimalStep": {**lot["minimalStep"], "valueAddedTaxIncluded": True},
        }},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertFalse(lot["value"]["valueAddedTaxIncluded"])
    self.assertEqual(lot["minimalStep"]["valueAddedTaxIncluded"], lot["value"]["valueAddedTaxIncluded"])


def get_tender_lot(self):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        set(response.json["data"]), {"id", "date", "title", "description", "minimalStep", "value", "status"}
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    api_lot = response.json["data"]
    if "auctionPeriod" in api_lot:
        api_lot.pop("auctionPeriod")
    self.assertEqual(api_lot, lot)

    response = self.app.get("/tenders/{}/lots/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "lot_id"}])

    response = self.app.get("/tenders/some_id/lots/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def get_tender_lots(self):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]

    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        set(response.json["data"][0]),
        {"id", "date", "title", "description", "minimalStep", "value", "status"},
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    api_lot = response.json["data"][0]
    if "auctionPeriod" in api_lot:
        api_lot.pop("auctionPeriod")
    self.assertEqual(api_lot, lot)

    response = self.app.get("/tenders/some_id/lots", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def delete_tender_lot(self):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]

    response = self.app.delete("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], lot)

    response = self.app.delete(
        "/tenders/{}/lots/some_id?acc_token={}".format(self.tender_id, self.tender_token), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "lot_id"}])

    response = self.app.delete("/tenders/some_id/lots/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]

    items = deepcopy(self.initial_data["items"])
    items[0]["relatedLot"] = lot["id"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Cannot delete lot with related items",
                "location": "body",
                "name": "data",
            }
        ],
    )

    self.set_status("{}".format(self.forbidden_lot_actions_status))

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't delete lot in current ({}) tender status".format(self.forbidden_lot_actions_status),
    )


def tender_lot_guarantee(self):
    data = deepcopy(self.initial_data)
    data["guarantee"] = {"amount": 100, "currency": "USD"}
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    tender = response.json["data"]
    tender_token = response.json["access"]["token"]
    self.assertEqual(response.status, "201 Created")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    lot = deepcopy(self.test_lots_data[0])
    lot["guarantee"] = {"amount": 20, "currency": "USD"}
    response = self.app.post_json("/tenders/{}/lots?acc_token={}".format(tender["id"], tender_token), {"data": lot})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], tender_token),
        {"data": {"guarantee": {"currency": "GBP", "amount": 20}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    lot["guarantee"] = {"amount": 20, "currency": "GBP"}
    response = self.app.post_json("/tenders/{}/lots?acc_token={}".format(tender["id"], tender_token), {"data": lot})
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20 + 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    lot2 = deepcopy(self.test_lots_data[0])
    lot2["guarantee"] = {"amount": 30, "currency": "GBP"}
    response = self.app.post_json("/tenders/{}/lots?acc_token={}".format(tender["id"], tender_token), {"data": lot2})
    self.assertEqual(response.status, "201 Created")
    lot2_id = response.json["data"]["id"]
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 30)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    lot2["guarantee"] = {"amount": 40, "currency": "USD"}
    # currency stay unchanged
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender["id"], tender_token), {"data": lot2}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 40)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20 + 20 + 30 + 40)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], tender_token),
        {"data": {"guarantee": {"amount": 55, "currency": "GBP"}}}
    )
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20 + 20 + 30 + 40)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(tender["id"], lot2_id, tender_token),
        {"data": {"guarantee": {"amount": 35, "currency": "GBP"}}},
    )
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 35)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20 + 20 + 35 + 40)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    for l_id in (lot_id, lot2_id):
        response = self.app.patch_json(
            "/tenders/{}/lots/{}?acc_token={}".format(tender["id"], l_id, tender_token),
            {"data": {"guarantee": {"amount": 0, "currency": "GBP"}}},
        )
        self.assertEqual(response.json["data"]["guarantee"]["amount"], 0)
        self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20 + 40)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    for l_id in (lot_id, lot2_id):
        response = self.app.delete("/tenders/{}/lots/{}?acc_token={}".format(tender["id"], l_id, tender_token))
        self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20 + 40)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")


# Tender Lot Feature Resource Test


def tender_value(self):
    request_path = "/tenders/{}".format(self.tender_id)
    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], sum([i["value"]["amount"] for i in self.initial_lots]))
    self.assertEqual(
        response.json["data"]["minimalStep"]["amount"], min([i["minimalStep"]["amount"] for i in self.initial_lots])
    )


@patch("openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
       get_now() + timedelta(days=1))
def tender_features_invalid(self):
    request_path = "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)
    item = deepcopy(self.initial_data["items"][0])
    item["id"] = "1"
    data = {
        "items": [item],
        "features": [
            {
                "featureOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "title": "Потужність всмоктування",
                "enum": [
                    {"value": self.invalid_feature_value, "title": "До 1000 Вт"},
                    {"value": 0.15, "title": "Більше 1000 Вт"},
                ],
            }
        ]
    }
    response = self.app.patch_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    {"enum": [{"value": ["Float value should be less than {}.".format(self.max_feature_value)]}]}
                ],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["enum"][0]["value"] = 0.1
    data["features"].append(data["features"][0].copy())
    data["features"][1]["enum"][0]["value"] = self.sum_of_max_value_of_all_features
    response = self.app.patch_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "Sum of max value of all features for lot should be less then or equal to {0:.0%}".format(
                        self.sum_of_max_value_of_all_features
                    )
                ],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][1]["enum"][0]["value"] = 0.1
    data["features"].append(data["features"][0].copy())
    data["features"][2]["relatedItem"] = self.initial_lots[1]["id"]
    data["features"].append(data["features"][2].copy())
    response = self.app.patch_json(request_path, {"data": data})
    self.assertEqual(response.status, "200 OK")


def tender_lot_document(self):
    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {
            "title": "укр.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    # dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("укр.doc", response.json["data"]["title"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"documentOf": "lot"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "relatedItem"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"documentOf": "lot", "relatedItem": "0" * 32}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["relatedItem should be one of lots"], "location": "body", "name": "relatedItem"}],
    )

    # get tender for lot id
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), status=200)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    # add document with lot_id
    lot_id = tender["lots"][0]["id"]
    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"documentOf": "lot", "relatedItem": lot_id}},
        status=200,
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["relatedItem"], lot_id)


# Tender Lot Bid Resource Test


def create_tender_bid_invalid(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    response = self.app.post_json(request_path, {"data": {"tenderers": [test_tender_below_organization]}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "lotValues"}],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 500}}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedLot": ["This field is required."]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 500}, "relatedLot": "0" * 32}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedLot": ["relatedLot should be one of lots"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 5000000}, "relatedLot": self.initial_lots[0]["id"]}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"value": ["value of bid should be less than value of lot"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [
                    {"value": {"amount": 500, "valueAddedTaxIncluded": False}, "relatedLot": self.initial_lots[0]["id"]}
                ],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    {
                        "value": [
                            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"
                        ]
                    }
                ],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 500, "currency": "USD"}, "relatedLot": self.initial_lots[0]["id"]}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"value": ["currency of bid should be identical to currency of value of lot"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "value": {"amount": 500},
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["value should be posted for each lot of bid"], "location": "body", "name": "value"}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": test_tender_below_organization,
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("invalid literal for int() with base 10", response.json["errors"][0]["description"])

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [
                    {"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]},
                    {"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]},
                ],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["bids don't allow duplicated proposals"], "location": "body", "name": "lotValues"}],
    )


def patch_tender_bid(self):
    lot_id = self.initial_lots[0]["id"]
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    token = response.json["access"]["token"]
    lot = bid["lotValues"][0]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"tenderers": [{"name": "Державне управління управлінням справами"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}], "tenderers": [test_tender_below_organization]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"lotValues": [{"value": {"amount": 400}, "relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])


# Tender Lot Feature Bid Resource Test


def create_tender_bid_invalid_feature(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    response = self.app.post_json(request_path, {"data": {"tenderers": [test_tender_below_organization]}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {"description": ["All features parameters is required."], "location": "body", "name": "parameters"},
            {"description": ["This field is required."], "location": "body", "name": "lotValues"},
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 500}}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedLot": ["This field is required."]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 500}, "relatedLot": "0" * 32}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedLot": ["relatedLot should be one of lots"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 5000000}, "relatedLot": self.lot_id}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"value": ["value of bid should be less than value of lot"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 500, "valueAddedTaxIncluded": False}, "relatedLot": self.lot_id}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    {
                        "value": [
                            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"
                        ]
                    }
                ],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 500, "currency": "USD"}, "relatedLot": self.lot_id}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"value": ["currency of bid should be identical to currency of value of lot"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": test_tender_below_organization,
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("invalid literal for int() with base 10", response.json["errors"][0]["description"])

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["All features parameters is required."], "location": "body", "name": "parameters"}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
                "parameters": [{"code": "code_item", "value": 0.01}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["All features parameters is required."], "location": "body", "name": "parameters"}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
                "parameters": [{"code": "code_invalid", "value": 0.01}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"code": ["code should be one of feature code."]}],
                "location": "body",
                "name": "parameters",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
                "parameters": [
                    {"code": "code_item", "value": 0.01},
                    {"code": "code_tenderer", "value": 0},
                    {"code": "code_lot", "value": 0.01},
                ],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"value": ["value should be one of feature value."]}],
                "location": "body",
                "name": "parameters",
            }
        ],
    )


def create_tender_bid_feature(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
                "parameters": [
                    {"code": "code_item", "value": 0.01},
                    {"code": "code_tenderer", "value": 0.01},
                    {"code": "code_lot", "value": 0.01},
                ],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], test_tender_below_organization["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    self.set_status("complete")

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_below_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
                "parameters": [
                    {"code": "code_item", "value": 0.01},
                    {"code": "code_tenderer", "value": 0.01},
                    {"code": "code_lot", "value": 0.01},
                ],
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


# Tender Lot Process Test


def proc_1lot_0bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    # add relatedLot for item
    items = deepcopy(self.initial_data["items"])
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
            ]
        },
    )
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # switch to unsuccessful
    response = self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}}], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["lots"][0]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def proc_1lot_1bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    # add relatedLot for item
    items = deepcopy(self.initial_data["items"])
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
            ]
        },
    )
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}]}
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    # switch to active.qualification
    response = self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}}], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def proc_1lot_2bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    self.initial_lots = [response.json["data"]]
    # add relatedLot for item
    items = deepcopy(self.initial_data["items"])
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
            ]
        },
    )
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 450}, "relatedLot": lot_id}]}
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    bid_id = bid["id"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 475}, "relatedLot": lot_id}]}
    self.create_bid(self.tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction")
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    response = self.app.patch_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {
            "data": {
                "lots": [
                    {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
                ],
                "bids": [
                    {
                        "id": i["id"],
                        "lotValues": [
                            {
                                "relatedLot": j["relatedLot"],
                                "participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"]),
                            }
                            for j in i["lotValues"]
                        ],
                    }
                    for i in auction_bids_data
                ],
            }
        },
    )
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {"data": {"bids": [{"lotValues": b["lotValues"]} for b in auction_bids_data]}}
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def proc_2lot_0bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    self.assertTrue(all(["auctionPeriod" in i for i in response.json["data"]["lots"]]))
    # switch to unsuccessful
    response = self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    self.assertTrue(all([i["status"] == "unsuccessful" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def proc_2lot_2can(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]

    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    self.assertTrue(all(["auctionPeriod" in i for i in response.json["data"]["lots"]]))

    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)

    if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
        set_complaint_period_end()

    # cancel every lot
    for lot_id in lots:
        cancellation = dict(**test_tender_below_cancellation)
        cancellation.update({
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": lot_id,
        })
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
            {"data": cancellation},
        )
        cancellation_id = response.json["data"]["id"]
        if RELEASE_2020_04_19 < get_now():
            activate_cancellation_after_2020_04_19(self, cancellation_id, tender_id, owner_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "cancelled" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def proc_2lot_2bid_0com_1can_before_auction(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {
        "tenderers": [test_tender_below_organization],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots],
    }
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    # for first lot
    lot_id = lots[0]
    # create bid #2 for 1 lot
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}]}},
    )
    # cancel lot
    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": lot_id,
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )

    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id, tender_id, owner_token)

    # switch to active.qualification
    response = self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = get_now().isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # check tender status
    response = self.check_chronograph()
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual([i["status"] for i in response.json["data"]["lots"]], ["cancelled", "unsuccessful"])
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def proc_2lot_1bid_0com_1can(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {
        "tenderers": [test_tender_below_organization],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots],
    }
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    # switch to active.qualification
    response = self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    # for first lot
    lot_id = lots[0]
    # cancel lot
    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": lot_id,
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id, tender_id, owner_token)
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = get_now().isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # check tender status
    response = self.check_chronograph()
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual([i["status"] for i in response.json["data"]["lots"]], ["cancelled", "unsuccessful"])
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def proc_2lot_1bid_2com_1win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {
        "tenderers": [test_tender_below_organization],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots],
    }
    self.create_bid(self.tender_id, bid_data)
    # switch to active.qualification
    response = self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    for lot_id in lots:
        # get awards
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
        # get pending award
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
        # set award as active
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
            {"data": {"status": "active"}},
        )
        # get contract id
        response = self.app.get("/tenders/{}".format(tender_id))
        contract = response.json["data"]["contracts"][-1]
        contract_id = contract["id"]
        contract_value = deepcopy(contract["value"])
        # after stand slill period
        self.set_status("complete", {"status": "active.awarded"})
        # time travel
        tender = self.mongodb.tenders.get(tender_id)
        now = (get_now() - timedelta(minutes=2)).isoformat()
        for i in tender.get("awards", []):
            i["complaintPeriod"] = {"startDate": now, "endDate": now}
        self.mongodb.tenders.save(tender)
        # sign contract
        self.app.authorization = ("Basic", ("broker", ""))
        contract_value["valueAddedTaxIncluded"] = False
        self.app.patch_json(
            "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
            {"data": {"status": "active", "value": contract_value}},
        )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "complete" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "complete")


def proc_2lot_1bid_0com_0win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {
        "tenderers": [test_tender_below_organization],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots],
    }

    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    # switch to active.qualification
    response = self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    # for every lot
    for lot_id in lots:
        # get awards
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
        # get pending award
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
        # set award as unsuccessful
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
            {"data": {"status": "unsuccessful"}},
        )
        # after stand slill period
        self.set_status("complete", {"status": "active.awarded"})
        # time travel
        tender = self.mongodb.tenders.get(tender_id)
        now = get_now().isoformat()
        for i in tender.get("awards", []):
            i["complaintPeriod"] = {"startDate": now, "endDate": now}
        self.mongodb.tenders.save(tender)
    # check tender status
    self.set_status("complete", {"status": "active.awarded"})
    response = self.check_chronograph()
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "unsuccessful" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def proc_2lot_1bid_1com_1win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {
        "tenderers": [test_tender_below_organization],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots],
    }
    self.create_bid(self.tender_id, bid_data)
    # switch to active.qualification
    response = self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # check tender status
    response = self.check_chronograph()
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual([i["status"] for i in response.json["data"]["lots"]], ["complete", "unsuccessful"])
    self.assertEqual(response.json["data"]["status"], "complete")


def proc_2lot_2bid_2com_2win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {
        "tenderers": [test_tender_below_organization],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots],
    }
    self.create_bid(self.tender_id, bid_data)
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(self.tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction")
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for lot_id in lots:
        # posting auction urls
        response = self.app.patch_json(
            "/tenders/{}/auction/{}".format(tender_id, lot_id),
            {
                "data": {
                    "lots": [
                        {"id": i["id"], "auctionUrl": "https://tender.auction.url"}
                        for i in response.json["data"]["lots"]
                    ],
                    "bids": [
                        {
                            "id": i["id"],
                            "lotValues": [
                                {
                                    "relatedLot": j["relatedLot"],
                                    "participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"]),
                                }
                                for j in i["lotValues"]
                            ],
                        }
                        for i in auction_bids_data
                    ],
                }
            },
        )
        # posting auction results
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(tender_id, lot_id),
            {"data": {"bids": [{"lotValues": b["lotValues"]} for b in auction_bids_data]}}
        )
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(minutes=2)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(minutes=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "complete" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "complete")


def proc_2lot_1feature_2bid_2com_2win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    # add features
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {
            "data": {
                "features": [
                    {
                        "code": "code_item",
                        "featureOf": "item",
                        "relatedItem": response.json["data"]["items"][0]["id"],
                        "title": "item feature",
                        "enum": [{"value": 0.1, "title": "good"}, {"value": 0.2, "title": "best"}],
                    }
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {
        "tenderers": [test_tender_below_organization],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lots[0]}],
        "parameters": [{"code": "code_item", "value": 0.2}],
    }
    self.create_bid(self.tender_id, bid_data)
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 500}, "relatedLot": lots[1]}]}
    self.create_bid(self.tender_id, bid_data)
    # switch to active.qualification
    response = self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(minutes=2)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(minutes=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "complete" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "complete")


def proc_2lot_2diff_bids_check_auction(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id

    # import pdb; pdb.set_trace()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {
                    "auctionPeriod": {
                        "startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
                    }
                }
                for i in lots
            ]
        },
    )
    # create bid (for 2 lots)
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {
        "tenderers": [test_tender_below_organization],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots],
    }
    self.create_bid(self.tender_id, bid_data)
    # create second bid (only for 1 lot)
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "lotValues": [{"value": {"amount": 500}, "relatedLot": lots[0]}]}
    self.create_bid(self.tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction")
    self.check_chronograph()
    # check lots auction period
    # first lot (with 2 bids) should have 'start date' and 'should start after' field
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    self.assertIn("startDate", response.json["data"]["lots"][0]["auctionPeriod"])
    self.assertIn("shouldStartAfter", response.json["data"]["lots"][0]["auctionPeriod"])
    # second lot (with only 1 bid) should have 'start date' and no 'should start after' field
    self.assertIn("auctionPeriod", response.json["data"]["lots"][1])
    self.assertIn("startDate", response.json["data"]["lots"][1]["auctionPeriod"])
    self.assertNotIn("shouldStartAfter", response.json["data"]["lots"][1]["auctionPeriod"])


def tender_lot_milestones(self):
    # add lot
    response = self.app.get("/tenders/{}".format(self.tender_id))
    response_data = response.json["data"]
    if "lots" in response_data:
        lot = response_data["lots"][0]
    else:
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lot = response.json["data"]
    # add milestones
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "milestones": [
                    {  # without relatedLot
                        "title": "signingTheContract",
                        "code": "prepayment",
                        "type": "financing",
                        "duration": {"days": 2, "type": "banking"},
                        "sequenceNumber": 0,
                        "percentage": 100,
                    },
                    {
                        "title": "signingTheContract",
                        "code": "prepayment",
                        "type": "financing",
                        "duration": {"days": 999, "type": "calendar"},
                        "sequenceNumber": 2,
                        "percentage": 100,
                        "relatedLot": lot["id"],
                    },
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    # try to delete the lot
    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertIn(
        {
            "location": "body",
            "name": "data",
            "description": "Cannot delete lot with related milestones"
        },
        response.json["errors"],
    )
