# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta
from mock import patch

from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_with_complaints_after_2020_04_19,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_cancellation,
)
from openprocurement.tender.competitivedialogue.tests.base import test_tender_openeu_bids
from openprocurement.tender.core.tests.criteria_utils import generate_responses

# TenderStage2EU(UA)LotResourceTest


def create_tender_lot_invalid(self):
    """ Try create invalid lot """
    self.create_tender()
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

    response = self.app.post(request_path, "data", content_type="application/json", status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't create lot for tender stage2"}],
    )

    response = self.app.post_json(request_path, "data", status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't create lot for tender stage2"}],
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't create lot for tender stage2"}],
    )

    response = self.app.post_json(request_path, {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't create lot for tender stage2"}],
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't create lot for tender stage2"}],
    )

    response = self.app.post_json(request_path, {"data": {"value": "invalid_value"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't create lot for tender stage2"}],
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
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't create lot for tender stage2"}],
    )


@patch("openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
       get_now() + timedelta(days=1))
def create_tender_lot(self):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": self.test_lots_data[0]},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't create lot for tender stage2")

    lot2 = deepcopy(self.test_lots_data[0])
    lot2["guarantee"] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot2}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't create lot for tender stage2")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertNotIn("guarantee", response.json["data"])

    lot3 = deepcopy(self.test_lots_data[0])
    lot3["guarantee"] = {"amount": 500, "currency": "UAH"}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot3}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't create lot for tender stage2")

    lot3["guarantee"] = {"amount": 500}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot3}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't create lot for tender stage2")

    lot3["guarantee"] = {"amount": 20, "currency": "USD"}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot3}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't create lot for tender stage2")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertNotIn("guarantee", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"guarantee": {"currency": "EUR", "amount": 300}}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "guarantee",
            "description": "Field change's not allowed"
        }]
    )

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": self.test_lots_data[0]},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't create lot for tender stage2")

    self.set_enquiry_period_end()
    response = self.app.post_json(
        "/tenders/{}/lots".format(self.tender_id), {"data": self.test_lots_data[0]}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("active.auction")

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": self.test_lots_data[0]},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't create lot for tender stage2")


def patch_tender_lot(self):
    """ Patch tender lot which came from first stage """
    self.create_tender()
    lot_id = self.lots_id[0]

    # Add new title
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot_id, self.tender_token),
        {"data": {"title": "new title"}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't update lot for tender stage2"}],
    )

    # Change guarantee currency
    self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot_id, self.tender_token),
        {"data": {"guarantee": {"amount": 123, "currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't update lot for tender stage2"}],
    )

    # Try get lot with bad lot id
    response = self.app.patch_json(
        "/tenders/{}/lots/some_id".format(self.tender_id), {"data": {"title": "other title"}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "lot_id"}])

    # Try get lot with bad tender id and lot id
    response = self.app.patch_json("/tenders/some_id/lots/some_id", {"data": {"title": "other title"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    # Change title for lot when tender has status active.tendering
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["title"], "new title")

    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    # Try change title for lot when tender in status active.pre-quaifications
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot_id, self.tender_token),
        {"data": {"title": "other title"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't update lot for tender stage2"}],
    )


def patch_tender_currency(self):
    self.create_tender()
    lot = self.lots[0]
    self.assertEqual(lot["value"]["currency"], "UAH")

    # update tender currency without mimimalStep currency change
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"currency": "GBP", "amount": 500}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "value",
                "description": "Field change's not allowed"
            }
        ],
    )


def patch_tender_vat(self):
    # set tender VAT
    data = deepcopy(self.initial_data)
    data["value"]["valueAddedTaxIncluded"] = True
    self.create_tender(initial_data=data)

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    lot = tender["lots"][0]
    self.assertTrue(lot["value"]["valueAddedTaxIncluded"])

    # Try update tender VAT
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False, "amount": tender["value"]["amount"]},
                  "minimalStep": {"valueAddedTaxIncluded": False, "amount": tender["minimalStep"]["amount"]}}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "value",
                "description": "Field change's not allowed"
            }
        ],
    )


@patch("openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
       get_now() + timedelta(days=1))
def get_tender_lot(self):
    self.create_tender()
    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    lot = response.json["data"][0]
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    result = response.json["data"]
    result.pop("auctionPeriod", None)
    self.assertEqual(
        set(result),
        {"id", "title", "date", "description", "minimalStep", "value", "status"},
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot.pop("auctionPeriod", None)
    res = response.json["data"]
    res.pop("auctionPeriod", None)
    self.assertEqual(res, lot)

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


@patch("openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
       get_now() + timedelta(days=1))
def get_tender_lots(self):
    self.create_tender()
    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    lot = response.json["data"][0]

    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    result = response.json["data"][0]
    result.pop("auctionPeriod", None)
    self.assertEqual(
        set(result),
        {"id", "date", "title", "description", "minimalStep", "value", "status"},
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot.pop("auctionPeriod", None)
    res = response.json["data"][0]
    res.pop("auctionPeriod", None)
    self.assertEqual(res, lot)

    response = self.app.get("/tenders/some_id/lots", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def delete_tender_lot(self):
    self.create_tender()
    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    lot = response.json["data"][0]

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't delete lot for tender stage2"}],
    )

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

    response = self.app.get(f"/tenders/{self.tender_id}")
    items = deepcopy(response.json["data"]["items"])
    items[0]["relatedLot"] = lot["id"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't delete lot for tender stage2"}],
    )
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't delete lot for tender stage2")


def tender_lot_guarantee(self):
    lots = deepcopy(self.initial_lots)
    lots[0]["guarantee"] = {"amount": 20, "currency": "GBP"}
    self.create_tender(initial_lots=lots)
    lot = self.lots[0]
    lot_id = lot["id"]
    response = self.app.get("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot_id, self.tender_token))
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    lot = self.lots[1]
    lot_id = lot["id"]
    response = self.app.get("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot_id, self.tender_token))
    self.assertNotIn("guarantee", response.json["data"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")


def tender_lot_guarantee_v2(self):
    lots = deepcopy(self.initial_lots)
    lots[0]["guarantee"] = {"amount": 20, "currency": "GBP"}
    lots[1]["guarantee"] = {"amount": 40, "currency": "GBP"}
    self.create_tender(initial_lots=lots)
    lot = self.lots[0]
    lot_id = lot["id"]
    response = self.app.get("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot_id, self.tender_token))
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    lot = self.lots[1]
    lot_id = lot["id"]
    response = self.app.get("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot_id, self.tender_token))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 40)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 60)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    lot2 = self.lots[1]
    lot2_id = lot2["id"]
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot2["id"], self.tender_token),
        {"data": {"guarantee": {"amount": 50, "currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't update lot for tender stage2"}],
    )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 60)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"guarantee": {"amount": 35, "currency": "GBP"}}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "guarantee",
                "description": "Field change's not allowed"
            }
        ],
    )


# TenderStage2EU(UA)LotBidderResourceTest


def patch_tender_bidder(self):
    lot_id = self.lots[0]["id"]
    tenderers = deepcopy(self.test_bids_data[0]["tenderers"])
    tenderers[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][0]["identifier"]["id"]
    tenderers[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][0]["identifier"]["scheme"]

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers,
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}],
    })
    bidder, bid_token = self.create_bid(self.tender_id, bid_data)
    lot = bidder["lotValues"][0]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"tenderers": [{"name": "Державне управління управлінням справами"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {
            "data": {
                "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}],
                "tenderers": self.test_bids_data[0]["tenderers"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"lotValues": [{"value": {"amount": 400}, "relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])

    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("lotValues", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}], "status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update bid in current (unsuccessful) tender status"
    )


@patch("openprocurement.tender.core.models.TWO_PHASE_COMMIT_FROM", get_now() + timedelta(days=1))
def create_tender_bidder_invalid(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "lotValues"}],
    )

    bid_data["lotValues"] = [{"value": {"amount": 500}}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": "0" * 32}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["lotValues"] = [{"value": {"amount": 5000000}, "relatedLot": self.lots[0]["id"]}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["lotValues"] = [
        {"value": {"amount": 500, "valueAddedTaxIncluded": False}, "relatedLot": self.lots[0]["id"]}
    ]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["lotValues"] = [{"value": {"amount": 500, "currency": "USD"}, "relatedLot": self.lots[0]["id"]}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.lots[0]["id"]}]
    bid_data["value"] = {"amount": 500}
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["value should be posted for each lot of bid"], "location": "body", "name": "value"}],
    )


# TenderStage2EU(UA)LotFeatureBidderResourceTest


@patch("openprocurement.tender.core.models.TWO_PHASE_COMMIT_FROM", get_now() + timedelta(days=1))
def create_tender_with_features_bidder_invalid(self):
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    tenderers = bid_data["tenderers"]
    tenderers[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][0]["identifier"]["id"]
    tenderers[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][0]["identifier"]["scheme"]

    request_path = "/tenders/{}/bids".format(self.tender_id)
    response = self.app.post_json(
        request_path, {"data": bid_data}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    bid_data["lotValues"] = [{"value": {"amount": 500}}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": "0" * 32}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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
    bid_data["lotValues"] = [{"value": {"amount": 5000000}, "relatedLot": self.lot_id}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["lotValues"] = [{"value": {"amount": 500, "valueAddedTaxIncluded": False}, "relatedLot": self.lot_id}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["lotValues"] = [{"value": {"amount": 500, "currency": "USD"}, "relatedLot": self.lot_id}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.lot_id}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["All features parameters is required."], "location": "body", "name": "parameters"}],
    )

    bid_data["parameters"] = [{"code": "code_item", "value": 0.01}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["All features parameters is required."], "location": "body", "name": "parameters"}],
    )

    bid_data["parameters"] = [{"code": "code_invalid", "value": 0.01}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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

    bid_data["parameters"] = [
        {"code": "code_item", "value": 0.01},
        {"code": "code_tenderer", "value": 0},
        {"code": "code_lot", "value": 0.01},
    ]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
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


def create_tender_with_features_bidder(self):
    tenderers = deepcopy(self.test_bids_data[0]["tenderers"])
    tenderers[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][0]["identifier"]["id"]
    tenderers[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][0]["identifier"]["scheme"]

    request_path = "/tenders/{}/bids".format(self.tender_id)

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers,
        "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
        "parameters": [
            {"code": "code_item", "value": 0.01},
            {"code": "code_tenderer", "value": 0.01},
            {"code": "code_lot", "value": 0.01},
        ]
    })
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bidder = response.json["data"]
    self.assertEqual(bidder["tenderers"][0]["name"], self.test_tender_data["procuringEntity"]["name"])
    self.assertIn("id", bidder)
    self.assertIn(bidder["id"], response.headers["Location"])

    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (unsuccessful) tender status")


# TenderStage2EULotProcessTest


def one_lot_0bid(self):
    self.create_tender(self.test_lots_data)
    response = self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}}]}
    )
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # switch to unsuccessful
    self.set_status("active.pre-qualification", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["lots"][0]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": self.test_lots_data[0]},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't create lot for tender stage2"}],
    )


def one_lot_1bid(self):
    self.create_tender(self.test_lots_data)
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    tenderers = bid_data["tenderers"]
    tenderers[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][0]["identifier"]["id"]
    tenderers[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][0]["identifier"]["scheme"]
    # create bid
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}]
    bid_data["requirementResponses"] = generate_responses(self)
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    # switch to unsuccessful
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def one_lot_2bid_1un(self):
    self.create_tender(self.test_lots_data)
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]

    tenderers = bid_data["tenderers"]
    tenderers[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][0]["identifier"]["id"]
    tenderers[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][0]["identifier"]["scheme"]
    # create bid

    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}]
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(self.tender_id, bid_data)

    self.create_bid(self.tender_id, bid_data)
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[0]["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[1]["id"], self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def one_lot_2bid(self):
    # create tender with item and lot
    self.create_tender(initial_lots=self.test_lots_data)
    tenderers_1 = deepcopy(self.test_bids_data[0]["tenderers"])
    tenderers_1[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][0]["identifier"]["id"]
    tenderers_1[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][0]["identifier"]["scheme"]
    tenderers_2 = deepcopy(self.test_bids_data[1]["tenderers"])
    tenderers_2[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][1]["identifier"]["id"]
    tenderers_2[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][1]["identifier"]["scheme"]
    # create bid
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["tenderers"] = tenderers_1
    bid_data["lotValues"] = [{"value": {"amount": 450}, "relatedLot": self.lots_id[0]}]
    del bid_data["value"]
    bid_data["requirementResponses"] = generate_responses(self)

    self.app.authorization = ("Basic", ("broker", ""))
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    bid_id = bid["id"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data.update({
        "tenderers": tenderers_2,
        "lotValues": [{"value": {"amount": 475}, "relatedLot": self.lots_id[0]}],
    })
    self.create_bid(self.tender_id, bid_data)
    # switch to active.auction
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")

    for bid in response.json["data"]["bids"]:
        self.assertEqual(bid["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")

    self.time_shift("active.auction")

    self.check_chronograph()

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = [
        {"id": b["id"], "lotValues": [
            {"relatedLot": l["relatedLot"], "value": l["value"]} for l in b["lotValues"]
        ]}
        for b in response.json["data"]["bids"]
    ]
    # posting auction urls
    response = self.app.patch_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.lots_id[0]),
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
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.lots_id[0]), {"data": {"bids": auction_bids_data}}
    )
    # # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand still period

    self.time_shift("complete")
    self.check_chronograph()

    # # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_2bid_1lot_del(self):
    # create tender 2 lot
    self.create_tender(initial_lots=self.test_lots_data * 2)
    self.app.authorization = ("Basic", ("broker", ""))

    self.set_status(
        "active.tendering",
        {
            "lots": [
                {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
                for i in self.initial_lots
            ]
        },
    )
    # create bid
    tenderers_1 = deepcopy(self.test_bids_data[0]["tenderers"])
    tenderers_1[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][0]["identifier"]["id"]
    tenderers_1[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][0]["identifier"]["scheme"]
    tenderers_2 = deepcopy(self.test_bids_data[1]["tenderers"])
    tenderers_2[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][1]["identifier"]["id"]
    tenderers_2[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][1]["identifier"]["scheme"]

    bids = []
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers_1,
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot["id"]} for lot in self.initial_lots],
    })
    bid_data["requirementResponses"] = generate_responses(self)
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    bids.append(response.json)
    # create second bid
    bid_data["tenderers"] = tenderers_2
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    bids.append(response.json)
    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, self.initial_lots[0]["id"], self.tender_token),
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't delete lot for tender stage2")


def one_lot_3bid_1del(self):
    """ Create tender with 1 lot and 3 bids, later delete 1 bid """
    self.create_tender(initial_lots=self.test_lots_data)
    tenderers = []
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 450}, "relatedLot": self.initial_lots[0]["id"]}]
    for i in range(3):
        tenderer = deepcopy(bid_data["tenderers"])
        tenderer[0]["identifier"]["id"] = self.initial_data["shortlistedFirms"][i]["identifier"]["id"]
        tenderer[0]["identifier"]["scheme"] = self.initial_data["shortlistedFirms"][i]["identifier"]["scheme"]
        tenderers.append(tenderer)
    bid_data["requirementResponses"] = generate_responses(self)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bids = []
    for i in range(3):
        bid_data["tenderers"] = tenderers[i]
        bid, bid_token = self.create_bid(self.tender_id, bid_data)
        bids.append({bid["id"]: bid_token})

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, list(bids[2].keys())[0], list(bids[2].values())[0]), status=200
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    self.time_shift("active.auction")

    self.check_chronograph()
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = [
        {"id": b["id"], "lotValues": [
            {"relatedLot": l["relatedLot"], "value": l["value"]}
            for l in b.get("lotValues", "")
        ]}
        for b in response.json["data"]["bids"]
    ]
    # posting auction urls
    data = {
        "data": {
            "lots": [
                {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
            ],
            "bids": [{"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                     for b in auction_bids_data],
        }
    }

    for bid_index, bid in enumerate(auction_bids_data):
        if bid.get("status", "active") == "active":
            for lot_index, lot_bid in enumerate(bid["lotValues"]):
                if lot_bid["relatedLot"] == self.initial_lots[0]["id"] and lot_bid.get("status", "active") == "active":
                    data["data"]["bids"][bid_index]["lotValues"][lot_index][
                        "participationUrl"
                    ] = "https://tender.auction.url/for_bid/{}".format(bid["id"])
                    break

    response = self.app.patch_json("/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]), data)
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    bid_id = list(bids[0].keys())[0]
    bid_token = list(bids[0].values())[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    bid_id = list(bids[2].keys())[0]
    bid_token = list(bids[2].values())[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token))
    self.assertEqual(response.json["data"]["status"], "deleted")

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    # # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand still period

    self.time_shift("complete")
    self.check_chronograph()

    # # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def one_lot_3bid_1un(self):
    """ Create tender with 1 lot and 3 bids, later 1 bid unsuccessful"""
    self.create_tender(initial_lots=self.test_lots_data)
    bid_count = 3
    tenderers = self.create_tenderers(bid_count)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bids = []
    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 450}, "relatedLot": self.initial_lots[0]["id"]}]
    bid_data["requirementResponses"] = generate_responses(self)
    for i in range(bid_count):
        bid_data["tenderers"] = tenderers[i]
        bid, bid_token = self.create_bid(self.tender_id, bid_data)
        bids.append({bid["id"]: bid_token})

    # switch to active.auction
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    for qualification in qualifications:
        if qualification["bidID"] == list(bids[2].keys())[0]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "unsuccessful"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "unsuccessful")
        else:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")

    self.time_shift("active.auction")

    self.check_chronograph()
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = [
        {"id": b["id"], "lotValues": [
            {"relatedLot": l["relatedLot"], "value": l["value"]} for l in b["lotValues"]
        ]}
        for b in response.json["data"]["bids"]
    ]
    # posting auction urls
    data = {
        "data": {
            "lots": [
                {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
            ],
            "bids": [{"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                     for b in auction_bids_data],
        }
    }

    for bid_index, bid in enumerate(auction_bids_data):
        if bid.get("status", "active") == "active":
            for lot_index, lot_bid in enumerate(bid["lotValues"]):
                if lot_bid["relatedLot"] == self.initial_lots[0]["id"] and lot_bid.get("status", "active") == "active":
                    data["data"]["bids"][bid_index]["lotValues"][lot_index][
                        "participationUrl"
                    ] = "https://tender.auction.url/for_bid/{}".format(bid["id"])
                    break

    response = self.app.patch_json("/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]), data)
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    bid_id = list(bids[0].keys())[0]
    bid_token = list(bids[0].values())[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    bid_id = list(bids[2].keys())[0]
    bid_token = list(bids[2].values())[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token))
    self.assertNotIn("lotValues", response.json["data"])

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    # # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand still period

    self.time_shift("complete")
    self.check_chronograph()

    # # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_0bid(self):
    """ Create tender with 2 lots and 0 bids """
    self.create_tender(initial_lots=self.test_lots_data * 2)

    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    # switch to unsuccessful
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertTrue(all([i["status"] == "unsuccessful" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def two_lot_2can(self):
    """ Create tender with 2 lots, later cancel both """
    self.create_tender(self.test_lots_data * 2)

    # cancel every lot
    for lot in self.initial_lots:
        cancellation = dict(**test_tender_below_cancellation)
        cancellation.update({
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": lot["id"],
        })
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        )
        cancellation_id = response.json["data"]["id"]
        if RELEASE_2020_04_19 < get_now():
            activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertTrue(all([i["status"] == "cancelled" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def two_lot_1can(self):
    """ Create tender with 2 lots, later 1 cancel """
    self.create_tender(initial_lots=self.test_lots_data * 2)

    # cancel first lot
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )

    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertFalse(all([i["status"] == "cancelled" for i in response.json["data"]["lots"]]))
    self.assertTrue(any([i["status"] == "cancelled" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # try to restore lot back by old cancellation
    response = self.app.get("/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(len(response.json["data"]), 1)
    cancellation = response.json["data"][0]
    self.assertEqual(cancellation["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can perform cancellation only in active lot status")

    # try to restore lot back by new pending cancellation
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can perform cancellation only in active lot status")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertFalse(all([i["status"] == "cancelled" for i in response.json["data"]["lots"]]))
    self.assertTrue(any([i["status"] == "cancelled" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "active.tendering")


def two_lot_2bid_0com_1can(self):
    """ Create tender with 2 lots and 2 bids """
    self.create_tender(self.test_lots_data * 2)

    tenderers = self.create_tenderers(2)
    # create bid
    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data["tenderers"] = tenderers[0]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot["id"]} for lot in self.initial_lots]
    bid_data["requirementResponses"] = generate_responses(self)
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(self.tender_id, bid_data)

    bid_data.update({
        "tenderers": tenderers[1],
        "lotValues": [{"value": {"amount": 499}, "relatedLot": lot["id"]} for lot in self.initial_lots],
    })
    self.create_bid(self.tender_id, bid_data)

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    # active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 2)

    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")


def two_lot_2bid_2com_2win(self):
    """ Create tender with 2 lots and 2 bids """
    self.create_tender(initial_lots=self.test_lots_data * 2)
    tenderers = self.create_tenderers(2)
    # create bid
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["requirementResponses"] = generate_responses(self)
    bid_data.update({
        "tenderers": tenderers[0],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot["id"]} for lot in self.initial_lots],
    })

    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(self.tender_id, bid_data)
    # create second bid
    bid_data["tenderers"] = tenderers[1]
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(self.tender_id, bid_data)
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 4)

    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.time_shift("active.auction")
    self.check_chronograph()
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = [
        {"id": b["id"], "lotValues": [
            {"relatedLot": l["relatedLot"], "value": l["value"]} for l in b["lotValues"]
        ]}
        for b in response.json["data"]["bids"]
    ]
    for lot in self.initial_lots:
        # posting auction urls
        self.app.patch_json(
            "/tenders/{}/auction/{}".format(self.tender_id, lot["id"]),
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
            "/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": {"bids": auction_bids_data}}
        )
    # for first lot
    lot_id = self.initial_lots[0]["id"]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # for second lot
    lot_id = self.initial_lots[1]["id"]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand still period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertTrue(all([i["status"] == "complete" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "complete")


# TenderStage2UALotBidderResourceTest


def patch_tender_bidder_ua(self):
    lot_id = self.lots[0]["id"]
    tenderers = self.create_tenderers()

    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers[0],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}],
    })
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bidder = response.json["data"]
    lot = bidder["lotValues"][0]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], owner_token),
        {"data": {"tenderers": [{"name": "Державне управління управлінням справами"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], owner_token),
        {"data": {"lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}], "tenderers": [test_tender_below_organization]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], owner_token),
        {"data": {"lotValues": [{"value": {"amount": 400}, "relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])

    self.set_status("complete")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bidder["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], owner_token),
        {"data": {"lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid in current (complete) tender status")


# TenderStage2UALotProcessTest


def one_lot_0bid_ua(self):
    self.create_tender(initial_lots=self.test_lots_data)
    # switch to active.tendering
    response = self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]}
    )
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # switch to unsuccessful
    response = self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}}], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["lots"][0]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def one_lot_2bid_ua(self):
    self.create_tender(initial_lots=self.test_lots_data)
    tenderers = self.create_tenderers(2)
    # switch to active.tendering
    response = self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]}
    )
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # create bid
    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data["tenderers"] = tenderers[0]
    bid_data["lotValues"] = [
        {"subcontractingDetails": "test", "value": {"amount": 450}, "relatedLot": self.lots_id[0]}
    ]
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    bid_id = bid["id"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data.update({
        "tenderers": tenderers[1],
        "lotValues": [{"value": {"amount": 475}, "relatedLot": self.lots_id[0]}],
    })
    self.create_bid(self.tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction")
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = [
        {"id": b["id"], "lotValues": [
            {"relatedLot": l["relatedLot"], "value": l["value"]} for l in b["lotValues"]
        ]}
        for b in response.json["data"]["bids"]
    ]
    # posting auction urls
    response = self.app.patch_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.lots_id[0]),
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
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.lots_id[0]), {"data": {"bids": auction_bids_data}}
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand still period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def one_lot_3bid_1un_ua(self):
    self.create_tender(initial_lots=self.test_lots_data)
    tenderers = self.create_tenderers(3)
    response = self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]}
    )
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # create bids
    bids_data = {}
    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 450}, "relatedLot": self.lots_id[0]}]
    for i in range(3):
        bid_data["tenderers"] = tenderers[i]
        bid_data["requirementResponses"] = generate_responses(self)
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        bids_data[response.json["data"]["id"]] = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, self.lots_id[0], self.tender_token),
        {"data": {"value": {"amount": 1000}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update lot for tender stage2")
    # create second bid
    for bid_id, bid_token in list(bids_data.items())[:-1]:

        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token), {"data": {"status": "active"}}
        )
        # bids_data[response.json['data']['id']] = response.json['access']['token']
    # switch to active.auction
    self.set_status("active.auction")
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = [
        {"id": b["id"], "lotValues": [
            {"relatedLot": l["relatedLot"], "value": l["value"]} for l in b["lotValues"]
        ]}
        for b in response.json["data"]["bids"]
    ]
    # posting auction urls

    auction_data = {
        "data": {
            "lots": [
                {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
            ],
            "bids": [],
        }
    }
    for i in auction_bids_data:
        if i.get("status", "active") == "active":
            auction_data["data"]["bids"].append(
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
            )
        else:
            auction_data["data"]["bids"].append({"id": i["id"]})

    response = self.app.patch_json("/tenders/{}/auction/{}".format(self.tender_id, self.lots_id[0]), auction_data)
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.lots_id[0]), {"data": {"bids": auction_bids_data}}
    )
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand still period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def one_lot_1bid_patch_ua(self):
    self.create_tender(initial_lots=self.test_lots_data)
    tenderers = self.create_tenderers()
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers[0],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lots_id[0]}],
    })
    bid_data["requirementResponses"] = generate_responses(self)
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    bid_id = bid["id"]

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, self.lots_id[0], self.tender_token),
        {"data": {"value": {"amount": 499}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update lot for tender stage2")

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def two_lot_0bid_ua(self):
    self.create_tender(initial_lots=self.test_lots_data * 2)
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}} for i in self.lots_id
            ]
        },
    )
    self.assertTrue(all(["auctionPeriod" in i for i in response.json["data"]["lots"]]))
    # switch to unsuccessful
    response = self.set_status(
        "active.auction",
        {"lots": [{"auctionPeriod": {"startDate": None}} for i in self.lots_id], "status": "active.tendering"},
    )
    response = self.check_chronograph()
    self.assertTrue(all([i["status"] == "unsuccessful" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def two_lot_1bid_0com_1can_ua(self):
    self.create_tender(initial_lots=self.test_lots_data * 2)
    tenderers = self.create_tenderers()
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}} for i in self.lots_id
            ]
        },
    )
    # create bid
    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers[0],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in self.lots_id],
    })
    bid_data["requirementResponses"] = generate_responses(self)

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    response = self.set_status(
        "active.auction",
        {"lots": [{"auctionPeriod": {"startDate": None}} for i in self.lots_id], "status": "active.tendering"},
    )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def two_lot_1bid_2com_1win_ua(self):
    self.create_tender(initial_lots=self.test_lots_data)
    tenderers = self.create_tenderers()
    # switch to active.tendering
    self.set_status(
        "active.tendering",
        {
            "lots": [
                {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}} for i in self.lots_id
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers[0],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in self.lots_id],
    })
    bid_data["requirementResponses"] = generate_responses(self)
    self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status(
        "active.auction",
        {"lots": [{"auctionPeriod": {"startDate": None}} for i in self.lots_id], "status": "active.tendering"},
    )
    response = self.check_chronograph()
    for lot_id in self.lots_id:
        # get awards
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
        # get pending award
        if len([i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id]) == 0:
            return
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]

        # set award as active
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
            {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
        )
        # get contract id
        response = self.app.get("/tenders/{}".format(self.tender_id))
        contract = response.json["data"]["contracts"][-1]
        contract_id = contract["id"]
        contract_value = deepcopy(contract["value"])
        # after stand still period
        self.set_status("complete", {"status": "active.awarded"})
        # time travel
        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get("awards", []):
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
        self.mongodb.tenders.save(tender)
        # sign contract
        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
            {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
        )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertTrue(all([i["status"] == "complete" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_1bid_0com_0win_ua(self):
    self.create_tender(initial_lots=self.test_lots_data * 2)
    tenderers = self.create_tenderers()
    # switch to active.tendering
    response = self.set_status(
        "active.tendering",
        {
            "lots": [
                {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}} for i in self.lots_id
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers[0],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in self.lots_id],
    })
    bid_data["requirementResponses"] = generate_responses(self)
    self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status(
        "active.auction",
        {"lots": [{"auctionPeriod": {"startDate": None}} for i in self.lots_id], "status": "active.tendering"},
    )
    response = self.check_chronograph()
    self.assertTrue(all([i["status"] == "unsuccessful" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def two_lot_1bid_1com_1win_ua(self):
    self.create_tender(initial_lots=self.test_lots_data * 2)
    tenderers = self.create_tenderers()
    # switch to active.tendering
    self.set_status(
        "active.tendering",
        {
            "lots": [
                {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}} for i in self.lots_id
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(test_tender_openeu_bids[0])
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers[0],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in self.lots_id],
    })
    bid_data["requirementResponses"] = generate_responses(self)
    self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status(
        "active.auction",
        {"lots": [{"auctionPeriod": {"startDate": None}} for i in self.lots_id], "status": "active.tendering"},
    )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def two_lot_2bid_2com_2win_ua(self):
    self.create_tender(initial_lots=self.test_lots_data * 2)
    tenderers = self.create_tenderers(2)
    # switch to active.tendering
    self.set_status(
        "active.tendering",
        {
            "lots": [
                {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}} for i in self.lots_id
            ]
        },
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(test_tender_openeu_bids[0])
    bid_data["requirementResponses"] = generate_responses(self)
    del bid_data["value"]
    bid_data.update({
        "tenderers": tenderers[0],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in self.lots_id],
    })
    self.create_bid(self.tender_id, bid_data)
    # create second bid

    bid_data["tenderers"] = tenderers[1]
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(self.tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction")
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = [
        {"id": b["id"], "lotValues": [
            {"relatedLot": l["relatedLot"], "value": l["value"]} for l in b["lotValues"]
        ]}
        for b in response.json["data"]["bids"]
    ]
    for lot_id in self.lots_id:
        # posting auction urls
        response = self.app.patch_json(
            "/tenders/{}/auction/{}".format(self.tender_id, lot_id),
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
            "/tenders/{}/auction/{}".format(self.tender_id, lot_id), {"data": {"bids": auction_bids_data}}
        )
    # for first lot
    lot_id = self.lots_id[0]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand still period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # for second lot
    lot_id = self.lots_id[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand still period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertTrue(all([i["status"] == "complete" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "complete")
