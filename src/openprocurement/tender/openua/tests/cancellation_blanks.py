# -*- coding: utf-8 -*-
from mock import patch
from datetime import timedelta
from copy import deepcopy
from iso8601 import parse_date

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_author, test_organization, test_cancellation,
    test_draft_complaint,
)
from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
    skip_complaint_period_2020_04_19
)


# TenderCancellationResourceTest

@skip_complaint_period_2020_04_19
def create_tender_cancellation(self):

    cancellation_data = dict(**test_cancellation)
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    cancellation_data.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    if get_now() < RELEASE_2020_04_19:
        self.assertEqual(cancellation["status"], "active")
        self.assertIn("id", cancellation)
        self.assertIn(cancellation["id"], response.headers["Location"])
    else:
        self.assertEqual(cancellation["status"], "draft")
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update tender in current (cancelled) status"
    )


@skip_complaint_period_2020_04_19
def patch_tender_cancellation(self):

    cancellation_data = dict(**test_cancellation)

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    old_date_status = response.json["data"]["date"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "active")
        self.assertNotEqual(old_date_status, response.json["data"]["date"])
    else:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

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

    if RELEASE_2020_04_19 < get_now():
        self.set_all_awards_complaint_period_end()

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "active")
    else:
        activate_cancellation_after_2020_04_19(self, cancellation["id"])

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    if get_now() < RELEASE_2020_04_19:
        self.assertEqual(cancellation["status"], "active")
    else:
        self.assertEqual(cancellation["status"], "draft")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])


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

    if RELEASE_2020_04_19 < get_now():
        self.set_all_awards_complaint_period_end()

    cancellation = dict(**test_cancellation)
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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't perform cancellation if all awards are unsuccessful")

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't perform cancellation if all awards are unsuccessful")

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "active")
    else:
        activate_cancellation_after_2020_04_19(self, cancellation["id"])


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() + timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() + timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def create_tender_cancellation_before_19_04_2020(self):
    request_path = "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token)
    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": "noDemand"})
    response = self.app.post_json(
        request_path,
        {"data": cancellation},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

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

    cancellation = dict(**test_cancellation)
    if RELEASE_2020_04_19 < get_now():
        del cancellation["reasonType"]

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["reasonType"], "cancelled")
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "reasonType": "unsuccessful"
    })

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reasonType"], "unsuccessful")
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertEqual(cancellation["status"], "active")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() + timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def patch_tender_cancellation_before_19_04_2020(self):
    cancellation = dict(**test_cancellation)
    if RELEASE_2020_04_19 < get_now():
        del cancellation["reasonType"]

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"reasonType": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["reasonType"], "unsuccessful")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_tender_cancellation_2020_04_19(self):
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if set_complaint_period_end:
        self.set_complaint_period_end()

    reasonType_choices = self.valid_reasonType_choices

    cancellation = dict(**test_cancellation)
    if RELEASE_2020_04_19 < get_now():
        del cancellation["reasonType"]

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=422
    )

    choices = self.valid_reasonType_choices

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"This field is required"],
                u"location": u"body",
                u"name": u"reasonType",
            }
        ],
    )

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "reasonType": "cancelled"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Value must be one of %s" % choices],
                u"location": u"body",
                u"name": u"reasonType",
            }
        ],
    )

    request_path = "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token)

    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0], "status": "active"})
    response = self.app.post_json(
        request_path,
        {"data": cancellation}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn("date", cancellation)

    self.assertEqual(cancellation["reasonType"], reasonType_choices[0])
    self.assertEqual(cancellation["status"], "draft")
    self.assertIn(cancellation_id, response.headers["Location"])

    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": reasonType_choices[1]})
    response = self.app.post_json(
        request_path,
        {"data": cancellation}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["reasonType"], reasonType_choices[1])
    self.assertEqual(cancellation["status"], "draft")
    self.assertIn(cancellation_id, response.headers["Location"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    if tender["procurementMethodType"] in ["reporting", "negotiation", "negotiation.quick"]:
        self.assertEqual(response.json["data"]["status"], "active")
    else:
        self.assertEqual(response.json["data"]["status"], "active.tendering")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.utils.RELEASE_2020_04_19",
            get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def patch_tender_cancellation_2020_04_19(self):
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if set_complaint_period_end:
        self.set_complaint_period_end()

    reasonType_choices = self.valid_reasonType_choices

    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["status"], "draft")
    self.assertEqual(cancellation["reasonType"], reasonType_choices[0])
    self.assertIn(cancellation_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"reasonType": reasonType_choices[1]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["reasonType"], reasonType_choices[1])

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"reasonType": "cancelled"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Value must be one of %s" % reasonType_choices],
                u"location": u"body",
                u"name": u"reasonType",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            u"description": u"Fields reason, cancellationOf and documents must be filled for switch cancellation to pending status",
            u"location": u"body",
            u"name": u"data",
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "active"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            u"description": u"Cancellation can't be updated from draft to active status",
            u"location": u"body",
            u"name": u"data",
        }]
    )

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    request_path = "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id,
                                                                      self.tender_token)
    response = self.app.patch_json(
        request_path,
        {"data": {"status": "pending", "reasonType": reasonType_choices[1]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reasonType"], reasonType_choices[1])
    self.assertEqual(cancellation["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "draft"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            u"description": u"Cancellation can't be updated from pending to draft status",
            u"location": u"body",
            u"name": u"data",
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "active"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            u"description": u"Cancellation can't be updated from pending to active status",
            u"location": u"body",
            u"name": u"data",
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            u"description": u"Cancellation can't be updated from pending to unsuccessful status",
            u"location": u"body",
            u"name": u"data",
        }]
    )

    # Create complaint and update to satisfied status

    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_author,
        "status": "pending"
    }

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint_id = response.json["data"]["id"]
    complaint_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(
                self.tender_id, cancellation_id, complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("reviewer", ""))

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_id, self.tender_token),
        {"data": {
            "status": "accepted",
            "reviewDate": get_now().isoformat(),
            "reviewPlace": "some",
        }},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "accepted")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_id, self.tender_token),
        {"data": {"status": "satisfied"}},
    )

    self.app.authorization = auth
    # end

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_id, self.tender_token),
        {"data": {"status": "resolved", "tendererAction": "tenderer some action"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "resolved")

    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if set_complaint_period_end:
        set_complaint_period_end()

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            u"description": u"Can't update cancellation in current (unsuccessful) status",
            u"location": u"body",
            u"name": u"data",
        }]
    )

    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["reasonType"], reasonType_choices[0])
    self.assertEqual(cancellation["status"], "draft")
    self.assertIn(cancellation_id, response.headers["Location"])

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["status"], "pending")

    with patch(
            "openprocurement.tender.core.utils.get_now",
            return_value=get_now() + timedelta(days=11)):
        response = self.check_chronograph()

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
        status=403
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            u"description": u"Can't update tender in current (cancelled) status",
            u"location": u"body",
            u"name": u"data",
        }]
    )


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def access_create_tender_cancellation_complaint(self):
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if set_complaint_period_end:
        self.set_complaint_period_end()

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])
    self.assertIn("startDate", response.json["data"]["complaintPeriod"])
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])

    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_author,
        "status": "pending"
    }

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, self.cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint_id = response.json["data"]["id"]
    complaint_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(
                self.tender_id, self.cancellation_id, complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("reviewer", ""))

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token),
        {"data": {
            "status": "accepted",
            "reviewDate": get_now().isoformat(),
            "reviewPlace": "some",
        }},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "accepted")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token),
        {"data": {"status": "satisfied"}},
    )

    self.app.authorization = auth

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    with patch(
            "openprocurement.tender.core.views.cancellation_complaint.get_now",
            return_value=get_now() + timedelta(days=5)):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.cancellation_id, complaint_id, self.tender_token),
            {"data": {"tendererAction": "Tenderer action"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        data = response.json["data"]
        self.assertEqual(data["tendererAction"], u"Tenderer action")
        self.assertEqual(data["status"], u"resolved")

    self.set_status("active.qualification")

    bid = self.initial_bids[0]
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_organization],
                "status": "pending",
                "bid_id": bid["id"],
                "lotID": self.initial_lots[0]["id"] if self.initial_lots else None
            }
        },
    )
    award = response.json["data"]
    self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award["id"]),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    self.set_all_awards_complaint_period_end()

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "reasonType": "noDemand"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {"data": {"status": "pending"}})

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    self.app.authorization = ("Basic", ("broker", ""))

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, cancellation_id),
        {"data": complaint_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u"description": u"Forbidden",
            u"location": u"url",
            u"name": u"permission",
        }],
    )
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints?acc_token={}".format(
            self.tender_id, cancellation_id, bid_token),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("value", response.json["data"])


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def permission_cancellation_pending(self):
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if set_complaint_period_end:
        self.set_complaint_period_end()

    reasonType_choices = self.valid_reasonType_choices

    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_1 = response.json["data"]
    cancellation_1_id = cancellation_1["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation_1)
    self.assertIn("date", cancellation_1)
    self.assertEqual(cancellation_1["status"], "draft")
    self.assertEqual(cancellation_1["reasonType"], reasonType_choices[0])
    self.assertIn(cancellation_1_id, response.headers["Location"])

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_2 = response.json["data"]
    cancellation_2_id = cancellation_2["id"]
    self.assertEqual(cancellation_2["reason"], "cancellation reason")
    self.assertEqual(cancellation_2["status"], "draft")

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_1_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, cancellation_1_id, self.tender_token
        ),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])
    self.assertIn("startDate", response.json["data"]["complaintPeriod"])
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_2_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, cancellation_2_id, self.tender_token
        ),
        {"data": {"reasonType": reasonType_choices[1]}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def activate_cancellation(self):
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if set_complaint_period_end:
        self.set_complaint_period_end()

    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_author,
        "status": "pending"
    }

    reasonType_choices = self.valid_reasonType_choices

    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    self.assertEqual(response.status, "201 Created")

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])
    self.assertIn("startDate", response.json["data"]["complaintPeriod"])
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])

    complaint_draft_data = deepcopy(complaint_data)
    complaint_draft_data["status"] = "draft"

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, cancellation_id),
        {"data": complaint_draft_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "draft")
    complaint_1_id = response.json["data"]["id"]
    complaint_1_token = response.json["access"]["token"]

    # Complaint 2
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    complaint_2_id = response.json["data"]["id"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(
                self.tender_id, cancellation_id, complaint_2_id),
            {"data": {"status": "pending"}},
        )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "pending")

    # Complain 3
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    complaint_3_id = response.json["data"]["id"]
    complaint_3_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(
                self.tender_id, cancellation_id, complaint_3_id),
            {"data": {"status": "pending"}},
        )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "pending")


    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_1_id, complaint_1_token),
        {"data": {"status": "mistaken"}},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "cancelledByComplainant")

    with patch(
            "openprocurement.tender.core.utils.get_now",
            return_value=get_now() + timedelta(days=11)):
        response = self.check_chronograph()

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("reviewer", ""))

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_2_id, self.tender_token),
        {"data": {
            "status": "accepted",
            "reviewDate": get_now().isoformat(),
            "reviewPlace": "some",
        }},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "accepted")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_2_id, self.tender_token),
        {"data": {"status": "declined"}},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "declined")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_3_id, self.tender_token),
        {"data": {
            "status": "invalid",
            "rejectReason": "tenderCancelled",
            "rejectReasonDescription": "reject reason description",
        }},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "invalid")

    with patch(
            "openprocurement.tender.core.utils.get_now",
            return_value=get_now() + timedelta(days=11)):
        response = self.check_chronograph()

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_tender_cancellation_complaint(self):
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if set_complaint_period_end:
        self.set_complaint_period_end()

    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_author,
        "status": "pending"
    }

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, self.cancellation_id),
        {"data": complaint_data},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u"description": u"Complaint can be add only in pending status of cancellation",
            u"location": u"body",
            u"name": u"data"
        }],
    )

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])
    self.assertIn("startDate", response.json["data"]["complaintPeriod"])
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, self.cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertIn("id", complaint)
    self.assertEqual(complaint["status"], "draft")
    self.assertEqual(complaint["description"], complaint_data["description"])
    self.assertIn(complaint["id"], response.headers["Location"])
    complaint_id = complaint["id"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(
                self.tender_id, self.cancellation_id, complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("reviewer", ""))
    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, owner_token),
        {"data": {
            "status": "invalid",
            "rejectReason": "tenderCancelled",
            "rejectReasonDescription": "reject reason description",
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.app.authorization = auth

    with patch(
            "openprocurement.tender.core.validation.get_now",
            return_value=get_now() + timedelta(days=11)) as mock_date:
        response = self.app.post_json(
            "/tenders/{}/cancellations/{}/complaints?acc_token={}".format(
                self.tender_id, self.cancellation_id, self.tender_token),
            {"data": complaint_data},
            status=422
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{
                u"description": u"Complaint can't be add after finish of complaint period",
                u"location": u"body",
                u"name": u"data"
            }],
        )

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, self.cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    self.assertIn("id", complaint)
    self.assertEqual(complaint["status"], "draft")
    self.assertEqual(complaint["description"], complaint_data["description"])
    self.assertIn(complaint["id"], response.headers["Location"])


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def patch_tender_cancellation_complaint(self):
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if set_complaint_period_end:
        self.set_complaint_period_end()

    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_author,
        "status": "pending",
    }

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])
    self.assertIn("startDate", response.json["data"]["complaintPeriod"])
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertIn("id", complaint)
    self.assertEqual(complaint["status"], "draft")
    self.assertEqual(complaint["description"], complaint_data["description"])
    self.assertIn(complaint["id"], response.headers["Location"])
    complaint_id = complaint["id"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(
                self.tender_id, self.cancellation_id, complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("reviewer", ""))

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token),
        {"data": {
            "status": "accepted",
            "reviewDate": get_now().isoformat(),
            "reviewPlace": "some",
        }},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "accepted")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token),
        {"data": {"status": "satisfied"}},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "satisfied")

    self.app.authorization = auth
    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token),
        {"data": {"tendererAction": "Tenderer action"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u"description": u"Complaint can't have tendererAction only if cancellation not in unsuccessful status",
            u"location": u"body",
            u"name": u"data"
        }],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, owner_token),
        {"data": {"tendererAction": "Tenderer action"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u"description": u"Forbidden",
            u"location": u"url",
            u"name": u"role"
        }],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    with patch(
            "openprocurement.tender.core.views.cancellation_complaint.get_now",
            return_value=get_now() + timedelta(days=5)) as mocked:

        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.cancellation_id, complaint_id, self.tender_token),
            {"data": {"tendererAction": "Tenderer action"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        data = response.json["data"]
        self.assertEqual(data["tendererAction"], u"Tenderer action")
        self.assertEqual(data["status"], u"resolved")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def get_tender_cancellation_complaints(self):
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if set_complaint_period_end:
        self.set_complaint_period_end()

    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_author,
    }

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])
    self.assertIn("startDate", response.json["data"]["complaintPeriod"])
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token),
        {"data": complaint_data, "status": "claim"},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    self.assertIn("id", complaint)
    self.assertEqual(complaint["status"], "draft")
    self.assertEqual(complaint["description"], complaint_data["description"])
    self.assertIn(complaint["id"], response.headers["Location"])

    response = self.app.get(
        "/tenders/{}/cancellations/{}/complaints".format(
            self.tender_id, self.cancellation_id, self.tender_token),
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], complaint)

    response = self.app.get("/tenders/some_id/cancellations", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_tender_cancellation_with_cancellation_lots(self):
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)

    if set_complaint_period_end:
        set_complaint_period_end()

    cancellation_data = dict(**test_cancellation)
    cancellation_data["reasonType"] = "noDemand"

    cancellation_lot_data = dict(**cancellation_data)
    lot = self.initial_lots[0]

    cancellation_lot_data["relatedLot"] = lot["id"]
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_lot_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_data},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden",
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_lot_data},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden",
    )


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def bot_patch_tender_cancellation_complaint(self):
    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    complaint_data = deepcopy(test_draft_complaint)
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.cancellation_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_cancellation_in_tender_complaint_period(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    complaint_period = tender["complaintPeriod"]
    self.assertIn("startDate", complaint_period)
    self.assertIn("endDate", complaint_period)
    start_date = parse_date(complaint_period["startDate"])
    end_date = parse_date(complaint_period["endDate"])

    now = get_now()
    self.assertGreater(now, start_date)
    self.assertLess(now, end_date)

    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": "noDemand"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u"description": u"Cancellation can't be add when exists active complaint period",
            u"location": u"body",
            u"name": u"data"
        }],
    )

    self.set_complaint_period_end()

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_cancellation_in_award_complaint_period(self):
    self.set_status("active.qualification")

    bid = self.initial_bids[0]
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_organization],
                "status": "pending",
                "bid_id": bid["id"],
                "lotID": self.initial_lots[0]["id"] if self.initial_lots else None
            }
        },
    )
    award = response.json["data"]
    self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award["id"]),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    complaint_period = tender["complaintPeriod"]
    end_date = parse_date(complaint_period["endDate"])

    self.assertGreater(get_now(), end_date)

    cancellation = dict(**test_cancellation)
    cancellation.update({"reasonType": "noDemand"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u"description": u"Cancellation can't be add when exists active complaint period",
            u"location": u"body",
            u"name": u"data"
        }],
    )

    self.set_all_awards_complaint_period_end()

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
