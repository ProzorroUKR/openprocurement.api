# -*- coding: utf-8 -*-
from datetime import timedelta
from copy import deepcopy

from openprocurement.api.models import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import parse_date
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_author,
    test_tender_below_cancellation,
    test_tender_below_claim,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_lots
from openprocurement.tender.open.tests.base import test_tender_open_bids


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
    items = deepcopy(self.initial_data["items"])
    for i in items:
        i["unit"]["value"]["currency"] = "GBP"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"currency": "GBP", "amount": self.initial_data["value"]["amount"]},
                  "items": items}},
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
        ],
    )

    # update tender currency
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"currency": "GBP", "amount": self.initial_data["value"]["amount"]},
                  "minimalStep": {"currency": "GBP", "amount": self.initial_data["minimalStep"]["amount"]},
                  "items": items}},
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
        {"data": {"value": {**lot["value"], "currency": "USD", "amount": lot["value"]["amount"]}}},
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
        {"data": {"minimalStep": {**lot["minimalStep"], "currency": "USD", "amount": lot["minimalStep"]["amount"]}}},
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
        {"data": {"value": {**lot["value"], "currency": "USD", "amount": lot["value"]["amount"]},
                  "minimalStep": {**lot["minimalStep"], "currency": "USD", "amount": lot["minimalStep"]["amount"]}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["value"]["currency"], "GBP")
    self.assertEqual(lot["minimalStep"]["currency"], "GBP")

    self.set_enquiry_period_end()
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"value": {**lot["value"], "currency": "USD", "amount": lot["value"]["amount"]},
                  "minimalStep": {**lot["minimalStep"], "currency": "USD", "amount": lot["minimalStep"]["amount"]}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")


def patch_tender_vat(self):
    # set tender VAT
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": True, "amount": self.initial_data["value"]["amount"]}}},
    )
    self.assertEqual(response.status, "200 OK")
    items = response.json["data"]["items"]

    # create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertTrue(lot["value"]["valueAddedTaxIncluded"])

    # update tender VAT
    for i in items:
        i["unit"]["value"]["valueAddedTaxIncluded"] = False
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False, "amount": lot["value"]["amount"]},
                  "minimalStep": {"valueAddedTaxIncluded": False, "amount": lot["minimalStep"]["amount"]},
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
        {"data": {"value": {"valueAddedTaxIncluded": True, "amount": lot["value"]["amount"], "currency": "UAH"}}},
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
        {"data": {
            "minimalStep": {
                "valueAddedTaxIncluded": True,
                "amount": lot["minimalStep"]["amount"],
                "currency": "UAH",
            }
        }},
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
            "minimalStep": {**lot["minimalStep"], "valueAddedTaxIncluded": True}
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

    self.set_enquiry_period_end()
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"value": {**lot["value"], "currency": "USD", "amount": lot["value"]["amount"]},
                  "minimalStep": {**lot["minimalStep"], "currency": "USD", "amount": lot["minimalStep"]["amount"]}}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")


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
    result = response.json["data"]
    result.pop("auctionPeriod", None)
    self.assertEqual(
        set(result),
        {"status", "date", "description", "title", "minimalStep", "value", "id"},
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    api_lot = response.json["data"]
    lot.pop("auctionPeriod", None)
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
    result = response.json["data"][-1]
    result.pop("auctionPeriod", None)
    self.assertEqual(
        set(result),
        {"status", "description", "date", "title", "minimalStep", "value", "id"},
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    api_lot = response.json["data"][-1]
    lot.pop("auctionPeriod", None)
    api_lot.pop("auctionPeriod")
    self.assertEqual(api_lot, lot)

    response = self.app.get("/tenders/some_id/lots", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def question_blocking(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": test_tender_below_author,
            }
        },
    )
    question = response.json["data"]
    self.assertEqual(question["questionOf"], "lot")
    self.assertEqual(question["relatedItem"], self.initial_lots[0]["id"])

    self.set_status(self.question_claim_block_status, extra={"status": "active.tendering"})
    self.check_chronograph()
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # cancel lot
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

    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    self.check_chronograph()

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], self.question_claim_block_status)


def claim_blocking(self):
    self.app.authorization = ("Basic", ("broker", ""))
    claim_data = deepcopy(test_tender_below_claim)
    claim_data["relatedLot"] = self.initial_lots[0]["id"]
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": claim_data
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    self.assertEqual(complaint["relatedLot"], self.initial_lots[0]["id"])

    self.set_status(self.question_claim_block_status, extra={"status": "active.tendering"})
    self.check_chronograph()

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # cancel lot
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
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    self.check_chronograph()

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], self.question_claim_block_status)


def next_check_value_with_unanswered_question(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": test_tender_below_author,
            }
        },
    )
    question = response.json["data"]
    self.assertEqual(question["questionOf"], "lot")
    self.assertEqual(question["relatedItem"], self.initial_lots[0]["id"])

    self.set_status(self.question_claim_block_status, extra={"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertNotIn("next_check", response.json["data"])

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
        activate_cancellation_after_2020_04_19(self, cancellation_id)
    else:
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertIn("next_check", response.json["data"])
        self.assertEqual(
            parse_date(response.json["data"]["next_check"]),
            parse_date(response.json["data"]["tenderPeriod"]["endDate"])
        )

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], self.question_claim_block_status)
    self.assertIn("next_check", response.json["data"])
    self.assertGreater(
        parse_date(response.json["data"]["next_check"]),
        parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )


def next_check_value_with_unanswered_claim(self):
    self.app.authorization = ("Basic", ("broker", ""))
    claim = deepcopy(test_tender_below_claim)
    claim["relatedLot"] = self.initial_lots[0]["id"]
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    self.assertEqual(complaint["relatedLot"], self.initial_lots[0]["id"])

    self.set_status(self.question_claim_block_status, extra={"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertNotIn("next_check", response.json["data"])

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
        activate_cancellation_after_2020_04_19(self, cancellation_id)
    else:
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertIn("next_check", response.json["data"])
        self.assertEqual(
            parse_date(response.json["data"]["next_check"]),
            parse_date(response.json["data"]["tenderPeriod"]["endDate"])
        )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], self.question_claim_block_status)
    self.assertIn("next_check", response.json["data"])
    self.assertGreater(
        parse_date(response.json["data"]["next_check"]),
        parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )


def create_tender_bidder_invalid(self):
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    request_path = f"/tenders/{self.tender_id}/bids"
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

    bid_data["lotValues"] = [{"value": {"amount": 500, "valueAddedTaxIncluded": False}, "relatedLot": self.initial_lots[0]["id"]}]
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

    bid_data["lotValues"] = [{"value": {"amount": 500, "currency": "USD"}, "relatedLot": self.initial_lots[0]["id"]}]
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

    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}]
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

    bid_data["tenderers"] = test_tender_below_organization
    bid_data["tenderers"] = test_tender_below_organization
    del bid_data["value"]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("invalid literal for int() with base 10", response.json["errors"][0]["description"])


def patch_tender_bidder(self):
    lot_id = self.initial_lots[0]["id"]
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id}]
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


def create_tender_bidder_feature_invalid(self):
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]

    request_path = "/tenders/{}/bids".format(self.tender_id)
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
            {"description": ["This field is required."], "location": "body", "name": "lotValues"},
            {"description": ["All features parameters is required."], "location": "body", "name": "parameters"},
        ],
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
    bid_data["tenderers"] = test_tender_below_organization
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("invalid literal for int() with base 10", response.json["errors"][0]["description"])

    bid_data["tenderers"] = [test_tender_below_organization]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.lot_id}]
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

    bid_data.update({
        "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
        "parameters": [{"code": "code_item", "value": 0.01}],
    })
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


def create_tender_bidder_feature(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.pop("value", None)

    bid_data.update({
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
    self.assertEqual(bidder["tenderers"][0]["name"], test_tender_below_organization["name"])
    self.assertIn("id", bidder)
    self.assertIn(bidder["id"], response.headers["Location"])

    self.set_status("complete")

    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


def proc_1lot_1bid(self):
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
    items = [deepcopy(self.initial_data["items"][0])]
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(days=self.days_till_auction_starts)
    response = self.set_status("active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}}]})
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(test_tender_open_bids[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"subcontractingDetails": "test", "value": {"amount": 500}, "relatedLot": lot_id}]
    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status("active.auction", {"lots": [{"auctionPeriod": {"startDate": None}}], "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["lots"][0]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def proc_1lot_1bid_patch(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    tender_data = deepcopy(self.initial_data)
    set_tender_lots(tender_data, self.test_lots_data)
    self.test_lots_data = tender_data["lots"]

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # add lot
    lot_data = self.test_lots_data[0].copy()
    lot_data.pop("id")
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": lot_data}
    )
    self.assertEqual(response.status, "201 Created")
    lot = response.json["data"]
    lot_id = lot["id"]
    # add relatedLot for item
    items = [deepcopy(self.initial_data["items"][0])]
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id}]
    bid, bid_token = self.create_bid(tender_id, bid_data)
    bid_id = bid["id"]

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(tender_id, lot_id, owner_token),
        {"data": {"value": {**lot["value"], "amount": 499}, "minimalStep": {**lot["minimalStep"], "amount": 14.0}}}
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "invalid")


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
    items = [deepcopy(self.initial_data["items"][0])]
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(days=self.days_till_auction_starts)
    response = self.set_status("active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}}]})
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"subcontractingDetails": "test", "value": {"amount": 450}, "relatedLot": lot_id}]

    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    bid_id = bid["id"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data["lotValues"] = [{"value": {"amount": 475}, "relatedLot": lot_id}]

    self.create_bid(self.tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction")
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    self.app.patch_json(
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
    self.app.post_json("/tenders/{}/auction/{}".format(tender_id, lot_id),
                       {"data": {"bids": [
                            {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                            for b in auction_bids_data]}})
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
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
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
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


def proc_1lot_3bid_1un(self):
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
    lot = response.json["data"]
    lot_id = lot["id"]
    self.initial_lots = [response.json["data"]]
    items = [deepcopy(self.initial_data["items"][0])]
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(days=self.days_till_auction_starts)
    response = self.set_status("active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}}]})
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # create bids
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 450}, "relatedLot": lot_id}]
    bids_data = {}
    for i in range(3):
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/bids".format(tender_id),
            {"data": bid_data},
        )
        bids_data[response.json["data"]["id"]] = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(tender_id, lot_id, owner_token),
        {"data": {"value": {**lot["value"], "amount": 1000}}}
    )
    self.assertEqual(response.status, "200 OK")
    # create second bid
    for bid_id, bid_token in list(bids_data.items())[:-1]:
        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token), {"data": {"status": "active"}}
        )
        # bids_data[response.json['data']['id']] = response.json['access']['token']
    # switch to active.auction
    self.set_status("active.auction")
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
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

    self.app.patch_json("/tenders/{}/auction/{}".format(tender_id, lot_id), auction_data)
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    self.app.post_json("/tenders/{}/auction/{}".format(tender_id, lot_id),
                       {"data": {"bids": [
                            {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                            for b in auction_bids_data]}})
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
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
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
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


def proc_2lot_1bid_0com_1can(self):
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
    items = [deepcopy(self.initial_data["items"][0]) for _ in lots]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    # add relatedLot for item
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    self.set_status(
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

    bid_data = deepcopy(test_tender_open_bids[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots]

    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def proc_2lot_2bid_1lot_del(self):
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
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )

    # switch to active.tendering
    start_date = get_now() + timedelta(days=self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )
    # create bid

    bids = []
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(test_tender_open_bids[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots]

    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bids.append(response.json)
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bids.append(response.json)
    response = self.app.delete("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lots[0], owner_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


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
    items = [deepcopy(self.initial_data["items"][0]) for i in lots]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    # add relatedLot for item
    for n, i in enumerate(lots):
        items[n]["relatedLot"] = i
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(days=self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(test_tender_open_bids[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots]

    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    self.check_chronograph()

    for lot_id in lots:
        # get awards
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
        # get pending award
        if len([i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id]) == 0:
            return
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]

        # set award as active
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
            {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
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
        for i in tender.get("awards", []):
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
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
    items = [deepcopy(self.initial_data["items"][0]) for i in lots]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    # add relatedLot for item
    for n, i in enumerate(lots):
        items[n]["relatedLot"] = i
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(days=self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(test_tender_open_bids[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots]

    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    self.assertTrue(all([i["status"] == "unsuccessful" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def proc_2lot_1bid_1com_1win(self):
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
    items = [deepcopy(self.initial_data["items"][0]) for i in lots]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    # add relatedLot for item
    for n, i in enumerate(lots):
        items[n]["relatedLot"] = i
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(days=self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(test_tender_open_bids[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots]
    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


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
    items = [deepcopy(self.initial_data["items"][0]) for i in lots]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    # add relatedLot for item
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(days=self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots]

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
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
        self.app.patch_json(
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
            {"data": {"bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                    for b in auction_bids_data]}}
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
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
    for i in tender.get("awards", []):
        now = get_now().isoformat()
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
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
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
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


def lots_features_delete(self):
    # create tender
    tender_data = deepcopy(self.test_features_tender_data)
    set_tender_lots(tender_data, self.test_lots_data)
    self.test_lots_data = tender_data["lots"]

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    self.assertEqual(tender["features"], tender_data["features"])
    # add lot
    lots = []
    for lot in self.test_lots_data * 2:
        lot = lot.copy()
        lot.pop("id")
        response = self.app.post_json("/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": lot})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        lots.append(response.json["data"]["id"])

    # add features
    self.app.patch_json(
        "/tenders/{}?acc_token={}&opt_pretty=1".format(tender["id"], owner_token),
        {
            "data": {
                "features": [
                    {
                        "code": "code_item",
                        "featureOf": "item",
                        "relatedItem": "1",
                        "title": "item feature",
                        "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
                    },
                    {
                        "code": "code_lot",
                        "featureOf": "lot",
                        "relatedItem": lots[1],
                        "title": "lot feature",
                        "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
                    },
                    {
                        "code": "code_tenderer",
                        "featureOf": "tenderer",
                        "title": "tenderer feature",
                        "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
                    },
                ]
            }
        },
    )
    # create bid
    bid_data = deepcopy(test_tender_open_bids[0])
    del bid_data["value"]
    bid_data.update({
        "lotValues": [{"value": {"amount": 500}, "relatedLot": lots[1]}],
        "parameters": [{"code": "code_lot", "value": 0.01}, {"code": "code_tenderer", "value": 0.01}]
    })

    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]
    self.set_responses(self.tender_id, response.json)

    # delete features
    self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"features": []}})
    response = self.app.get("/tenders/{}?opt_pretty=1".format(tender_id))
    self.assertNotIn("features", response.json["data"])
    # patch bid without parameters
    bid_data["parameters"] = []

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("parameters", response.json["data"])


def proc_2lot_2bid_1claim_1com_1win(self):
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
    items = [deepcopy(self.initial_data["items"][0]) for i in lots]
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    # add relatedLot for item
    for n, i in enumerate(lots):
        items[n]["relatedLot"] = i
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    self.set_status(
        "active.tendering",
        {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}} for i in lots]},
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(test_tender_open_bids[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id} for lot_id in lots]

    bid, bid_token = self.create_bid(self.tender_id, bid_data)
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
        self.app.patch_json(
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
            {"data": {"bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                    for b in auction_bids_data]}}
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # add complaint
    claim = deepcopy(test_tender_below_claim)
    claim["relatedLot"] = lot_id
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(tender_id, award_id, bid_token),
        {
            "data": claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    # cancel lot

    if RELEASE_2020_04_19 < get_now():
        self.set_all_awards_complaint_period_end()

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
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]

    if get_now() > RELEASE_2020_04_19:
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
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
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
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
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
    self.assertTrue([i["status"] for i in response.json["data"]["lots"]], ["cancelled", "complete"])
    self.assertEqual(response.json["data"]["status"], "complete")
