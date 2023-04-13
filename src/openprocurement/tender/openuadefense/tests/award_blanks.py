import mock
from freezegun import freeze_time
from datetime import timedelta
from mock import patch
from iso8601 import parse_date

from openprocurement.api.utils import get_now
from openprocurement.api.constants import (
    SANDBOX_MODE,
    RELEASE_2020_04_19,
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
    NO_DEFENSE_AWARD_CLAIMS_FROM,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.core.tests.cancellation import activate_cancellation_after_2020_04_19
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_complaint,
    test_tender_below_draft_complaint,
    test_tender_below_claim,
    test_tender_below_draft_claim,
    test_tender_below_cancellation,
)
from openprocurement.tender.openua.tests.award_blanks import (
    create_tender_award_claim as create_tender_award_claim_ua,
    review_tender_award_claim as review_tender_award_claim_ua,
)


def tender_award_complaint_period(
    self, date, mock_normalized_date, mock_midnight_date, expected_date, expected_sb_date
):
    freezer = freeze_time(date)
    freezer.start()

    patcher_normalized = mock.patch(
        "openprocurement.tender.core.utils.NORMALIZED_COMPLAINT_PERIOD_FROM", mock_normalized_date
    )
    patcher_normalized.start()

    patcher_midnight = mock.patch(
        "openprocurement.tender.core.utils.WORKING_DATE_ALLOW_MIDNIGHT_FROM", mock_midnight_date
    )
    patcher_midnight.start()

    self.create_tender()

    tender = self.mongodb.tenders.get(self.tender_id)
    self.set_status(tender["status"])

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {"data": {"suppliers": [test_tender_below_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]

    self.app.authorization = auth

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

    end_date = response.json["data"]["awards"][0]["complaintPeriod"]["endDate"]

    if SANDBOX_MODE:
        self.assertEqual(end_date, expected_sb_date.isoformat())
    else:
        self.assertEqual(end_date, expected_date.isoformat())

    patcher_normalized.stop()
    patcher_midnight.stop()

    freezer.stop()


# TenderAwardResourceTest
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM",
       get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM",
       get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO",
       get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO",
       get_now() + timedelta(days=100))
def check_tender_award_complaint_period_dates_before_new(self):
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
                "value": {"amount": 500},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    updated_award = response.json["data"]
    self.assertIn("complaintPeriod", updated_award)
    self.assertIn("startDate", updated_award["complaintPeriod"])
    self.assertIn("endDate", updated_award["complaintPeriod"])
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)
    updated_award = response.json["data"]
    self.assertIn("complaintPeriod", updated_award)
    self.assertIn("startDate", updated_award["complaintPeriod"])
    self.assertIn("endDate", updated_award["complaintPeriod"])


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM",
       get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM",
       get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO",
       get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO",
       get_now() - timedelta(days=1))
def check_tender_award_complaint_period_dates_after_new(self):
    return check_tender_award_complaint_period_dates_before_new(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def check_tender_award_complaint_period_dates_new(self):
    self.app.authorization = ("Basic", ("token", ""))
    request_path = "/tenders/{}/awards".format(self.tender_id)
    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "value": {"amount": 500},
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {
            "data": {
                "status": "unsuccessful"
            }
        },
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_award = response.json["data"]
    self.assertNotIn("complaintPeriod", updated_award)
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)
    updated_award = response.json["data"]
    self.assertIn("complaintPeriod", updated_award)
    self.assertIn("startDate", updated_award["complaintPeriod"])
    self.assertIn("endDate", updated_award["complaintPeriod"])

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    updated_award = response.json["data"]
    self.assertIn("complaintPeriod", updated_award)
    self.assertIn("startDate", updated_award["complaintPeriod"])
    self.assertIn("endDate", updated_award["complaintPeriod"])


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
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(
        new_award_location[-81:] + "?acc_token={}".format(self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)
    origin_complaint_period_end_date = parse_date(response.json["data"]["complaintPeriod"]["endDate"])

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        new_award_location[-81:] + "/complaints?acc_token={}".format(bid_token),
        {
            "data": test_tender_below_complaint
        },
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
        data.update({
            "reviewDate": now.isoformat(),
            "reviewPlace": "some",
        })

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
    new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < get_now() < NEW_DEFENSE_COMPLAINTS_TO
    if new_defence_complaints:
        self.assertEqual(origin_complaint_period_end_date, parse_date(response.json["data"]["complaintPeriod"]["endDate"]))
    else:
        self.assertGreater(get_now(), parse_date(response.json["data"]["complaintPeriod"]["endDate"]))

    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(new_award_location[-81:], {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(new_award_location[-81:], {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 4)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def patch_tender_award_active_before_new(self):
    return patch_tender_award_active(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
def patch_tender_award_active_after_new(self):
    return patch_tender_award_active(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def patch_tender_award_active_new(self):
    return patch_tender_award_active(self)


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
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

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

    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    origin_complaint_period_end_date = parse_date(response.json["data"]["complaintPeriod"]["endDate"])

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award["id"], bid_token),
        {
            "data": test_tender_below_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]

    now = get_now()
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(
                    self.tender_id, award["id"], complaint_id),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ("Basic", ("reviewer", ""))
    data = {"status": "accepted"}
    if RELEASE_2020_04_19 < now:
        data.update({
            "reviewDate": now.isoformat(),
            "reviewPlace": "some",
        })
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

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award["id"]), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < get_now() < NEW_DEFENSE_COMPLAINTS_TO
    if new_defence_complaints:
        self.assertEqual(origin_complaint_period_end_date, parse_date(response.json["data"]["complaintPeriod"]["endDate"]))
    else:
        self.assertGreater(get_now(), parse_date(response.json["data"]["complaintPeriod"]["endDate"]))

    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(new_award_location[-81:], {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(new_award_location[-81:], {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 4)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def patch_tender_award_unsuccessful_before_new(self):
    return patch_tender_award_unsuccessful(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
def patch_tender_award_unsuccessful_after_new(self):
    return patch_tender_award_unsuccessful(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def patch_tender_award_unsuccessful_new(self):
    return patch_tender_award_unsuccessful(self)


# TenderLotAwardResourceTest

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
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

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

    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    origin_complaint_period_end_date = parse_date(response.json["data"]["complaintPeriod"]["endDate"])

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award["id"], bid_token),
        {
            "data": test_tender_below_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]

    now = get_now()
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(
                    self.tender_id, award["id"], complaint_id),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ("Basic", ("reviewer", ""))
    now = get_now()
    data = {"status": "accepted"}
    if RELEASE_2020_04_19 < now:
        data.update({
            "reviewDate": now.isoformat(),
            "reviewPlace": "some",
        })
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
    if now < NO_DEFENSE_AWARD_CLAIMS_FROM:
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

    new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < get_now() < NEW_DEFENSE_COMPLAINTS_TO
    if new_defence_complaints:
        self.assertEqual(origin_complaint_period_end_date, parse_date(response.json["data"]["complaintPeriod"]["endDate"]))
    else:
        self.assertGreater(get_now(), parse_date(response.json["data"]["complaintPeriod"]["endDate"]))

    response = self.app.patch_json(new_award_location[-81:], {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)
    new_award_location = response.headers["Location"]

    response = self.app.patch_json(new_award_location[-81:], {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("Location", response.headers)

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 4)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.validation.NO_DEFENSE_AWARD_CLAIMS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NO_DEFENSE_AWARD_CLAIMS_FROM", get_now() + timedelta(days=1))
def patch_tender_lot_award_unsuccessful_before_new(self):
    return patch_tender_lot_award_unsuccessful(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.validation.NO_DEFENSE_AWARD_CLAIMS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NO_DEFENSE_AWARD_CLAIMS_FROM", get_now() - timedelta(days=1))
def patch_tender_lot_award_unsuccessful_after_new(self):
    return patch_tender_lot_award_unsuccessful(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.validation.NO_DEFENSE_AWARD_CLAIMS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.award_blanks.NO_DEFENSE_AWARD_CLAIMS_FROM", get_now() - timedelta(days=1))
def patch_tender_lot_award_unsuccessful_new(self):
    return patch_tender_lot_award_unsuccessful(self)


# TenderAwardComplaintResourceTest

@patch("openprocurement.tender.openuadefense.validation.NO_DEFENSE_AWARD_CLAIMS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def create_tender_award_claim(self):
    return create_tender_award_claim_ua(self)


@patch("openprocurement.tender.openuadefense.validation.NO_DEFENSE_AWARD_CLAIMS_FROM", get_now() - timedelta(days=1))
def create_tender_award_claim_denied(self):
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
        {
            "data": test_tender_below_claim
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't add complaint of 'claim' type",
                "location": "body",
                "name": "data",
            }
        ],
    )


def get_tender_award_complaint(self):
    bid_token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], complaint)

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/some_id".format(self.tender_id, self.award_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}]
    )

    response = self.app.get("/tenders/some_id/awards/some_id/complaints/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def get_tender_award_complaints(self):
    bid_token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get("/tenders/{}/awards/{}/complaints".format(self.tender_id, self.award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], complaint)

    response = self.app.get("/tenders/some_id/awards/some_id/complaints", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        now = get_now().isoformat()
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add complaint only in complaintPeriod")


def get_tender_lot_award_complaint(self):
    bid_token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], complaint)

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/some_id".format(self.tender_id, self.award_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}]
    )

    response = self.app.get("/tenders/some_id/awards/some_id/complaints/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def get_tender_lot_award_complaints(self):
    bid_token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get("/tenders/{}/awards/{}/complaints".format(self.tender_id, self.award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], complaint)

    response = self.app.get("/tenders/some_id/awards/some_id/complaints", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        now = get_now().isoformat()
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add complaint only in complaintPeriod")


@patch("openprocurement.tender.openuadefense.validation.NO_DEFENSE_AWARD_CLAIMS_FROM", get_now() + timedelta(days=1))
def review_tender_award_claim(self):
    return review_tender_award_claim_ua(self)


# Tender2LotAwardComplaintResourceTest

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
            status=403
        )
        self.assertEqual(
            response.json,
            {"status": "error", "errors": [
                {"location": "body", "name": "data", "description": "Can't update draft complaint into pending status"}]}
        )

    else:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
            status=200
        )
        self.assertEqual(response.status, "200 OK")

    with patch(
        "openprocurement.tender.openuadefense.validation.NO_DEFENSE_AWARD_CLAIMS_FROM",
        get_now() + timedelta(days=1)
    ):

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
