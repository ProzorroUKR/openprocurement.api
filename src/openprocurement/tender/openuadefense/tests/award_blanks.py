import mock
from freezegun import freeze_time

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.tender.belowthreshold.tests.base import test_organization


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

    tender = self.db.get(self.tender_id)
    self.set_status(tender["status"])

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {"data": {"suppliers": [test_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
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
