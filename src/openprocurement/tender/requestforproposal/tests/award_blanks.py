from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_date
from openprocurement.tender.requestforproposal.tests.base import test_tender_rfp_claim


def award_sign_not_required(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    request_path = "/tenders/{}/awards".format(self.tender_id)
    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_supplier],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
                "value": {"amount": 500},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]

    self.app.authorization = auth

    # try to make unsuccessful award without signing
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertIn(response.json["data"][-1]["id"], new_award_location)
    new_award = response.json["data"][-1]

    # try to make active award without sign
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def milestone_24h(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    procurement_method_type = response.json["data"]["procurementMethodType"]

    # try upload documents
    context = response.json["data"]["{}s".format(self.context_name)][0]
    bid_id = context.get("bid_id") or context.get("bidID")  # awards and qualifications developed on different days
    winner_token = self.initial_bids_tokens[bid_id]

    # invalid creation
    response = self.app.post_json(
        "/tenders/{}/{}s/{}/milestones".format(self.tender_id, self.context_name, self.context_id),
        {"data": {}},
        status=403,
    )
    self.assertEqual(
        response.json,
        {"status": "error", "errors": [{"location": "url", "name": "permission", "description": "Forbidden"}]},
    )
    response = self.app.post_json(
        "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
            self.tender_id, self.context_name, self.context_id, self.tender_token
        ),
        {"data": {"code": "alp"}},
        status=422,
    )
    if get_now() > RELEASE_2020_04_19:
        milestones_codes = ["24h", "extensionPeriod"] if self.context_name == "award" else ["24h"]
        self.assertEqual(
            response.json,
            {
                "status": "error",
                "errors": [
                    {
                        "location": "body",
                        "name": "code",
                        "description": [f"Value must be one of {milestones_codes}."],
                    }
                ],
            },
        )
    else:
        self.assertEqual(
            response.json,
            {"status": "error", "errors": [{"location": "body", "name": "data", "description": "Forbidden"}]},
        )
        return

    # valid creation
    request_data = {
        "code": "24h",
        "description": "One ring to bring them all and in the darkness bind them",
        "dueDate": (get_now() + timedelta(days=10)).isoformat(),
    }
    response = self.app.post_json(
        "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
            self.tender_id, self.context_name, self.context_id, self.tender_token
        ),
        {"data": request_data},
    )
    self.assertEqual(response.status, "201 Created")
    created_milestone = response.json["data"]

    # get milestone from tender
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]
    context = tender_data["{}s".format(self.context_name)][0]
    public_milestone = context["milestones"][0]

    self.assertEqual(created_milestone, public_milestone)
    self.assertEqual(
        set(created_milestone.keys()),
        {
            "id",
            "date",
            "code",
            "description",
            "dueDate",
        },
    )
    self.assertEqual(created_milestone["code"], request_data["code"])
    self.assertEqual(created_milestone["description"], request_data["description"])
    self.assertEqual(created_milestone["dueDate"], request_data["dueDate"])

    # get milestone by its direct link
    response = self.app.get(
        "/tenders/{}/{}s/{}/milestones/{}".format(
            self.tender_id, self.context_name, self.context_id, created_milestone["id"]
        )
    )
    direct_milestone = response.json["data"]
    self.assertEqual(created_milestone, direct_milestone)

    # can't post another
    response = self.app.post_json(
        "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
            self.tender_id, self.context_name, self.context_id, self.tender_token
        ),
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "description": [{"milestones": ["There can be only one '24h' milestone"]}],
                    "location": "body",
                    "name": "{}s".format(self.context_name),
                }
            ],
        },
    )

    # can't update status of context until dueDate
    if procurement_method_type in ("belowThreshold", "simple.defense", "requestForProposal"):
        activation_data = {"status": "active", "qualified": True}
    else:
        activation_data = {"status": "active", "qualified": True, "eligible": True}
    response = self.app.patch_json(
        "/tenders/{}/{}s/{}?acc_token={}".format(self.tender_id, self.context_name, self.context_id, self.tender_token),
        {"data": activation_data},
        status=403,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "description": (
                        "Can't change status to 'active' " "until milestone.dueDate: {}".format(
                            created_milestone["dueDate"]
                        )
                    ),
                    "location": "body",
                    "name": "data",
                }
            ],
        },
    )

    # try upload documents
    self.assert_upload_docs_status(bid_id, winner_token)

    # wait until milestone dueDate ends
    with patch(
        "openprocurement.tender.core.procedure.state.tender.get_request_now",
        lambda: dt_from_iso(created_milestone["dueDate"]) + timedelta(seconds=1),
    ):
        # self.assert_upload_docs_status(bid_id, winner_token, success=upload_allowed_by_default)

        response = self.app.patch_json(
            "/tenders/{}/{}s/{}?acc_token={}".format(
                self.tender_id, self.context_name, self.context_id, self.tender_token
            ),
            {"data": activation_data},
            status=200,
        )
        self.assertEqual(response.json["data"]["status"], "active")

    # check appending milestone at active qualification status
    # remove milestone to skip "only one" validator
    tender = self.mongodb.tenders.get(self.tender_id)
    context = tender["{}s".format(self.context_name)][0]
    context["milestones"] = []
    self.mongodb.tenders.save(tender)

    response = self.app.post_json(
        "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
            self.tender_id, self.context_name, self.context_id, self.tender_token
        ),
        {"data": request_data},
        status=403,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "description": "Not allowed in current 'active' {} status".format(self.context_name),
                    "location": "body",
                    "name": "data",
                }
            ],
        },
    )


def milestone_24h_dueDate_less_than_24h(self):
    # valid creation
    request_data = {
        "code": "24h",
        "description": "One ring to bring them all and in the darkness bind them",
        "dueDate": (get_now() - timedelta(hours=1)).isoformat(),
    }
    response = self.app.post_json(
        "/tenders/{}/{}s/{}/milestones?acc_token={}".format(
            self.tender_id, self.context_name, self.context_id, self.tender_token
        ),
        {"data": request_data},
    )
    self.assertEqual(response.status, "201 Created")
    created_milestone = response.json["data"]

    # get milestone from tender
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]
    context = tender_data["{}s".format(self.context_name)][0]
    public_milestone = context["milestones"][0]

    self.assertEqual(created_milestone, public_milestone)
    self.assertEqual(
        set(created_milestone.keys()),
        {
            "id",
            "date",
            "code",
            "description",
            "dueDate",
        },
    )
    self.assertEqual(created_milestone["code"], request_data["code"])
    self.assertEqual(created_milestone["description"], request_data["description"])
    self.assertNotEqual(created_milestone["dueDate"], request_data["dueDate"])
    expected_date = calculate_tender_date(
        parse_date(created_milestone["date"]),
        timedelta(hours=24),
        tender=tender_data,
    )
    self.assertEqual(created_milestone["dueDate"], expected_date.isoformat())


def patch_tender_award_unsuccessful_to_cancelled_cancels_subsequent_award_complaints(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_supplier],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
                "value": {"amount": 500},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    award = response.json["data"]
    self.app.authorization = auth

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    # rejecting the first bid generates a new award for the next-ranked bid
    self.assertIn("Location", response.headers)
    next_award_id = response.headers["Location"].split("/")[-1]

    # activate the next-ranked bid's award, creating a pending contract for it
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, next_award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active.awarded")
    self.assertEqual(len(tender["contracts"]), 1)
    self.assertEqual(tender["contracts"][0]["awardID"], next_award_id)
    self.assertEqual(tender["contracts"][0]["status"], "pending")

    # a bidder submits a claim on the active award
    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, next_award_id, bid_token),
        {"data": test_tender_rfp_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")
    complaint_id = response.json["data"]["id"]

    # hasAwardingOrder=True: cancelling the unsuccessful award also cancels the later awards
    # of the same lot together with their complaints
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertIn("Location", response.headers)
    new_award_id = response.headers["Location"].split("/")[-1]

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active.qualification")
    self.assertNotIn("endDate", tender["awardPeriod"])

    awards = tender["awards"]
    self.assertEqual(len(awards), 3)
    self.assertEqual(awards[0]["id"], award["id"])
    self.assertEqual(awards[0]["status"], "cancelled")
    self.assertEqual(awards[1]["id"], next_award_id)
    self.assertEqual(awards[1]["status"], "cancelled")
    self.assertEqual(len(awards[1]["complaints"]), 1)
    self.assertEqual(awards[1]["complaints"][0]["id"], complaint_id)
    self.assertEqual(awards[1]["complaints"][0]["status"], "cancelled")
    self.assertEqual(awards[1]["complaints"][0]["cancellationReason"], "cancelled")
    self.assertIn("dateCanceled", awards[1]["complaints"][0])
    # qualification restarts from the first-ranked bid
    self.assertEqual(awards[2]["id"], new_award_id)
    self.assertEqual(awards[2]["status"], "pending")
    self.assertEqual(awards[2]["bid_id"], self.initial_bids[0]["id"])

    self.assertEqual(len(tender["contracts"]), 1)
    self.assertEqual(tender["contracts"][0]["awardID"], next_award_id)
    self.assertEqual(tender["contracts"][0]["status"], "cancelled")


def patch_tender_award_unsuccessful_to_cancelled_cancels_subsequent_lot_awards(self):
    # the auction results generated a pending award for the first-ranked bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    awards = response.json["data"]
    self.assertEqual(len(awards), 1)
    self.assertEqual(awards[0]["status"], "pending")
    first_award = awards[0]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, first_award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertIn("Location", response.headers)
    second_award_id = response.headers["Location"].split("/")[-1]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, second_award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertIn("Location", response.headers)
    third_award_id = response.headers["Location"].split("/")[-1]

    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, second_award_id))
    second_award = response.json["data"]

    # hasAwardingOrder=True: cancelling the second award cancels only the awards after it
    # in the same lot; the first (unsuccessful) award stays untouched
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, second_award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertIn("Location", response.headers)
    new_award_id = response.headers["Location"].split("/")[-1]

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active.qualification")

    awards = tender["awards"]
    self.assertEqual(len(awards), 4)
    self.assertEqual(awards[0]["id"], first_award["id"])
    self.assertEqual(awards[0]["status"], "unsuccessful")
    self.assertEqual(awards[1]["id"], second_award_id)
    self.assertEqual(awards[1]["status"], "cancelled")
    self.assertEqual(awards[2]["id"], third_award_id)
    self.assertEqual(awards[2]["status"], "cancelled")
    # qualification continues from the cancelled award's bid, the first-ranked one still eligible
    self.assertEqual(awards[3]["id"], new_award_id)
    self.assertEqual(awards[3]["status"], "pending")
    self.assertEqual(awards[3]["bid_id"], second_award["bid_id"])


def patch_tender_award_unsuccessful_to_cancelled_keeps_other_lot_awards(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_supplier],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
                "value": {"amount": 500},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    award = response.json["data"]
    self.app.authorization = auth

    # rejecting the first bid generates the next award of the first lot
    # and the first award of the second lot
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    awards = response.json["data"]
    self.assertEqual(len(awards), 3)
    self.assertEqual(awards[0]["id"], award["id"])
    self.assertEqual(awards[0]["status"], "unsuccessful")
    self.assertEqual(awards[1]["lotID"], self.initial_lots[0]["id"])
    self.assertEqual(awards[1]["status"], "pending")
    self.assertEqual(awards[2]["lotID"], self.initial_lots[1]["id"])
    self.assertEqual(awards[2]["status"], "pending")
    next_award_id = awards[1]["id"]
    other_lot_award_id = awards[2]["id"]

    # hasAwardingOrder=True: only the later awards of the same lot are cancelled,
    # the other lot's award placed after the current one stays pending
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertIn("Location", response.headers)
    new_award_id = response.headers["Location"].split("/")[-1]

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active.qualification")

    awards = tender["awards"]
    self.assertEqual(len(awards), 4)
    self.assertEqual(awards[0]["id"], award["id"])
    self.assertEqual(awards[0]["status"], "cancelled")
    self.assertEqual(awards[1]["id"], next_award_id)
    self.assertEqual(awards[1]["status"], "cancelled")
    self.assertEqual(awards[2]["id"], other_lot_award_id)
    self.assertEqual(awards[2]["status"], "pending")
    # qualification of the first lot restarts from the first-ranked bid
    self.assertEqual(awards[3]["id"], new_award_id)
    self.assertEqual(awards[3]["lotID"], self.initial_lots[0]["id"])
    self.assertEqual(awards[3]["status"], "pending")
    self.assertEqual(awards[3]["bid_id"], self.initial_bids[0]["id"])
