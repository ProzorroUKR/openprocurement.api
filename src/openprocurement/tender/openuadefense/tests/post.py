from mock import patch

from openprocurement.tender.belowthreshold.tests.base import (
    test_organization,
    test_draft_complaint,
    test_cancellation,
)
from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.openua.tests.post import (
    ComplaintPostResourceMixin,
    TenderComplaintPostResourceMixin,
    TenderAwardComplaintPostResourceMixin,
    TenderCancellationComplaintPostResourceMixin,
    date_after_2020_04_19,
)
from openprocurement.tender.openuadefense.tests.base import BaseTenderUAContentWebTest, test_bids


class TenderComplaintPostResourceTest(
    BaseTenderUAContentWebTest,
    ComplaintPostResourceMixin,
    TenderComplaintPostResourceMixin
):
    docservice = True

    def setUp(self):
        super(TenderComplaintPostResourceTest, self).setUp()
        response = self.app.post_json(
            "/tenders/{}/complaints".format(
                self.tender_id
            ),
            {"data": test_draft_complaint},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderAwardComplaintPostResourceTest(
    BaseTenderUAContentWebTest,
    ComplaintPostResourceMixin,
    TenderAwardComplaintPostResourceMixin
):
    docservice = True
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintPostResourceTest, self).setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {"data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"]
                }}
            )

        award = response.json["data"]
        self.award_id = award["id"]

        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}".format(
                    self.tender_id, self.award_id
                ),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }}
            )

        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(
                self.tender_id, self.award_id, self.initial_bids_tokens[self.initial_bids[0]["id"]]
            ),
            {"data": test_draft_complaint},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", date_after_2020_04_19)
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", date_after_2020_04_19)
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", date_after_2020_04_19)
class TenderCancellationComplaintPostResourceTest(
    BaseTenderUAContentWebTest,
    ComplaintPostResourceMixin,
    TenderCancellationComplaintPostResourceMixin
):
    docservice = True

    @patch("openprocurement.tender.core.models.RELEASE_2020_04_19", date_after_2020_04_19)
    @patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", date_after_2020_04_19)
    @patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", date_after_2020_04_19)
    def setUp(self):
        super(TenderCancellationComplaintPostResourceTest, self).setUp()
        self.set_complaint_period_end()

        # Create cancellation
        cancellation = dict(**test_cancellation)
        cancellation.update({
            "reasonType": "noDemand"
        })
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]

        # Add document and update cancellation status to pending

        self.app.post(
            "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
                self.tender_id, self.cancellation_id, self.tender_token
            ),
            upload_files=[("file", "name.doc", "content")],
        )
        self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(
                self.tender_id, self.cancellation_id, self.tender_token
            ),
            {"data": {"status": "pending"}},
        )

        # Create complaint for cancellation

        response = self.app.post_json(
            "/tenders/{}/cancellations/{}/complaints".format(
                self.tender_id, self.cancellation_id
            ),
            {"data": test_draft_complaint},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
