from copy import deepcopy
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.models import get_now
from openprocurement.tender.core.tests.cancellation import activate_cancellation_after_2020_04_19
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_complaint,
    test_tender_below_cancellation,
)

# TenderLotNegotiationResourceTest


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

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
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
    del lot["date"]
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


def create_complete_tender_lot(self):
    """ Can't create lot when tender status is complete """
    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": self.test_lots_data[0]},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't add lot in current (complete) tender status",
            }
        ],
    )


def create_cancelled_tender_lot(self):
    """ Can't create lot when tender status is cancelled """
    self.set_status("cancelled")

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": self.test_lots_data[0]},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't add lot in current (cancelled) tender status",
            }
        ],
    )


def create_unsuccessful_tender_lot(self):
    """ Can't create lot when tender status is unsuccessful """
    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": self.test_lots_data[0]},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't add lot in current (unsuccessful) tender status",
            }
        ],
    )


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
        {"data": {"description": "new description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["description"], "new description")

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"value": {**lot["value"], "amount": 400}}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)

    response = self.app.patch_json(
        "/tenders/{}/lots/some_id".format(self.tender_id), {"data": {"title": "other title"}}, status=404
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

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"title": "other title"}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update lot in current (complete) tender status")


def patch_tender_currency(self):
    # create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["value"]["currency"], "UAH")

    # update tender currency
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {
            "value": {"currency": "GBP", "amount": tender["value"]["amount"]}
        }}
    )

    self.assertEqual(response.status, "200 OK")
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

    # try to update lot minimalStep currency and lot value currency in single request
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


def patch_tender_vat(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

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
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False, "amount": tender["value"]["amount"]}}},
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

    # try to update value VAT in single request
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


def delete_unsuccessful_tender_lot(self):
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

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
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
                "location": "body",
                "name": "data",
                "description": "Cannot delete lot with related items"
            }
        ],
    )
    self.set_status("unsuccessful")

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't delete lot in current (unsuccessful) tender status"
    )

    response = self.app.get("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token))
    self.assertEqual(response.status, "200 OK")


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

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
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
                "location": "body",
                "name": "data",
                "description": "Cannot delete lot with related items"
            }
        ],
    )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = None
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.delete("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token))

    self.assertEqual(response.status, "200 OK")

    response = self.app.get(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "lot_id"}])


def delete_complete_tender_lot(self):
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

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
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
                "location": "body",
                "name": "data",
                "description": "Cannot delete lot with related items"
            }
        ],
    )
    self.set_status("complete")

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't delete lot in current (complete) tender status")

    response = self.app.get("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token))
    self.assertEqual(response.status, "200 OK")


def cancel_lot_after_sing_contract(self):
    # Create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]

    #  Update item with relatedLot field
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = lot["id"]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )
    # Create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "qualified": True,
                "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                "lotID": lot["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    award = response.json["data"]

    # Activate award
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    # Activate contract
    contract["value"]["valueAddedTaxIncluded"] = False
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active", "value": contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # try to cancel lot
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": lot["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't perform cancellation in current (complete) tender status",
            }
        ],
    )


def cancel_lot_with_complaint(self):
    # Create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = lot["id"]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )

    # Create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "qualified": True,
                "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                "lotID": lot["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    award = response.json["data"]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # Create complaints
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints".format(self.tender_id, award["id"]),
        {
            "data": test_tender_below_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if RELEASE_2020_04_19 < get_now():
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(
                    self.tender_id, award["id"], complaint["id"]),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    # set complaint status invalid to be able to cancel the lot
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, award["id"], response.json["data"]["id"], owner_token
            ),
            {"data": {
                "status": "invalid",
                "rejectReason": "buyerViolationsCorrected"
            }},
        )
        self.assertEqual(response.status, "200 OK")

    self.set_all_awards_complaint_period_end()
    # Try to cancel lot
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": lot["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]

    if RELEASE_2020_04_19 > get_now():
        self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(
                self.tender_id, cancellation_id, self.tender_token
            ),
            {"data": {"status": "active"}},
        )

    else:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    # Check lot status
    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    self.assertEqual(response.json["data"][0]["status"], "cancelled")


def last_lot_complete(self):
    # Create 3 lots and update related items
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    first_lot = response.json["data"]
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    second_lot = response.json["data"]
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    third_lot = response.json["data"]

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = first_lot["id"]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )

    items[0]["relatedLot"] = second_lot["id"]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )

    items[0]["relatedLot"] = third_lot["id"]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )

    # Cancel 1 lot
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": first_lot["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 > get_now():
        self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(
                self.tender_id, cancellation_id, self.tender_token
            ),
            {"data": {"status": "active"}},
        )

    else:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, first_lot["id"]))
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # create awards for second and third
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "qualified": True,
                "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                "lotID": second_lot["id"],
            }
        },
    )
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, response.json["data"]["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "qualified": True,
                "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                "lotID": third_lot["id"],
            }
        },
    )
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, response.json["data"]["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    # Sign in contracts
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    first_contract = response.json["data"][0]
    second_contract = response.json["data"][1]
    first_contract["value"]["valueAddedTaxIncluded"] = False
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, first_contract["id"], self.tender_token),
        {"data": {"status": "active", "value": first_contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    second_contract["value"]["valueAddedTaxIncluded"] = False
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, second_contract["id"], self.tender_token),
        {"data": {"status": "active", "value": second_contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # Check tender status
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def all_cancelled_lots(self):
    # Create 2 lots and update related items
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    first_lot = response.json["data"]
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    second_lot = response.json["data"]

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = first_lot["id"]

    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )

    items[0]["relatedLot"] = second_lot["id"]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )

    # Cancel lots
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": first_lot["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 > get_now():
        self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(
                self.tender_id, cancellation_id, self.tender_token
            ),
            {"data": {"status": "active"}},
        )
    else:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, first_lot["id"]))
    self.assertEqual(response.json["data"]["status"], "cancelled")
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": second_lot["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 > get_now():
        self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(
                self.tender_id, cancellation_id, self.tender_token
            ),
            {"data": {"status": "active"}},
        )

    else:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, second_lot["id"]))
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # Check tender status
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def cancel_lots_check_awards(self):
    # create first lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    first_lot = response.json["data"]

    # create second lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    second_lot = response.json["data"]

    # first award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"suppliers": [test_tender_below_organization], "status": "pending", "lotID": first_lot["id"], "qualified": True,
                  "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False}}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    first_award = response.json["data"]

    # second award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"suppliers": [test_tender_below_organization], "status": "pending", "lotID": second_lot["id"], "qualified": True,
                  "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    second_award = response.json["data"]

    # cancellation for first lot
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": first_lot["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]

    if RELEASE_2020_04_19 > get_now():
        self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(
                self.tender_id, cancellation_id, self.tender_token
            ),
            {"data": {"status": "active"}},
        )

    else:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    # check corresponding lot
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, first_lot["id"]))
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # check corresponding award
    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, first_award["id"]))
    self.assertEqual(response.json["data"]["status"], "pending")


def delete_lot_after_first_award(self):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"suppliers": [test_tender_below_organization], "status": "pending", "lotID": lot["id"], "qualified": True,
                  "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # try to delete lot
    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't delete lot when you have awards"}],
    )


def patch_lot_with_cancellation(self):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]

    # Create cancellation on lot
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": lot["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"suppliers": [test_tender_below_organization], "qualified": True, "lotID": lot["id"],
                      "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},}}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}}
        )
        self.set_all_awards_complaint_period_end()

        # Create cancellation
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))

        response = self.app.post_json(
            "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
                self.tender_id, cancellation_id, self.tender_token
            ),
            {"data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(
                self.tender_id, cancellation_id, self.tender_token
            ),
            {"data": {"status": "pending"}},
        )
        cancellation = response.json["data"]
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(cancellation["status"], "pending")

    # Try to patch lot with cancellation on it
    else:
        response = self.app.patch_json(
            "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
            {"data": {"title": "new title"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update lot that have active cancellation")
