# -*- coding: utf-8 -*-

# TenderCancellationResourceTest

import mock
from datetime import timedelta

from openprocurement.api.utils import get_now


@mock.patch(
    "openprocurement.tender.core.models.RELEASE_2020_04_19",
    get_now() + timedelta(days=1)
)
def create_tender_cancellation(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"reason": "cancellation reason"}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["reasonType"], "cancelled")
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"reason": "cancellation reason", "reasonType": "unFixable"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Value must be one of %s" % ["cancelled", "unsuccessful"]],
                u"location": u"body",
                u"name": u"reasonType",
            }
        ],
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"reason": "cancellation reason", "status": "active", "reasonType": "unsuccessful"}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reasonType"], "unsuccessful")
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertEqual(cancellation["status"], "active")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"reason": "cancellation reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update tender in current (cancelled) status"
    )


@mock.patch(
    "openprocurement.tender.core.models.RELEASE_2020_04_19",
    get_now() + timedelta(days=1)
)
def patch_tender_cancellation(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"reason": "cancellation reason"}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    old_date_status = response.json["data"]["date"]
    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"reasonType": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["reasonType"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotEqual(old_date_status, response.json["data"]["date"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update tender in current (cancelled) status"
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"cancellation_id"}]
    )

    response = self.app.patch_json("/tenders/some_id/cancellations/some_id", {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["reason"], "cancellation reason")


# TenderAwardsCancellationResourceTest


@mock.patch(
    "openprocurement.tender.core.models.RELEASE_2020_04_19",
    get_now() + timedelta(days=1)
)
def cancellation_active_award(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for i in self.initial_lots:
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(self.tender_id, i["id"]), {"data": {"bids": auction_bids_data}}
        )

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [
        i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
    ][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "reason": "cancellation reason",
                "status": "active",
                "cancellationOf": "lot",
                "relatedLot": self.initial_lots[0]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertEqual(cancellation["status"], "active")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"reason": "cancellation reason", "status": "active"}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertEqual(cancellation["status"], "active")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])


@mock.patch(
    "openprocurement.tender.core.models.RELEASE_2020_04_19",
    get_now() + timedelta(days=1)
)
def cancellation_unsuccessful_award(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for i in self.initial_lots:
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(self.tender_id, i["id"]), {"data": {"bids": auction_bids_data}}
        )

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [
        i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
    ][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [
        i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
    ][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "reason": "cancellation reason",
                "status": "active",
                "cancellationOf": "lot",
                "relatedLot": self.initial_lots[0]["id"],
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't perform cancellation if all awards are unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"reason": "cancellation reason", "status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't perform cancellation if all awards are unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "reason": "cancellation reason",
                "status": "active",
                "cancellationOf": "lot",
                "relatedLot": self.initial_lots[1]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertEqual(cancellation["status"], "active")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])
