from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_date


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
        "openprocurement.tender.core.procedure.validation.get_request_now",
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
