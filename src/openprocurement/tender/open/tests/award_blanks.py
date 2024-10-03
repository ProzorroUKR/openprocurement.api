from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

import dateutil

from openprocurement.api.constants import (
    COMPLAINT_IDENTIFIER_REQUIRED_FROM,
    RELEASE_2020_04_19,
    SANDBOX_MODE,
)
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_cancellation,
    test_tender_below_claim,
    test_tender_below_complaint,
    test_tender_below_draft_claim,
    test_tender_below_draft_complaint,
    test_tender_below_organization,
)
from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneCodes,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.tender.open.constants import STAND_STILL_TIME


def create_tender_award(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]
    self.assertEqual(award["suppliers"][0]["name"], test_tender_below_organization["name"])
    self.assertIn("id", award)
    self.assertIn(award["id"], response.headers["Location"])

    self.app.authorization = auth

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][-1], award)

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertIn("Location", response.headers)


def create_tender_award_invalid(self):
    self.app.authorization = ("Basic", ("token", ""))
    request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
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

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"suppliers": [{"identifier": "invalid_value"}]}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "identifier": ["Please use a mapping for this field or Identifier instance instead of str."]
                },
                "location": "body",
                "name": "suppliers",
            }
        ],
    )

    response = self.app.post_json(request_path, {"data": {"suppliers": [{"identifier": {"id": 0}}]}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    {
                        "contactPoint": ["This field is required."],
                        "identifier": {"scheme": ["This field is required."]},
                        "name": ["This field is required."],
                        "address": ["This field is required."],
                        "scale": ["This field is required."],
                    }
                ],
                "location": "body",
                "name": "suppliers",
            },
            {"description": ["This field is required."], "location": "body", "name": "bid_id"},
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"suppliers": [{"name": "name", "identifier": {"uri": "invalid_value"}}]}}, status=422
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
                        "contactPoint": ["This field is required."],
                        "identifier": {
                            "scheme": ["This field is required."],
                            "id": ["This field is required."],
                            "uri": ["Not a well formed URL."],
                        },
                        "address": ["This field is required."],
                        "scale": ["This field is required."],
                    }
                ],
                "location": "body",
                "name": "suppliers",
            },
            {"description": ["This field is required."], "location": "body", "name": "bid_id"},
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": "0" * 32,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["lotID should be one of lots"], "location": "body", "name": "lotID"}],
    )

    response = self.app.post_json(
        "/tenders/some_id/awards",
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/some_id/awards", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't create award in current (complete) tender status"
    )


def create_tender_award_no_scale_invalid(self):
    self.app.authorization = ("Basic", ("token", ""))
    award_data = {
        "data": {
            "status": "pending",
            "suppliers": [{key: value for key, value in test_tender_below_organization.items() if key != "scale"}],
            "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
        }
    }
    if self.initial_bids:
        award_data["data"]["bid_id"] = self.initial_bids[0]["id"]
    response = self.app.post_json("/tenders/{}/awards".format(self.tender_id), award_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "suppliers", "description": [{"scale": ["This field is required."]}]}],
    )


def patch_tender_award(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
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
    response = self.app.patch_json(
        "/tenders/{}/awards/some_id".format(self.tender_id), {"data": {"status": "unsuccessful"}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}])

    response = self.app.patch_json("/tenders/some_id/awards/some_id", {"data": {"status": "unsuccessful"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"awardStatus": "unsuccessful"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "awardStatus", "description": "Rogue field"}]
    )

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update award in current (unsuccessful) status")

    request_path = "/tenders/{}/awards".format(self.tender_id)
    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertIn(response.json["data"][1]["id"], new_award_location)
    new_award = response.json["data"][-1]
    old_date = new_award["date"]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(old_date, response.json["data"]["date"])
    old_date = response.json["data"]["date"]

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertNotEqual(old_date, response.json["data"]["date"])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)

    self.set_status("complete")

    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 500)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update award in current (complete) tender status"
    )


def check_tender_award_complaint_period_dates(self):
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)

    updated_award = response.json["data"]
    self.assertIn("endDate", updated_award["complaintPeriod"])
    new_complaint_period_start_date = dateutil.parser.parse(updated_award["complaintPeriod"]["startDate"])
    new_complaint_period_end_date = dateutil.parser.parse(updated_award["complaintPeriod"]["endDate"])

    self.assertGreater(new_complaint_period_start_date, self.old_complaint_period_start_date)
    self.assertGreater(new_complaint_period_end_date, new_complaint_period_start_date)


def patch_tender_award_active(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
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
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split("/")[-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        new_award_location[-81:] + "/complaints?acc_token={}".format(bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]
    now = get_now()
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                new_award_location[-81:] + "/complaints/{}".format(complaint_id),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ("Basic", ("reviewer", ""))
    data = {"status": "accepted"}
    if RELEASE_2020_04_19 < now:
        data.update(
            {
                "reviewDate": now.isoformat(),
                "reviewPlace": "some",
            }
        )

    response = self.app.patch_json(
        new_award_location[-81:] + "/complaints/{}".format(complaint_id),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "accepted")
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["reviewPlace"], "some")
        self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        new_award_location[-81:] + "/complaints/{}".format(response.json["data"]["id"]),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.patch_json(new_award_location[-81:], {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]
    self.app.authorization = ("Basic", ("broker", ""))
    new_award_id = new_award_location.split('/')[-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)


def patch_tender_award_unsuccessful(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
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
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split("/")[-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award["id"], bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]

    now = get_now()
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award["id"], complaint_id),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ("Basic", ("reviewer", ""))
    data = {"status": "accepted"}
    if RELEASE_2020_04_19 < now:
        data.update(
            {
                "reviewDate": now.isoformat(),
                "reviewPlace": "some",
            }
        )
    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award["id"], complaint_id),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["reviewPlace"], "some")
        self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award["id"], complaint_id),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "{}/complaints".format(new_award_location[-81:]),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award["id"]), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    self.app.authorization = ("Basic", ("broker", ""))
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split('/')[-1]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")

    response = self.app.patch_json(
        f"{new_award_location[-81:]}?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split('/')[-1]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")

    response = self.app.patch_json(
        f"{new_award_location[-81:]}?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 4)


def award_has_satisfied_complaint(self):
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "accepted", "reviewDate": get_now().isoformat(), "reviewPlace": "Place of review"}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "satisfied"}},
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.json["data"]["status"], 'cancelled')
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint["id"], self.tender_token
        ),
        {'data': {"tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно", "status": "resolved"}},
    )
    self.assertEqual(response.status, '200 OK')


def award_has_resolved_complaint(self):
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
            {"data": {"status": "pending"}},
        )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "accepted", "reviewDate": get_now().isoformat(), "reviewPlace": "Place of review"}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "satisfied"}},
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint["id"], self.tender_token
        ),
        {'data': {"tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно", "status": "resolved"}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.json["data"]["status"], 'cancelled')


def any_award_has_not_considered_complaint(self):
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
            {"data": {"status": "pending"}},
        )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(response.json["errors"][0]["description"], "Can't update award in current (unsuccessful) status")

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "accepted", "reviewDate": get_now().isoformat(), "reviewPlace": "Place of review"}},
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(response.json["errors"][0]["description"], "Can't update award with accepted complaint")


def another_award_has_considered_complaint(self):
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    response = self.app.get(
        '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
    )
    award_2_id = response.json["data"][-1]["id"]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_2_id}/documents")
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_2_id, bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award_2_id, complaint["id"]),
            {"data": {"status": "pending"}},
        )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_2_id, complaint["id"]),
        {'data': {"status": "accepted", "reviewDate": get_now().isoformat(), "reviewPlace": "Place of review"}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_2_id, complaint["id"]),
        {'data': {"status": "satisfied"}},
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, award_2_id, complaint["id"], self.tender_token
        ),
        {'data': {"tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно", "status": "resolved"}},
    )
    self.assertEqual(response.status, '200 OK')

    # try to cancel first award when second award has complaint
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.json["data"]["status"], 'cancelled')


def patch_tender_award_unsuccessful_complaint_first(self):
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    award1 = response.json["data"]
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split("/")[-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    award2 = response.json["data"]
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split("/")[-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    award3 = response.json["data"]

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)

    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 1)
    contract = response.json["data"][0]
    self.assertEqual(contract["status"], "pending")

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award1["id"], bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]

    now = get_now()

    self.app.authorization = ("Basic", ("reviewer", ""))
    data = {
        "status": "accepted",
        "reviewDate": now.isoformat(),
        "reviewPlace": "some",
    }

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award1["id"], complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award1["id"], complaint_id),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["reviewPlace"], "some")
    self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award1["id"], complaint_id),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award1["id"]), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    # self.assertIn("Location", response.headers)
    # new_award_location = response.headers["Location"]

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 4)

    self.assertEqual(response.json["data"][0]["status"], "cancelled")
    self.assertEqual(response.json["data"][1]["status"], "unsuccessful")
    self.assertEqual(response.json["data"][2]["status"], "cancelled")
    self.assertEqual(response.json["data"][3]["status"], "pending")
    self.assertEqual(response.json["data"][0]["bid_id"], response.json["data"][3]["bid_id"])


def patch_tender_award_unsuccessful_complaint_second(self):
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    award1 = response.json["data"]
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split("/")[-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    award2 = response.json["data"]
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split("/")[-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    award3 = response.json["data"]

    # import pdb; pdb.set_trace()

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)

    bid2_token = self.initial_bids_tokens[self.initial_bids[1]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award2["id"], bid2_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]

    now = get_now()

    self.app.authorization = ("Basic", ("reviewer", ""))
    data = {
        "status": "accepted",
        "reviewDate": now.isoformat(),
        "reviewPlace": "some",
    }

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award2["id"], complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award2["id"], complaint_id),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["reviewPlace"], "some")
    self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award2["id"], complaint_id),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award2["id"]), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 4)

    self.assertEqual(response.json["data"][0]["status"], "unsuccessful")
    self.assertEqual(response.json["data"][1]["status"], "cancelled")
    self.assertEqual(response.json["data"][2]["status"], "cancelled")
    self.assertEqual(response.json["data"][3]["status"], "pending")
    self.assertEqual(response.json["data"][1]["bid_id"], response.json["data"][3]["bid_id"])


def patch_tender_award_unsuccessful_complaint_third(self):
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    award1 = response.json["data"]
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split("/")[-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    award2 = response.json["data"]
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split("/")[-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    award3 = response.json["data"]

    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 1)
    contract = response.json["data"][0]
    self.assertEqual(contract["status"], "pending")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)

    bid1_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    bid2_token = self.initial_bids_tokens[self.initial_bids[1]["id"]]

    # Complaint award 1
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award1["id"], bid1_token),
        {"data": test_tender_below_complaint},
    )

    # Complaint award 2
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award2["id"], bid2_token),
        {"data": test_tender_below_complaint},
    )

    # Complaint award 3

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award3["id"], bid2_token),
        {"data": test_tender_below_complaint},
    )

    self.assertEqual(response.status, "201 Created")
    complaint3_id = response.json["data"]["id"]

    now = get_now()

    self.app.authorization = ("Basic", ("reviewer", ""))
    data = {
        "status": "accepted",
        "reviewDate": now.isoformat(),
        "reviewPlace": "some",
    }

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award3["id"], complaint3_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award3["id"], complaint3_id),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["reviewPlace"], "some")
    self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award3["id"], complaint3_id),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award3["id"]), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 4)

    self.assertEqual(response.json["data"][0]["status"], "unsuccessful")
    self.assertEqual(response.json["data"][1]["status"], "unsuccessful")
    self.assertEqual(response.json["data"][2]["status"], "cancelled")
    self.assertEqual(response.json["data"][3]["status"], "pending")
    self.assertEqual(response.json["data"][2]["bid_id"], response.json["data"][3]["bid_id"])


def patch_tender_award_unsuccessful_complaint_second_complainnt_third(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
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
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    award1 = response.json["data"]
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    award2 = response.json["data"]
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    award3 = response.json["data"]

    # import pdb; pdb.set_trace()

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award2["id"], bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]

    now = get_now()

    self.app.authorization = ("Basic", ("reviewer", ""))
    data = {
        "status": "accepted",
        "reviewDate": now.isoformat(),
        "reviewPlace": "some",
    }

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award2["id"], complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award2["id"], complaint_id),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["reviewPlace"], "some")
    self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award2["id"], complaint_id),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award2["id"]), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 4)

    self.assertEqual(response.json["data"][0]["status"], "unsuccessful")
    self.assertEqual(response.json["data"][1]["status"], "cancelled")
    self.assertEqual(response.json["data"][2]["status"], "cancelled")
    self.assertEqual(response.json["data"][3]["status"], "pending")
    self.assertEqual(response.json["data"][1]["bid_id"], response.json["data"][3]["bid_id"])


def create_tender_lots_unsuccessful_award_complaint_check_bidders(self):
    bid1_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    bid2_token = self.initial_bids_tokens[self.initial_bids[1]["id"]]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    # try to add complaint by another bidder to unsuccessful award
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={bid2_token}",
        {"data": test_tender_below_complaint},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can add complaint only on unsuccessful award of your bid",
                "location": "body",
                "name": "bid_id",
            }
        ],
    )

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={bid1_token}",
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def last_award_unsuccessful_next_check(self):
    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "lotID": self.initial_lots[0]["id"],
                    "value": {"amount": 500},
                }
            },
        )
    award = response.json["data"]

    self.check_chronograph()  # deletes next_check

    # disqualify all
    award_location = "/tenders/{}/awards/{}".format(self.tender_id, award["id"])
    for _ in range(4):
        award_id = award_location.split("/")[-1]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
        response = self.app.patch_json(
            f"{award_location}?acc_token={self.tender_token}",
            {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        )
        award = response.json["data"]
        if "Location" not in response.headers:
            break
        award_location = response.headers["Location"][-81:]

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(['unsuccessful', 'unsuccessful'], [a["status"] for a in response.json["data"]])

    # next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual("active.awarded", tender["status"])
    self.assertIn("next_check", tender)

    response = self.app.get("/tenders?opt_fields=next_check")
    tender = response.json["data"][0]
    self.assertEqual(self.tender_id, tender["id"])
    self.assertIn("next_check", tender)
    self.assertEqual(tender["next_check"], award["complaintPeriod"]["endDate"])


def get_tender_award(self):
    auth = self.app.authorization

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]
    self.app.authorization = auth

    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    award_data = response.json["data"]
    self.assertEqual(award_data, award)

    response = self.app.get("/tenders/{}/awards/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}])

    response = self.app.get("/tenders/some_id/awards/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


def check_tender_award_complaint_period_dates(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    request_path = "/tenders/{}/awards".format(self.tender_id)
    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_organization],
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

    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_award = response.json["data"]
    self.assertIn("complaintPeriod", updated_award)
    self.assertIn("startDate", updated_award["complaintPeriod"])
    self.assertIn("endDate", updated_award["complaintPeriod"])


def create_tender_lot_award(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "lotID", "description": ["This field is required."]}]
    )

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]
    self.assertEqual(award["suppliers"][0]["name"], test_tender_below_organization["name"])
    self.assertEqual(award["lotID"], self.initial_lots[0]["id"])
    self.assertIn("id", award)
    self.assertIn(award["id"], response.headers["Location"])

    self.app.authorization = auth
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][-1], award)

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertIn("Location", response.headers)


def patch_tender_lot_award(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
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
    response = self.app.patch_json(
        "/tenders/{}/awards/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}])

    response = self.app.patch_json("/tenders/some_id/awards/some_id", {"data": {"status": "unsuccessful"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"awardStatus": "unsuccessful"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "awardStatus", "description": "Rogue field"}]
    )

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {
            "data": {
                "title": "title",
                "description": "description",
                "status": "unsuccessful",
                "qualified": False,
                "eligible": False,
            }
        },
    )

    self.assertEqual(response.json["data"]["title"], "title")
    self.assertEqual(response.json["data"]["description"], "description")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update award in current (unsuccessful) status")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertIn(response.json["data"][-1]["id"], new_award_location)
    new_award = response.json["data"][-1]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "active", "eligible": True}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "qualified",
                "description": ["Can't update award to active status with not qualified"],
            }
        ],
    )
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"title": "title", "description": "description", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["qualified"], True)
    self.assertEqual(response.json["data"]["eligible"], True)
    self.assertEqual(response.json["data"]["title"], "title")
    self.assertEqual(response.json["data"]["description"], "description")

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)

    self.set_status("complete")

    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 500)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update award in current (complete) tender status"
    )


def patch_tender_lot_award_unsuccessful(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
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
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split('/')[-1]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")

    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award["id"], bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]

    now = get_now()
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award["id"], complaint_id),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ("Basic", ("reviewer", ""))
    now = get_now()
    data = {"status": "accepted"}
    if RELEASE_2020_04_19 < now:
        data.update(
            {
                "reviewDate": now.isoformat(),
                "reviewPlace": "some",
            }
        )
    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award["id"], complaint_id),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "accepted")
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["reviewPlace"], "some")
        self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award["id"], complaint_id),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "{}/complaints".format(new_award_location[-81:]),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award["id"]), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split('/')[-1]
    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")

    response = self.app.patch_json(
        new_award_location[-81:] + f"?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]
    new_award_id = new_award_location.split('/')[-1]
    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")

    response = self.app.patch_json(
        new_award_location[-81:] + f"?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 4)


def create_tender_lots_award(self):
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
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can create award only in active lot status")

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[1]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]
    self.assertEqual(award["suppliers"][0]["name"], test_tender_below_organization["name"])
    self.assertEqual(award["lotID"], self.initial_lots[1]["id"])
    self.assertIn("id", award)
    self.assertIn(award["id"], response.headers["Location"])

    self.app.authorization = auth
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][-1], award)

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertIn("Location", response.headers)


def patch_tender_lots_award(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
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
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)
    new_award = response.json["data"][-1]

    if RELEASE_2020_04_19:
        self.set_all_awards_complaint_period_end()

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
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update award only in active lot status")


def create_tender_award_claim(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, self.award_id), {"data": {"status": "cancelled"}}
    )

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][-1]
    bid_token = self.initial_bids_tokens[self.initial_bids[1]["id"]]

    self.app.authorization = auth
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_id, bid_token),
        {"data": test_tender_below_claim},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can add complaint only in complaintPeriod",
                "location": "body",
                "name": "data",
            }
        ],
    )

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("broker", ""))

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.app.authorization = auth

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_id, bid_token),
        {"data": test_tender_below_claim},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can add claim only on unsuccessful award of your bid",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_id, bid_token),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can add claim only on unsuccessful award of your bid",
                "location": "body",
                "name": "data",
            }
        ],
    )


def create_tender_award_complaint_not_active(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, self.award_id), {"data": {"status": "cancelled"}}
    )
    self.app.authorization = auth

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][-1]

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_id, self.bid_token),
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can add complaint only in complaintPeriod",
                "location": "body",
                "name": "data",
            }
        ],
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_tender_award_complaint_after_2020_04_19(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, self.award_id), {"data": {"status": "cancelled"}}
    )
    self.app.authorization = auth

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][-1]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_id, self.bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(self.tender_id, award_id, complaint_id, owner_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update complaint from draft to pending status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award_id, complaint_id),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")


def create_tender_award_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    self.assertEqual(complaint["author"]["name"], test_tender_below_author["name"])
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])

    complaint_data = deepcopy(test_tender_below_draft_complaint)
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": complaint_data},
        status=201,
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    self.assertEqual(complaint["status"], "draft")

    if get_now() > COMPLAINT_IDENTIFIER_REQUIRED_FROM:
        test_draft_complaint_invalid = deepcopy(test_tender_below_draft_complaint)
        test_draft_complaint_invalid["author"]["identifier"]["legalName"] = ""
        test_draft_complaint_invalid["author"]["identifier"]["id"] = ""
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": test_draft_complaint_invalid},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": {
                        "identifier": {
                            "id": ["This field is required."],
                            "legalName": ["This field is required."],
                        },
                    },
                    "location": "body",
                    "name": "author",
                }
            ],
        )

    self.set_status("active.awarded")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (unsuccessful) tender status"
    )


def patch_tender_award_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=200,
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "cancelled")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")
    else:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from draft to cancelled status"
        )

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], self.tender_token
        ),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"title": "claim title"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "claim title")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual(response.json["errors"][0]["description"], "Can't update complaint from draft to claim status")

    if get_now() > COMPLAINT_IDENTIFIER_REQUIRED_FROM:
        denied_patch_fields = {
            "id": "new_id",
            "scheme": "AE-ACCI",
            "legalName": "new_legal_name",
        }
        author = deepcopy(complaint["author"])
        author["identifier"] = denied_patch_fields

        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {
                "data": {
                    "author": author,
                    "title": "new_title",
                },
            },
            status=403,
        )
        self.assertEqual(
            response.json["errors"],
            [{"location": "body", "name": "data", "description": "Can\'t change complaint author id"}],
        )

    if get_now() > RELEASE_2020_04_19:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )
    else:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/some_id/awards/some_id/complaints/some_id",
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.patch_json(
        "/tenders/{}/awards/some_id/complaints/some_id".format(self.tender_id),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/some_id".format(self.tender_id, self.award_id),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}])

    if RELEASE_2020_04_19 > get_now():
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")

        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from stopping to cancelled status"
        )

        response = self.app.get(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"])
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")
    else:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
            status=403,
        )

        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from pending to stopping status"
        )

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    self.set_status("complete")

    if get_now() > RELEASE_2020_04_19:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
                status=403,
            )
    else:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint in current (complete) tender status"
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def bot_patch_tender_award_complaint(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(
            self.tender_id, self.award_id, list(self.initial_bids_tokens.values())[0]
        ),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def bot_patch_tender_award_complaint_forbidden(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(
            self.tender_id, self.award_id, list(self.initial_bids_tokens.values())[0]
        ),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from draft to pending status"
        )


def review_tender_award_complaint(self):
    for status in ["invalid", "stopped", "declined", "satisfied"]:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": test_tender_below_complaint},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        complaint = response.json["data"]
        now = get_now()

        if RELEASE_2020_04_19 < now:
            self.assertEqual(response.json["data"]["status"], "draft")
            owner_token = response.json["access"]["token"]

            with change_auth(self.app, ("Basic", ("bot", ""))):
                response = self.app.patch_json(
                    "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                    {"data": {"status": "pending"}},
                )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "pending")

        self.app.authorization = ("Basic", ("reviewer", ""))
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
            {"data": {"decision": "{} complaint".format(status), "rejectReasonDescription": "reject reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["decision"], "{} complaint".format(status))
        self.assertEqual(response.json["data"]["rejectReasonDescription"], "reject reason")

        if status in ["declined", "satisfied", "stopped"]:
            data = {"status": "accepted"}
            if RELEASE_2020_04_19 < now:
                data.update(
                    {
                        "reviewDate": now.isoformat(),
                        "reviewPlace": "some",
                    }
                )
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": data},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "accepted")
            if RELEASE_2020_04_19 < now:
                self.assertEqual(response.json["data"]["reviewPlace"], "some")
                self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

            now = get_now()
            data = {"decision": "accepted:{} complaint".format(status)}
            if RELEASE_2020_04_19 > now:
                data.update(
                    {
                        "reviewDate": now.isoformat(),
                        "reviewPlace": "some",
                    }
                )
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": data},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["decision"], "accepted:{} complaint".format(status))
            if RELEASE_2020_04_19 > now:
                self.assertEqual(response.json["data"]["reviewPlace"], "some")
                self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

            self.app.authorization = ("Basic", ("token", ""))
            response = self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["errors"][0]["description"], "Can't update award with accepted complaint")

        self.app.authorization = ("Basic", ("reviewer", ""))
        now = get_now()
        data = {"status": status}
        if RELEASE_2020_04_19 < now:
            if status in ["invalid", "stopped"]:
                data.update({"rejectReason": "tenderCancelled", "rejectReasonDescription": "reject reason description"})
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
            {"data": data},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], status)


def review_tender_award_stopping_complaint(self):
    if RELEASE_2020_04_19 > get_now():
        for status in ["stopped", "declined", "mistaken", "invalid", "satisfied"]:
            self.app.authorization = ("Basic", ("broker", ""))
            response = self.app.post_json(
                "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
                {"data": test_tender_below_complaint},
            )
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.content_type, "application/json")
            complaint = response.json["data"]
            owner_token = response.json["access"]["token"]

            url_patch_complaint = "/tenders/{}/awards/{}/complaints/{}".format(
                self.tender_id, self.award_id, complaint["id"]
            )

            response = self.app.patch_json(
                "{}?acc_token={}".format(url_patch_complaint, owner_token),
                {"data": {"status": "stopping", "cancellationReason": "reason"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "stopping")
            self.assertEqual(response.json["data"]["cancellationReason"], "reason")

            self.app.authorization = ("Basic", ("reviewer", ""))
            data = {"decision": "decision", "status": status}
            if status in ["invalid", "stopped"]:
                data.update({"rejectReason": "tenderCancelled", "rejectReasonDescription": "reject reason description"})
            response = self.app.patch_json(url_patch_complaint, {"data": data})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], status)
            self.assertEqual(response.json["data"]["decision"], "decision")

        # This test exist in patch_tender_complaint method


def review_tender_award_claim(self):
    for status in ["invalid", "resolved", "declined"]:
        # self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={self.bid_token}",
            {"data": test_tender_below_claim},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        complaint = response.json["data"]
        complaint_token = response.json["access"]["token"]

        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], self.tender_token
            ),
            {
                "data": {
                    "status": "answered",
                    "resolutionType": status,
                    "resolution": "resolution text for {} status".format(status),
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["resolutionType"], status)

        # self.app.authorization = ("Basic", ("token", ""))
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], complaint_token
            ),
            {"data": {"satisfied": "i" in status}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["satisfied"], "i" in status)


def create_tender_lot_award_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    self.assertEqual(complaint["author"]["name"], test_tender_below_organization["name"])
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])

    self.set_status("active.awarded")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (unsuccessful) tender status"
    )


def patch_tender_lot_award_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/some_id/awards/some_id/complaints/some_id",
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.patch_json(
        "/tenders/{}/awards/some_id/complaints/some_id?acc_token={}".format(self.tender_id, owner_token),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/some_id?acc_token={}".format(self.tender_id, self.award_id, owner_token),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}])

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")

        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from stopping to cancelled status"
        )

        response = self.app.get(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"])
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")
    else:
        pass
        # This test exist in in patch_tender_award_complaint method

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    self.set_status("complete")

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
            status=403,
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
                status=403,
            )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint in current (complete) tender status"
    )


def create_tender_lots_award_complaint(self):
    now = get_now()
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(
            self.tender_id, self.award_id, self.initial_bids_tokens[self.initial_bids[0]["id"]]
        ),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertEqual(complaint["author"]["name"], test_tender_below_organization["name"])
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])

    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    self.set_status("active.awarded")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    if RELEASE_2020_04_19:
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
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < now:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(
            self.tender_id, self.award_id, self.initial_bids_tokens[self.initial_bids[0]["id"]]
        ),
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add complaint only in active lot status")


def patch_tender_lots_award_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(
            self.tender_id, self.award_id, self.initial_bids_tokens[self.initial_bids[0]["id"]]
        ),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if RELEASE_2020_04_19 < get_now():
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
            status=403,
        )
        self.assertEqual(
            response.json,
            {
                "status": "error",
                "errors": [
                    {
                        "location": "body",
                        "name": "data",
                        "description": "Can't update complaint from draft to pending status",
                    }
                ],
            },
        )

    else:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
            status=200,
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(
            self.tender_id, self.award_id, self.initial_bids_tokens[self.initial_bids[0]["id"]]
        ),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if RELEASE_2020_04_19:
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
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update complaint only in active lot status")


def lot_award_has_satisfied_complaint(self):
    patch_data = {"status": "unsuccessful", "qualified": False}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = False
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": patch_data},
    )

    if "defense" in self.initial_data["procurementMethodType"]:
        self.assertNotIn("complaintPeriod", response.json["data"])

        # activate second award to have complaintPeriod in unsuccessful award
        response = self.app.get(
            '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        )
        self.assertEqual(response.json["data"][1]["lotID"], response.json["data"][0]["lotID"])
        award_2_id = response.json["data"][1]["id"]
        patch_data = {"status": "active", "qualified": True}
        if self.initial_data['procurementMethodType'] != "simple.defense":
            patch_data["eligible"] = True
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_2_id, self.tender_token),
            {"data": patch_data},
        )

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "accepted", "reviewDate": get_now().isoformat(), "reviewPlace": "Place of review"}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "satisfied"}},
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.json["data"]["status"], 'cancelled')
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint["id"], self.tender_token
        ),
        {'data': {"tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно", "status": "resolved"}},
    )
    self.assertEqual(response.status, '200 OK')


def lot_award_has_resolved_complaint(self):
    patch_data = {"status": "unsuccessful", "qualified": False}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = False
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": patch_data},
    )

    if "defense" in self.initial_data["procurementMethodType"]:
        self.assertNotIn("complaintPeriod", response.json["data"])

        # activate second award to have complaintPeriod in unsuccessful award
        response = self.app.get(
            '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        )
        self.assertEqual(response.json["data"][1]["lotID"], response.json["data"][0]["lotID"])
        award_2_id = response.json["data"][1]["id"]
        patch_data = {"status": "active", "qualified": True}
        if self.initial_data['procurementMethodType'] != "simple.defense":
            patch_data["eligible"] = True
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_2_id, self.tender_token),
            {"data": patch_data},
        )

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
            {"data": {"status": "pending"}},
        )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "accepted", "reviewDate": get_now().isoformat(), "reviewPlace": "Place of review"}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "satisfied"}},
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint["id"], self.tender_token
        ),
        {'data': {"tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно", "status": "resolved"}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.json["data"]["status"], 'cancelled')


def any_lot_award_has_not_considered_complaint(self):
    patch_data = {"status": "unsuccessful", "qualified": False}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = False
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": patch_data},
    )

    if "defense" in self.initial_data["procurementMethodType"]:
        self.assertNotIn("complaintPeriod", response.json["data"])

        # activate second award to have complaintPeriod in unsuccessful award
        response = self.app.get(
            '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        )
        self.assertEqual(response.json["data"][1]["lotID"], response.json["data"][0]["lotID"])
        award_2_id = response.json["data"][1]["id"]
        patch_data = {"status": "active", "qualified": True}
        if self.initial_data['procurementMethodType'] != "simple.defense":
            patch_data["eligible"] = True
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_2_id, self.tender_token),
            {"data": patch_data},
        )

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
            {"data": {"status": "pending"}},
        )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(response.json["errors"][0]["description"], "Can't update award in current (unsuccessful) status")

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint["id"]),
        {'data': {"status": "accepted", "reviewDate": get_now().isoformat(), "reviewPlace": "Place of review"}},
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(response.json["errors"][0]["description"], "Can't update award with accepted complaint")


def another_award_for_one_lot_has_considered_complaint(self):
    patch_data = {"status": "unsuccessful", "qualified": False}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = False
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": patch_data},
    )
    response = self.app.get(
        '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
    )
    self.assertEqual(response.json["data"][1]["lotID"], response.json["data"][0]["lotID"])
    award_2_id = response.json["data"][1]["id"]
    patch_data = {"status": "active", "qualified": True}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = True
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_2_id, self.tender_token),
        {"data": patch_data},
    )
    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_2_id, bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award_2_id, complaint["id"]),
            {"data": {"status": "pending"}},
        )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_2_id, complaint["id"]),
        {'data': {"status": "accepted", "reviewDate": get_now().isoformat(), "reviewPlace": "Place of review"}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_2_id, complaint["id"]),
        {'data': {"status": "satisfied"}},
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, award_2_id, complaint["id"], self.tender_token
        ),
        {'data': {"tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно", "status": "resolved"}},
    )
    self.assertEqual(response.status, '200 OK')

    # try to cancel first award when second award has complaint
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.json["data"]["status"], 'cancelled')


def award_for_another_lot_has_considered_complaint(self):
    patch_data = {"status": "unsuccessful", "qualified": False}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = False
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": patch_data},
    )
    response = self.app.get(
        '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
    )
    self.assertNotEqual(response.json["data"][-1]["lotID"], response.json["data"][0]["lotID"])
    award_3_id = response.json["data"][-1]["id"]
    patch_data = {"status": "active", "qualified": True}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = True
    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_3_id, self.tender_token),
        {"data": patch_data},
    )
    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_3_id, bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, award_3_id, complaint["id"]),
            {"data": {"status": "pending"}},
        )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_3_id, complaint["id"]),
        {'data': {"status": "accepted", "reviewDate": get_now().isoformat(), "reviewPlace": "Place of review"}},
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_3_id, complaint["id"]),
        {'data': {"status": "satisfied"}},
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(response.json["errors"][0]["description"], "Can't update award in current (unsuccessful) status")


def patch_tender_award_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
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
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, self.complaint_id),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
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
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )


def put_tender_lots_award_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
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
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
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
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
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
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, self.complaint_id),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
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
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    # set complaint status invalid to be able to cancel the lot-
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    if RELEASE_2020_04_19:
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
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only in active lot status")


def patch_tender_lots_award_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
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
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, self.complaint_id),
                {"data": {"status": "pending"}},
            )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description2"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["description"], "document description2")

    # set complaint status invalid to be able to cancel the lot-
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    if RELEASE_2020_04_19:
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
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only in active lot status")


def tender_award_complaint_period(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
                "value": {"amount": 500},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award_id = response.json["data"]["id"]

    self.app.authorization = auth
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]

    start = parse_date(award["complaintPeriod"]["startDate"])
    end = parse_date(award["complaintPeriod"]["endDate"])
    delta = end - start
    self.assertEqual(delta.days, 0 if SANDBOX_MODE else STAND_STILL_TIME.days)


def create_award_requirement_response(self):
    base_request_path = "/tenders/{}/awards/{}/requirement_responses".format(self.tender_id, self.award_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    valid_data = [
        {
            "title": "Requirement response",
            "description": "some description",
            "requirement": {
                "id": self.requirement_id,
                "title": self.requirement_title,
            },
            "value": True,
        }
    ]

    response = self.app.post_json(
        base_request_path,
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.post_json(
        "{}?acc_token={}".format(base_request_path, "some_random_phrase"),
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.post_json(
        request_path,
        {
            "data": [
                {
                    "requirement": {
                        "id": self.requirement_id,
                        "title": self.requirement_title,
                    }
                }
            ]
        },
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                "name": 0,
                "description": {"value": "Response required at least one of field [\"value\", \"values\"]"},
            },
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": [{"description": "some description"}]},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {'location': 'body', 'name': 'requirement', 'description': ['This field is required.']},
        ],
    )

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr = response.json["data"]

    for i, rr_data in enumerate(valid_data):
        for k, v in rr_data.items():
            self.assertEqual(rr[i][k], v)


def patch_award_requirement_response(self):
    request_path = "/tenders/{}/awards/{}/requirement_responses?acc_token={}".format(
        self.tender_id, self.award_id, self.tender_token
    )

    valid_data = [
        {
            "title": "Requirement response",
            "description": "some description",
            "requirement": {
                "id": self.requirement_id,
                "title": self.requirement_title,
            },
            "value": True,
        }
    ]

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr_id = response.json["data"][0]["id"]

    base_request_path = "/tenders/{}/awards/{}/requirement_responses/{}".format(self.tender_id, self.award_id, rr_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)
    updated_data = {
        "title": "Rquirement response updated",
        "value": 100,
    }

    response = self.app.patch_json(
        base_request_path,
        {"data": updated_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.patch_json(
        "{}?acc_token={}".format(base_request_path, "some_random_token"),
        {"data": updated_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': ['Must be either true or false.'],
                'location': 'body',
                'name': 'value',
            }
        ],
    )

    updated_data["value"] = True
    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    rr = response.json["data"]
    self.assertEqual(rr["title"], updated_data["title"])
    self.assertEqual(rr["value"], updated_data["value"])
    self.assertNotIn("evidences", rr)


def get_award_requirement_response(self):
    request_path = "/tenders/{}/awards/{}/requirement_responses?acc_token={}".format(
        self.tender_id, self.award_id, self.tender_token
    )

    valid_data = [
        {
            "title": "Requirement response",
            "description": "some description",
            "requirement": {
                "id": self.requirement_id,
                "title": self.requirement_title,
            },
            "value": True,
        }
    ]

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr_id = response.json["data"][0]["id"]

    response = self.app.get("/tenders/{}/awards/{}/requirement_responses".format(self.tender_id, self.award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rrs = response.json["data"]
    self.assertEqual(len(rrs), 1)

    for i, rr_data in enumerate(valid_data):
        for k, v in rr_data.items():
            self.assertIn(k, rrs[i])
            self.assertEqual(v, rrs[i][k])

    response = self.app.get(
        "/tenders/{}/awards/{}/requirement_responses/{}".format(self.tender_id, self.award_id, rr_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rr = response.json["data"]
    for k, v in valid_data[0].items():
        self.assertIn(k, rr)
        self.assertEqual(v, rr[k])


def create_award_requirement_response_evidence(self):
    base_request_path = "/tenders/{}/awards/{}/requirement_responses/{}/evidences".format(
        self.tender_id, self.award_id, self.rr_id
    )
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        base_request_path,
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.post_json(
        "{}?acc_token={}".format(base_request_path, "some_test_token"),
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.post_json(request_path, {"data": {"description": "some description"}}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{'description': ['type should be one of eligibleEvidences types'], 'location': 'body', 'name': 'type'}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "title": "Some title",
                "description": "some description",
                "type": "document",
            }
        },
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{'description': ['This field is required.'], 'location': 'body', 'name': 'relatedDocument'}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "title": "Some title",
                "description": "some description",
                "type": "document",
                "relatedDocument": {
                    "id": "0" * 32,
                    "title": "name.doc",
                },
            }
        },
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': ['relatedDocument.id should be one of award documents'],
                'location': 'body',
                'name': 'relatedDocument',
            }
        ],
    )

    response = self.app.post_json(request_path, {"data": valid_data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence = response.json["data"]

    for k, v in valid_data.items():
        self.assertIn(k, evidence)
        self.assertEqual(evidence[k], v)


def patch_award_requirement_response_evidence(self):
    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        "/tenders/{}/awards/{}/requirement_responses/{}/evidences?acc_token={}".format(
            self.tender_id, self.award_id, self.rr_id, self.tender_token
        ),
        {"data": valid_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    updated_data = {
        "title": "Updated title",
        "description": "Updated description",
    }

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/requirement_responses/{}/evidences/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.rr_id, evidence_id, self.tender_token
        ),
        {"data": updated_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidence = response.json["data"]

    self.assertEqual(evidence["title"], updated_data["title"])
    self.assertEqual(evidence["description"], updated_data["description"])

    response = self.app.delete(
        "/tenders/{}/awards/{}/requirement_responses/{}/evidences/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.rr_id, evidence_id, self.tender_token
        ),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def get_award_requirement_response_evidence(self):
    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        "/tenders/{}/awards/{}/requirement_responses/{}/evidences?acc_token={}".format(
            self.tender_id, self.award_id, self.rr_id, self.tender_token
        ),
        {"data": valid_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    response = self.app.get(
        "/tenders/{}/awards/{}/requirement_responses/{}/evidences".format(self.tender_id, self.award_id, self.rr_id)
    )

    evidences = response.json["data"]
    self.assertEqual(len(evidences), 1)

    for k, v in valid_data.items():
        self.assertIn(k, evidences[0])
        self.assertEqual(v, evidences[0][k])

    response = self.app.get(
        "/tenders/{}/awards/{}/requirement_responses/{}/evidences/{}".format(
            self.tender_id, self.award_id, self.rr_id, evidence_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rr = response.json["data"]
    for k, v in valid_data.items():
        self.assertIn(k, rr)
        self.assertEqual(v, rr[k])


def award_sign(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    request_path = "/tenders/{}/awards".format(self.tender_id)
    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_organization],
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
    # try to make unsuccessful award without sign
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Document with type 'notice' and format pkcs7-signature is required",
    )

    # add sign doc
    doc_id = self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents").json[
        "data"
    ]["id"]

    # try to add another sign
    request_body = {
        "data": {
            "title": "sign.p7s",
            "documentType": "notice",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "sign/pkcs7-signature",
        }
    }
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{award['id']}/documents?acc_token={self.tender_token}",
        request_body,
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "notice document in award should be only one",
    )

    # try to put sign
    response = self.app.put_json(
        f"/tenders/{self.tender_id}/awards/{award['id']}/documents/{doc_id}?acc_token={self.tender_token}",
        request_body,
    )

    # try to add another doc
    request_body["data"]["documentType"] = "winningBid"
    request_body["data"]["title"] = "winBid.doc"
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{award['id']}/documents?acc_token={self.tender_token}",
        request_body,
    )

    # try to make unsuccessful award after signing
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn(response.json["data"][-1]["id"], new_award_location)
    new_award = response.json["data"][-1]

    # try to make active award without sign
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Document with type 'notice' and format pkcs7-signature is required",
    )

    # add sign doc
    doc_id = self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award['id']}/documents").json[
        "data"
    ]["id"]

    # try to add another sign
    request_body["data"]["documentType"] = "notice"
    request_body["data"]["title"] = "sign.p7s"
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{new_award['id']}/documents?acc_token={self.tender_token}",
        request_body,
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "notice document in award should be only one",
    )

    # try to put sign
    response = self.app.put_json(
        f"/tenders/{self.tender_id}/awards/{new_award['id']}/documents/{doc_id}?acc_token={self.tender_token}",
        request_body,
    )

    # try to add another doc
    request_body["data"]["documentType"] = "winningBid"
    request_body["data"]["title"] = "winBid.doc"
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{new_award['id']}/documents?acc_token={self.tender_token}",
        request_body,
    )

    # try to make active award after signing
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )


def prolongation_award(self):
    tender = self.app.get(f"/tenders/{self.tender_id}").json["data"]
    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "lotID": self.initial_bids[0]["lotValues"][0]["relatedLot"] if self.initial_lots else None,
                }
            },
        )
    award_id = response.json["data"]["id"]
    period_start = dt_from_iso(response.json["data"]["period"]["startDate"])
    period_end = calculate_tender_full_date(
        period_start,
        timedelta(days=5),
        tender=tender,
        working_days=True,
    ).isoformat()
    self.assertEqual(response.json["data"]["period"]["endDate"], period_end)

    # try to add milestone for extension without description
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{award_id}/milestones?acc_token={self.tender_token}",
        {"data": {"code": AwardMilestoneCodes.CODE_EXTENSION_PERIOD.value}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "description", "description": ["This field is required."]},
    )

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{award_id}/milestones?acc_token={self.tender_token}",
        {"data": {"code": AwardMilestoneCodes.CODE_EXTENSION_PERIOD.value, "description": "Prolongation"}},
    )

    # check prolongation
    due_date = response.json["data"]["dueDate"]
    response = self.app.get(
        f'/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}',
    )
    period_start = dt_from_iso(response.json["data"]["period"]["startDate"])
    new_period_end = calculate_tender_full_date(
        period_start,
        timedelta(days=20),
        tender=tender,
        working_days=True,
    ).isoformat()
    self.assertEqual(response.json["data"]["period"]["endDate"], new_period_end)
    self.assertEqual(due_date, new_period_end)

    # try to add one more milestone for extension
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{award_id}/milestones?acc_token={self.tender_token}",
        {"data": {"code": AwardMilestoneCodes.CODE_EXTENSION_PERIOD.value, "description": "Prolongation"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"][0],
        {'milestones': ["There can be only one 'extensionPeriod' milestone"]},
    )

    # add document for prolongation
    request_body = {
        "data": {
            "title": "sign.p7s",
            "documentType": "extensionReport",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "sign/pkcs7-signature",
        }
    }
    self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{award_id}/documents?acc_token={self.tender_token}",
        request_body,
    )

    # try to add one more time doc for prolongation
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{award_id}/documents?acc_token={self.tender_token}",
        request_body,
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "extensionReport document in award should be only one",
    )


def qualified_eligible_awards(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[1]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")
    award_id = response.json["data"]["id"]
    # activate award without qualified and eligible
    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "qualified",
                "description": ["Can't update award to active status with not qualified"],
            },
            {
                "location": "body",
                "name": "eligible",
                "description": ["Can't update award to active status with not eligible"],
            },
        ],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active", "qualified": True}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Can't update award to active status with not eligible"],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active", "eligible": True}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Can't update award to active status with not qualified"],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active", "qualified": True, "eligible": False}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Can't update award to active status with not eligible"],
    )

    # successful activation
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    # cancel the winner
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "cancelled"}},
    )

    # set award to unsuccesssful status without qualified or eligible False
    new_award = self.app.get(f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}").json["data"][-1]
    new_award_id = new_award["id"]
    self.assertEqual(new_award["status"], "pending")

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award_id}/documents")
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "qualified": True, "eligible": True}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Can't update award to unsuccessful status when qualified/eligible isn't set to False"],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "eligible": False}},
        status=422,
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "qualified": False}},
        status=422,
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "eligible": True}},
        status=422,
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "qualified": True}},
        status=422,
    )

    # successful setting unsuccessful
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{new_award_id}?acc_token={self.tender_token}",
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": True}},
    )
