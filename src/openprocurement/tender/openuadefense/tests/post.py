from openprocurement.tender.belowthreshold.tests.base import test_author, test_organization, test_draft_complaint
from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.openua.tests.post import (
    ComplaintPostResourceMixin,
    TenderComplaintPostResourceMixin,
    TenderAwardComplaintPostResourceMixin,
)
from openprocurement.tender.openuadefense.tests.base import BaseTenderUAContentWebTest


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
