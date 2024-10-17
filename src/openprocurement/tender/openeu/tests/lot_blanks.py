from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_cancellation,
    test_tender_below_claim,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import activate_contract
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
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
                "author": self.test_author,
            }
        },
    )
    question = response.json["data"]
    self.assertEqual(question["questionOf"], "lot")
    self.assertEqual(question["relatedItem"], self.initial_lots[0]["id"])

    self.set_status(self.question_claim_block_status, extra={"status": "active.tendering"})
    response = self.check_chronograph()

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # cancel lot
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(self, cancellation_id)
        response = self.app.get("/tenders/{}".format(self.tender_id))

    response = self.check_chronograph()

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], self.question_claim_block_status)


def claim_blocking(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # as POST claim already doesn't work, create claim via database just to test old tenders
    tender = self.mongodb.tenders.get(self.tender_id)
    claim_data = deepcopy(test_tender_below_claim)
    claim_data["relatedLot"] = self.initial_lots[0]["id"]
    tender["complaints"] = [claim_data]
    self.mongodb.tenders.save(tender)

    self.set_status(self.question_claim_block_status, extra={"status": "active.tendering"})
    response = self.check_chronograph()
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # cancel lot
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.check_chronograph()

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
                "author": self.test_author,
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
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
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
            parse_date(response.json["data"]["tenderPeriod"]["endDate"]),
        )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], self.question_claim_block_status)


def next_check_value_with_unanswered_claim(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # as POST claim already doesn't work, create claim via database just to test old tenders
    tender = self.mongodb.tenders.get(self.tender_id)
    claim_data = deepcopy(test_tender_below_claim)
    claim_data["relatedLot"] = self.initial_lots[0]["id"]
    claim_data["author"] = getattr(self, "test_author", test_tender_below_author)
    tender["complaints"] = [claim_data]
    self.mongodb.tenders.save(tender)

    self.set_status(self.question_claim_block_status, extra={"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertNotIn("next_check", response.json["data"])

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
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
            parse_date(response.json["data"]["tenderPeriod"]["endDate"]),
        )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], self.question_claim_block_status)


# TenderLotBidderResourceTest


def create_tender_bidder_invalid(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
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

    bid_data["lotValues"] = [{"value": {"amount": 5000000}, "relatedLot": self.initial_lots[0]["id"]}]
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
        {"value": {"amount": 500, "valueAddedTaxIncluded": False}, "relatedLot": self.initial_lots[0]["id"]}
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

    bid_data["value"] = {"amount": 500}
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}]

    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["value should be posted for each lot of bid"], "location": "body", "name": "value"}],
    )


def patch_tender_bidder(self):
    lot_id = self.initial_lots[0]["id"]
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id}]
    del bid_data["value"]

    bidder, bid_token = self.create_bid(self.tender_id, bid_data)
    lot = bidder["lotValues"][0]
    lot_values = bidder["lotValues"]

    tenderer = deepcopy(test_tender_below_organization)
    tenderer["name"] = "Державне управління управлінням справами"
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"tenderers": [tenderer]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bidder['id'], bid_token)
    doc_id = response.json["data"]["documents"][-1]["id"]
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {
            "data": {
                "lotValues": [{**lot_values[0], "value": {"amount": 500}, "relatedLot": lot_id}],
                "tenderers": self.test_bids_data[0]["tenderers"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bidder['id'], bid_token, doc_id)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"lotValues": [{**lot_values[0], "value": {"amount": 400}, "relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bidder['id'], bid_token, doc_id)
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])

    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {
            "data": {
                "lotValues": [{**lot_values[0], "value": {"amount": 500}, "relatedLot": lot_id}],
                "status": "active",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update bid in current (unsuccessful) tender status"
    )


# TenderLotFeatureBidderResourceTest


def create_tender_feature_bidder_invalid(self):
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


def create_tender_feature_bidder(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data.update(
        {
            "lotValues": [{"value": {"amount": 500}, "relatedLot": self.lot_id}],
            "parameters": [
                {"code": "code_item", "value": 0.01},
                {"code": "code_tenderer", "value": 0.01},
                {"code": "code_lot", "value": 0.01},
            ],
        }
    )
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bidder = response.json["data"]
    self.assertEqual(bidder["tenderers"][0]["name"], self.initial_data["procuringEntity"]["name"])
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


# TenderLotProcessTest


def one_lot_1bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    tender_response = response.json
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
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    self.set_initial_status(tender_response)
    # create bid

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id}]

    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, bid_data, "pending")
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    # switch to unsuccessful
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def one_lot_2bid_1unqualified(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    tender_response = response.json
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
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    self.set_initial_status(tender_response)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    for i in range(self.min_bids_number):
        bid_data["tenderers"] = self.test_bids_data[i]["tenderers"]
        bid_data["lotValues"] = [{"value": self.test_bids_data[i]["value"], "relatedLot": lot_id}]
        self.create_bid(tender_id, bid_data, "pending")

    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    for i in range(self.min_bids_number - 1):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[i]["id"], owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[-1]["id"], owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.add_sign_doc(tender_id, owner_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    self.set_status("active.auction", {"id": tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def one_lot_2bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    tender_response = response.json
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
    self.set_initial_status(tender_response)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id}]
    bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
    bid_id = bid["id"]
    # create second bid
    bid_data["tenderers"] = self.test_bids_data[1]["tenderers"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[1]["value"], "relatedLot": lot_id}]
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, bid_data, "pending")
    # switch to active.auction
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.status, "200 OK")

    for bid in response.json["data"]["bids"]:
        self.assertEqual(bid["status"], "active")

    self.add_sign_doc(tender_id, owner_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")

    self.time_shift("active.auction")

    self.check_chronograph()

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
        {
            "data": {
                "bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                    for b in auction_bids_data
                ]
            }
        },
    )
    # # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    # after stand slill period

    self.time_shift("complete")
    self.check_chronograph()

    # # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_2bid_1lot_del(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json
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
    self.set_initial_status(tender_response)
    # create bid

    bids = []

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["status"] = "draft"
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id} for lot_id in lots]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    response = self.set_responses(self.tender_id, response.json, "pending")
    bids.append(response.json)
    # create second bid
    bid_data.update(
        {
            "tenderers": self.test_bids_data[1]["tenderers"],
            "lotValues": [{"value": self.test_bids_data[1]["value"], "relatedLot": lot_id} for lot_id in lots],
        }
    )

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    self.set_responses(self.tender_id, response.json, "pending")

    bids.append(response.json)
    response = self.app.delete("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lots[0], owner_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def one_lot_3bid_1del(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json
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
    self.set_initial_status(tender_response)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bids = []
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id}]
    for i in range(3):
        bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
        bids.append({bid["id"]: bid_token})

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, list(bids[2].keys())[0], list(bids[2].values())[0])
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    self.add_sign_doc(tender_id, owner_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    self.time_shift("active.auction")

    self.check_chronograph()
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    data = {
        "data": {
            "lots": [
                {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
            ],
            "bids": [
                (
                    {
                        "id": b["id"],
                        "lotValues": [
                            {"participationUrl": "https://tender.auction.url/for_bid/{}".format(b["id"])}
                            for l in b.get("lotValues", "")
                        ],
                    }
                    if b.get("status", "active") == "active"
                    else {}
                )
                for b in auction_bids_data
            ],
        }
    }
    response = self.app.patch_json("/tenders/{}/auction/{}".format(tender_id, lot_id), data)
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    bid_id = list(bids[0].keys())[0]
    bid1_token = list(bids[0].values())[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid1_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {
            "data": {
                "bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b.get("lotValues", "")]}
                    for b in auction_bids_data
                ]
            }
        },
    )
    # # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    # after stand slill period

    self.time_shift("complete")
    self.check_chronograph()

    # # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def one_lot_3bid_1un(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json
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
    self.set_initial_status(tender_response)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id}]
    bids = []
    for i in range(3):
        bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
        bids.append({bid["id"]: bid_token})

    # switch to active.auction
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    for qualification in qualifications:
        if qualification["bidID"] == list(bids[2].keys())[0]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
                {"data": {"status": "unsuccessful"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "unsuccessful")
        else:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "active")
    self.add_sign_doc(tender_id, owner_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    self.time_shift("active.auction")

    self.check_chronograph()
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    data = {
        "data": {
            "lots": [
                {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
            ],
            "bids": [
                (
                    {
                        "id": b["id"],
                        "lotValues": [
                            {"participationUrl": "https://tender.auction.url/for_bid/{}".format(b["id"])}
                            for l in b["lotValues"]
                        ],
                    }
                    if b.get("status", "active") == "active"
                    else {}
                )
                for b in auction_bids_data
            ],
        }
    }

    response = self.app.patch_json("/tenders/{}/auction/{}".format(tender_id, lot_id), data)
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    bid_id = list(bids[0].keys())[0]
    bid1_token = list(bids[0].values())[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid1_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    bid_id = list(bids[2].keys())[0]
    bid2_token = list(bids[2].values())[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid2_token))
    self.assertEqual("unsuccessful", response.json["data"]["status"])
    self.assertIn("lotValues", response.json["data"])
    self.assertIn("value", response.json["data"]["lotValues"][0])  # value is visible for owner

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid1_token))
    self.assertEqual("unsuccessful", response.json["data"]["status"])
    self.assertIn("lotValues", response.json["data"])
    self.assertNotIn("value", response.json["data"]["lotValues"][0])  # value is not visible for other bidders

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {
            "data": {
                "bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                    for b in auction_bids_data
                ]
            }
        },
    )
    # # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    # after stand slill period

    self.time_shift("complete")
    self.check_chronograph()

    # # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_1can(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json

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
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.set_initial_status(tender_response)
    # cancel first lot

    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)

    if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
        set_complaint_period_end()

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": lots[0],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )

    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id, tender_id, owner_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertFalse(all(i["status"] == "cancelled" for i in response.json["data"]["lots"]))
    self.assertTrue(any(i["status"] == "cancelled" for i in response.json["data"]["lots"]))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # try to restore lot back by old cancellation
    response = self.app.get("/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(len(response.json["data"]), 1)
    cancellation = response.json["data"][0]
    self.assertEqual(cancellation["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(tender_id, cancellation["id"], owner_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can perform cancellation only in active lot status")

    # try to restore lot back by new pending cancellation
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "pending",
            "cancellationOf": "lot",
            "relatedLot": lots[0],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can perform cancellation only in active lot status")
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertFalse(all(i["status"] == "cancelled" for i in response.json["data"]["lots"]))
    self.assertTrue(any(i["status"] == "cancelled" for i in response.json["data"]["lots"]))
    self.assertEqual(response.json["data"]["status"], "active.tendering")


def two_lot_2bid_0com_1can(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json

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
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.set_initial_status(tender_response)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]

    for i in range(self.min_bids_number):
        bid_data.update(
            {
                "tenderers": self.test_bids_data[i]["tenderers"],
                "lotValues": [{"value": self.test_bids_data[i]["value"], "relatedLot": lot_id} for lot_id in lots],
            }
        )
        self.create_bid(tender_id, bid_data, "pending")

    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
        set_complaint_period_end()

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": lots[0],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )

    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id, tender_id, owner_token)

    response = self.app.get("/tenders/{}?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.status, "200 OK")
    # active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number)

    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    self.add_sign_doc(tender_id, owner_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")


def two_lot_2bid_2com_2win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json
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
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.set_initial_status(tender_response)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id} for lot_id in lots]

    _, bid1_token = self.create_bid(tender_id, bid_data, "pending")
    # create second bid
    bid_data["tenderers"] = self.test_bids_data[1]["tenderers"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[1]["value"], "relatedLot": lot_id} for lot_id in lots]

    self.app.authorization = ("Basic", ("broker", ""))
    _, bid2_token = self.create_bid(tender_id, bid_data, "pending")
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 4)

    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    self.add_sign_doc(tender_id, owner_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.time_shift("active.auction")
    self.check_chronograph()
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
            {
                "data": {
                    "bids": [
                        {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                        for b in auction_bids_data
                    ]
                }
            },
        )
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    # after stand still period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid2_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all(i["status"] == "complete" for i in response.json["data"]["lots"]))
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_3bid_1win_bug(self):
    """
    ref: http://prozorro.worksection.ua/project/141436/3931481/#com9856686
    """
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json
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
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")

    self.set_initial_status(tender_response)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id} for lot_id in lots]

    _, bid1_token = self.create_bid(tender_id, bid_data, "pending")
    # create second bid
    bid_data["tenderers"] = self.test_bids_data[1]["tenderers"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[1]["value"], "relatedLot": lot_id} for lot_id in lots]

    self.app.authorization = ("Basic", ("broker", ""))
    _, bid2_token = self.create_bid(tender_id, bid_data, "pending")
    # create third bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid, bid3_token = self.create_bid(tender_id, bid_data, "pending")
    bid_id = bid["id"]
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 6)

    for qualification in qualifications:
        if lots[1] == qualification["lotID"] and bid_id == qualification["bidID"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
                {"data": {"status": "unsuccessful"}},
            )
        else:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
        self.assertEqual(response.status, "200 OK")
        if lots[1] == qualification["lotID"] and bid_id == qualification["bidID"]:
            self.assertEqual(response.json["data"]["status"], "unsuccessful")
        else:
            self.assertEqual(response.json["data"]["status"], "active")
    self.add_sign_doc(tender_id, owner_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.time_shift("active.auction")
    self.check_chronograph()
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
            {
                "data": {
                    "bids": [
                        {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                        for b in auction_bids_data
                    ]
                }
            },
        )
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    self.assertEqual([i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id], [])
    # after stand still period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # ping by chronograph
    self.check_chronograph()
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual({i["status"] for i in response.json["data"]["lots"]}, {"complete", "unsuccessful"})
    self.assertEqual(response.json["data"]["status"], "complete")
