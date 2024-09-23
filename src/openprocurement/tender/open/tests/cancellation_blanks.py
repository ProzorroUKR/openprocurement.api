from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_cancellation,
    test_tender_below_complaint,
    test_tender_below_draft_complaint,
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.core.tests.utils import change_auth


def create_tender_cancellation(self):
    cancellation_data = deepcopy(test_tender_below_cancellation)
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

    cancellation_data.update(
        {
            "status": "active",
        }
    )
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
        {"data": test_tender_below_cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
    )


def patch_tender_cancellation(self):
    cancellation_data = deepcopy(test_tender_below_cancellation)

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
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
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
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "cancellation_id"}]
    )

    response = self.app.patch_json("/tenders/some_id/cancellations/some_id", {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["reason"], "cancellation reason")


def cancellation_active_award(self):
    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        for i in self.initial_lots:
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, i["id"]),
                {
                    "data": {
                        "bids": [
                            {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                            for b in auction_bids_data
                        ]
                    }
                },
            )

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [
        i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
    ][0]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    if RELEASE_2020_04_19 < get_now():
        self.set_all_awards_complaint_period_end()

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

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
        }
    )
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
    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        for i in self.initial_lots:
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, i["id"]),
                {
                    "data": {
                        "bids": [
                            {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                            for b in auction_bids_data
                        ]
                    }
                },
            )

    with change_auth(self.app, ("Basic", ("broker", ""))):
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        award_id = [
            i["id"]
            for i in response.json["data"]
            if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
        ][0]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
            {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        )

        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        award_id = [
            i["id"]
            for i in response.json["data"]
            if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
        ][0]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
            {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        )

        if RELEASE_2020_04_19 < get_now():
            self.set_all_awards_complaint_period_end()

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
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation if all awards are unsuccessful"
    )

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation if all awards are unsuccessful"
    )

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[1]["id"],
        }
    )
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


def cancellation_lot_during_qualification_after_first_winner_chosen(self):
    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get(f"/tenders/{self.tender_id}/auction")
        auction_bids_data = response.json["data"]["bids"]
        for i in self.initial_lots:
            self.app.post_json(
                f"/tenders/{self.tender_id}/auction/{i['id']}",
                {
                    "data": {
                        "bids": [
                            {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                            for b in auction_bids_data
                        ]
                    }
                },
            )

    # there are two pending awards for two active lots
    # let's make award for the first lot a winner
    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.get(f"/tenders/{self.tender_id}/awards")
        self.assertEqual(len(response.json["data"]), 2)
        self.assertEqual(response.json["data"][0]["status"], "pending")
        self.assertEqual(response.json["data"][1]["status"], "pending")
        award_id = [
            i["id"]
            for i in response.json["data"]
            if i["status"] == "pending" and i["lotID"] == self.initial_lots[0]["id"]
        ][0]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    self.set_all_awards_complaint_period_end()

    # cancel the second lot which has pending award
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[1]["id"],
        }
    )
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations?acc_token={self.tender_token}",
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertEqual(cancellation["status"], "draft")

    activate_cancellation_after_2020_04_19(self, cancellation["id"])

    # complaintPeriod is over, that's why second lot become 'cancelled', award for this lot stays 'pending'

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "active")
    self.assertEqual(response.json["data"]["lots"][1]["status"], "cancelled")
    self.assertEqual(response.json["data"]["awards"][0]["status"], "active")
    self.assertEqual(response.json["data"]["awards"][1]["status"], "pending")
    # tender goes to 'active.awarded' as already has the winner for active lot, another lot is cancelled
    self.assertEqual(response.json["data"]["status"], "active.awarded")


def cancellation_lot_during_qualification_before_winner_chosen(self):
    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get(f"/tenders/{self.tender_id}/auction")
        auction_bids_data = response.json["data"]["bids"]
        for i in self.initial_lots:
            self.app.post_json(
                f"/tenders/{self.tender_id}/auction/{i['id']}",
                {
                    "data": {
                        "bids": [
                            {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                            for b in auction_bids_data
                        ]
                    }
                },
            )

    # there are two pending awards for two active lots
    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.get(f"/tenders/{self.tender_id}/awards")
        self.assertEqual(len(response.json["data"]), 2)
        self.assertEqual(response.json["data"][0]["status"], "pending")
        self.assertEqual(response.json["data"][1]["status"], "pending")

    # cancel the second lot which has pending award
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[1]["id"],
        }
    )
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations?acc_token={self.tender_token}",
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertEqual(cancellation["status"], "draft")

    activate_cancellation_after_2020_04_19(self, cancellation["id"])

    # complaintPeriod is over, that's why second lot become 'cancelled', award for this lot stays 'pending'
    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "active")
    self.assertEqual(response.json["data"]["lots"][1]["status"], "cancelled")
    self.assertEqual(response.json["data"]["awards"][0]["status"], "pending")
    self.assertEqual(response.json["data"]["awards"][1]["status"], "pending")
    # tender stays at 'active.qualification' as doesn't have the winner for active lot, another lot is cancelled
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    # let's make award for the first lot a winner
    award_id = [i["id"] for i in response.json["data"]["awards"] if i["lotID"] == self.initial_lots[0]["id"]][0]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    self.set_all_awards_complaint_period_end()

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "active")
    self.assertEqual(response.json["data"]["lots"][1]["status"], "cancelled")
    self.assertEqual(response.json["data"]["awards"][0]["status"], "active")
    self.assertEqual(response.json["data"]["awards"][1]["status"], "pending")
    # tender goes to 'active.awarded' as already has the winner for active lot, another lot is cancelled
    self.assertEqual(response.json["data"]["status"], "active.awarded")


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def create_tender_cancellation_before_19_04_2020(self):
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": "noDemand"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
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
                "description": ["Value must be one of %s" % ["cancelled", "unsuccessful"]],
                "location": "body",
                "name": "reasonType",
            }
        ],
    )

    cancellation = deepcopy(test_tender_below_cancellation)
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

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"status": "active", "reasonType": "unsuccessful"})

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


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def patch_tender_cancellation_before_19_04_2020(self):
    cancellation = deepcopy(test_tender_below_cancellation)
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


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_tender_cancellation_2020_04_19(self):
    reasonType_choices = self.valid_reasonType_choices

    cancellation = deepcopy(test_tender_below_cancellation)
    if RELEASE_2020_04_19 < get_now():
        del cancellation["reasonType"]

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=422,
    )

    choices = self.valid_reasonType_choices

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["This field is required"],
                "location": "body",
                "name": "reasonType",
            }
        ],
    )

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": "cancelled"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Value must be one of %s" % choices],
                "location": "body",
                "name": "reasonType",
            }
        ],
    )

    request_path = "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token)

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(request_path, {"data": cancellation})
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

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[1]})
    response = self.app.post_json(request_path, {"data": cancellation})
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


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_cancellation_with_tender_complaint(self):
    # Create tender complaint
    complaint_data = deepcopy(test_tender_below_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender_complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    auth = self.app.authorization
    self.app.authorization = ('Basic', ('bot', ''))

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, tender_complaint["id"], owner_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.app.authorization = auth

    cancellation_data = deepcopy(test_tender_below_cancellation)
    cancellation_data.update({"reasonType": self.valid_reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't perform operation for there is a tender complaint in pending status",
    )

    auth = self.app.authorization
    self.app.authorization = ('Basic', ('reviewer', ''))

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, tender_complaint["id"], owner_token),
        {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_cancellation_with_award_complaint(self):
    self.set_status("active.qualification")

    bid = self.initial_bids[0]
    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": self.initial_lots[0]["id"] if self.initial_lots else None,
                }
            },
        )
        award = response.json["data"]
        award_id = award["id"]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    # Create award complaint
    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    complaint_data = deepcopy(test_tender_below_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_id, bid_token),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award_complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    self.set_all_awards_complaint_period_end()

    with change_auth(self.app, ('Basic', ('bot', ''))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, award_id, award_complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "reasonType": "noDemand",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't perform operation for there is an award complaint in pending status",
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def patch_tender_cancellation_2020_04_19(self):
    reasonType_choices = self.valid_reasonType_choices

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]
    self.assertEqual(response.json["data"]["reason"], "cancellation reason")
    self.assertEqual(response.json["data"]["status"], "draft")
    self.assertEqual(response.json["data"]["reasonType"], reasonType_choices[0])
    self.assertIn(cancellation_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
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

    for reasonType_choice in self.valid_reasonType_choices:
        if reasonType_choice != cancellation["reasonType"]:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(
                    self.tender_id, cancellation['id'], self.tender_token
                ),
                {"data": {"reasonType": reasonType_choice}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["reasonType"], reasonType_choice)

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
                "description": ["Value must be one of %s" % reasonType_choices],
                "location": "body",
                "name": "reasonType",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Fields reason, cancellationOf and documents must be filled for switch cancellation to pending status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't switch cancellation status from draft to active",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    request_path = "/tenders/{}/cancellations/{}?acc_token={}".format(
        self.tender_id, cancellation_id, self.tender_token
    )
    response = self.app.patch_json(
        request_path,
        {"data": {"status": "pending", "reasonType": reasonType_choices[1]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reasonType"], reasonType_choices[1])
    self.assertEqual(cancellation["status"], "pending")

    response = self.app.get(f"/tenders/{self.tender_id}")
    tender_data = response.json["data"]
    self.assertEqual(tender_data["next_check"], cancellation["complaintPeriod"]["endDate"])

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "draft"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't switch cancellation status from pending to draft",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't switch cancellation status from pending to active",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can\'t switch cancellation status from pending to unsuccessful",
                "location": "body",
                "name": "data",
            }
        ],
    )

    # Create complaint and update to satisfied status

    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_tender_below_author,
        "status": "pending",
    }

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint_id = response.json["data"]["id"]
    complaint_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(self.tender_id, cancellation_id, complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("reviewer", ""))

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_id, self.tender_token
        ),
        {
            "data": {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "some",
            }
        },
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "accepted")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_id, self.tender_token
        ),
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
            self.tender_id, cancellation_id, complaint_id, self.tender_token
        ),
        {"data": {"status": "resolved", "tendererAction": "tenderer some action"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "resolved")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"reasonType": "forceMajeure"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update cancellation in current (unsuccessful) status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
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

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
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

    tender = self.mongodb.tenders.get(self.tender_id)
    for c in tender["cancellations"]:
        if c["status"] == "pending":
            c["complaintPeriod"]["endDate"] = get_now().isoformat()
    self.mongodb.tenders.save(tender)

    self.check_chronograph()

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't perform cancellation in current (cancelled) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def patch_tender_cancellation_2020_04_19_to_pending(self):
    reasonType_choices = self.valid_reasonType_choices
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})

    # draft 1
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
    )
    cancellation_1_id = response.json["data"]["id"]

    # draft 2
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
    )
    cancellation_2_id = response.json["data"]["id"]

    # adding docs
    self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_1_id}/documents?acc_token={self.tender_token}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_2_id}/documents?acc_token={self.tender_token}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )

    # activate 1
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_1_id}?acc_token={self.tender_token}",
        {"data": {"status": "pending", "reasonType": reasonType_choices[1]}},
    )
    cancellation = response.json["data"]
    self.assertEqual(cancellation["status"], "pending")

    # activate 2
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_2_id}?acc_token={self.tender_token}",
        {"data": {"status": "pending", "reasonType": reasonType_choices[1]}},
        status=403,
    )
    self.assertEqual(
        [{"location": "body", "name": "data", "description": "Forbidden because of a pending cancellation"}],
        response.json["errors"],
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def access_create_tender_cancellation_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])
    self.assertIn("startDate", response.json["data"]["complaintPeriod"])
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])

    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_tender_below_author,
        "status": "pending",
    }

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, self.cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint_id = response.json["data"]["id"]
    complaint_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(self.tender_id, self.cancellation_id, complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.cancellation_id, complaint_id, self.tender_token
            ),
            {
                "data": {
                    "status": "accepted",
                    "reviewDate": get_now().isoformat(),
                    "reviewPlace": "some",
                }
            },
        )
        complaint = response.json["data"]
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(complaint["status"], "accepted")

        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.cancellation_id, complaint_id, self.tender_token
            ),
            {"data": {"status": "satisfied"}},
        )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token
        ),
        {"data": {"tendererAction": "Tenderer action"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    data = response.json["data"]
    self.assertEqual(data["tendererAction"], "Tenderer action")
    self.assertEqual(data["status"], "resolved")

    self.set_status("active.qualification")

    bid = self.initial_bids[0]

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": self.initial_lots[0]["id"] if self.initial_lots else None,
                }
            },
        )
        award = response.json["data"]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    self.set_all_awards_complaint_period_end()

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": "noDemand"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    self.app.authorization = ("Basic", ("broker", ""))

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation_id),
        {"data": complaint_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Forbidden",
                "location": "url",
                "name": "permission",
            }
        ],
    )
    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json(
            "/tenders/{}/cancellations/{}/complaints?acc_token={}".format(self.tender_id, cancellation_id, bid_token),
            {"data": complaint_data},
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("value", response.json["data"])


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def permission_cancellation_pending(self):
    reasonType_choices = self.valid_reasonType_choices

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
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
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_2 = response.json["data"]
    cancellation_2_id = cancellation_2["id"]
    self.assertEqual(cancellation_2["reason"], "cancellation reason")
    self.assertEqual(cancellation_2["status"], "draft")

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_1_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_1_id, self.tender_token),
        {"data": {"status": "pending"}},
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
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden because of a pending cancellation")

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_2_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden because of a pending cancellation")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_2_id, self.tender_token),
        {"data": {"reasonType": reasonType_choices[1]}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden because of a pending cancellation")


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def activate_cancellation(self):
    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_tender_below_author,
        "status": "pending",
    }

    reasonType_choices = self.valid_reasonType_choices

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    self.assertEqual(response.status, "201 Created")

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])
    self.assertIn("startDate", response.json["data"]["complaintPeriod"])
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])

    complaint_draft_data = deepcopy(complaint_data)
    complaint_draft_data["status"] = "draft"

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation_id),
        {"data": complaint_draft_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "draft")
    complaint_1_id = response.json["data"]["id"]
    complaint_1_token = response.json["access"]["token"]

    # Complaint 2
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    complaint_2_id = response.json["data"]["id"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(self.tender_id, cancellation_id, complaint_2_id),
            {"data": {"status": "pending"}},
        )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "pending")

    # Complain 3
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    complaint_3_id = response.json["data"]["id"]
    complaint_3_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}/complaints/{}".format(self.tender_id, cancellation_id, complaint_3_id),
            {"data": {"status": "pending"}},
        )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_1_id, complaint_1_token
        ),
        {"data": {"status": "mistaken"}},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "cancelledByComplainant")

    with patch("openprocurement.tender.core.procedure.utils.get_now", return_value=get_now() + timedelta(days=11)):
        response = self.check_chronograph()

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("reviewer", ""))

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_2_id, self.tender_token
        ),
        {
            "data": {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "some",
            }
        },
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "accepted")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_2_id, self.tender_token
        ),
        {"data": {"status": "declined"}},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "declined")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, cancellation_id, complaint_3_id, self.tender_token
        ),
        {
            "data": {
                "status": "invalid",
                "rejectReason": "tenderCancelled",
                "rejectReasonDescription": "reject reason description",
            }
        },
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "invalid")

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["cancellations"][0]["complaintPeriod"]["endDate"] = get_now().isoformat()
    self.mongodb.tenders.save(tender)

    self.check_chronograph()

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_tender_cancellation_complaint(self):
    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_tender_below_author,
        "status": "pending",
    }

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, self.cancellation_id),
        {"data": complaint_data},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Complaint can be add only in pending status of cancellation",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])
    self.assertIn("startDate", response.json["data"]["complaintPeriod"])
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, self.cancellation_id),
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
            "/tenders/{}/cancellations/{}/complaints/{}".format(self.tender_id, self.cancellation_id, complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("reviewer", ""))
    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, owner_token
        ),
        {
            "data": {
                "status": "invalid",
                "rejectReason": "tenderCancelled",
                "rejectReasonDescription": "reject reason description",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.app.authorization = auth

    with patch(
        "openprocurement.tender.core.procedure.state.cancellation_complaint.get_now",
        return_value=get_now() + timedelta(days=11),
    ):
        response = self.app.post_json(
            "/tenders/{}/cancellations/{}/complaints?acc_token={}".format(
                self.tender_id, self.cancellation_id, self.tender_token
            ),
            {"data": complaint_data},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": "Complaint can't be add after finish of complaint period",
                    "location": "body",
                    "name": "data",
                }
            ],
        )

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, self.cancellation_id),
        {"data": complaint_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    self.assertIn("id", complaint)
    self.assertEqual(complaint["status"], "draft")
    self.assertEqual(complaint["description"], complaint_data["description"])
    self.assertIn(complaint["id"], response.headers["Location"])


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def patch_tender_cancellation_complaint(self):
    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_tender_below_author,
        "status": "pending",
    }

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, self.cancellation_id, self.tender_token),
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
            self.tender_id, self.cancellation_id, self.tender_token
        ),
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
            "/tenders/{}/cancellations/{}/complaints/{}".format(self.tender_id, self.cancellation_id, complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("reviewer", ""))

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token
        ),
        {
            "data": {
                "status": "accepted",
                "reviewDate": get_now().isoformat(),
                "reviewPlace": "some",
            }
        },
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "accepted")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token
        ),
        {"data": {"status": "satisfied"}},
    )
    complaint = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(complaint["status"], "satisfied")

    self.app.authorization = auth
    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token
        ),
        {"data": {"tendererAction": "Tenderer action"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Complaint can't have tendererAction only if cancellation not in unsuccessful status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, owner_token
        ),
        {"data": {"tendererAction": "Tenderer action"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, complaint_id, self.tender_token
        ),
        {"data": {"tendererAction": "Tenderer action"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    data = response.json["data"]
    self.assertEqual(data["tendererAction"], "Tenderer action")
    self.assertEqual(data["status"], "resolved")


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def get_tender_cancellation_complaints(self):
    complaint_data = {
        "title": "complaint title",
        "description": "complaint description",
        "author": test_tender_below_author,
    }

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, self.cancellation_id, self.tender_token),
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
            self.tender_id, self.cancellation_id, self.tender_token
        ),
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
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, self.cancellation_id, self.tender_token),
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], complaint)

    response = self.app.get("/tenders/some_id/cancellations", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_tender_cancellation_with_cancellation_lots(self):
    cancellation_data = deepcopy(test_tender_below_cancellation)
    cancellation_data["reasonType"] = "noDemand"

    cancellation_lot_data = deepcopy(cancellation_data)
    lot = self.initial_lots[0]

    cancellation_lot_data["relatedLot"] = lot["id"]
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_lot_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden because of a pending cancellation",
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_lot_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden because of a pending cancellation",
    )


def create_tender_lots_cancellation_complaint(self):
    cancellation_data = deepcopy(test_tender_below_cancellation)
    cancellation_data["reasonType"] = "noDemand"

    cancellation_lot_data = deepcopy(cancellation_data)
    lot = self.initial_lots[0]

    cancellation_lot_data["relatedLot"] = lot["id"]
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_lot_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertIn("complaintPeriod", response.json["data"])

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/complaints?acc_token={self.tender_token}",
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["relatedLot"], lot["id"])


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_lot_cancellation_with_tender_cancellation(self):
    cancellation_data = deepcopy(test_tender_below_cancellation)
    cancellation_data["reasonType"] = "noDemand"

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_data},
    )
    cancellation_id = response.json["data"]["id"]

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden because of a pending cancellation",
    )

    cancellation_lot_data = deepcopy(cancellation_data)
    lot = self.initial_lots[0]
    cancellation_lot_data["relatedLot"] = lot["id"]
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_lot_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden because of a pending cancellation",
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def bot_patch_tender_cancellation_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, self.cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    complaint_data = deepcopy(test_tender_below_draft_complaint)
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


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_cancellation_in_award_complaint_period(self):
    self.set_status("active.qualification")
    bid = self.initial_bids[0]
    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": self.initial_lots[0]["id"] if self.initial_lots else None,
                }
            },
        )
        award = response.json["data"]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": "noDemand"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Cancellation can't be add when exists active complaint period",
                "location": "body",
                "name": "data",
            }
        ],
    )

    self.set_all_awards_complaint_period_end()

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


# TenderDPSLotCancellationResourceTest


def create_tender_dps_lot_cancellation_complaint(self):
    cancellation_data = deepcopy(test_tender_below_cancellation)
    cancellation_data["reasonType"] = "noDemand"

    cancellation_lot_data = deepcopy(cancellation_data)
    lot = self.initial_lots[0]

    cancellation_lot_data["relatedLot"] = lot["id"]
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_lot_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.json["data"]["status"], "active")  # as we don't have complaintPeriod
    self.assertNotIn("complaintPeriod", response.json["data"])

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/complaints?acc_token={self.tender_token}",
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint as it is forbidden by configuration"
    )

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def patch_tender_dps_lot_cancellation(self):
    lot_id = self.initial_lots[0]["id"]
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": lot_id,
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]

    if RELEASE_2020_04_19 > get_now():
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "active")
    else:
        activate_cancellation_after_2020_04_19(self, cancellation["id"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "cancelled")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
    )

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["reason"], "cancellation reason")
