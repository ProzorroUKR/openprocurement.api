from mock import patch

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_draft_complaint,
    test_tender_below_cancellation,
)
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_cfaua_bids,
    test_tender_cfaua_lots,
)
from openprocurement.tender.openua.tests.post import (
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderComplaintPostResourceMixin,
    TenderAwardComplaintPostResourceMixin,
    TenderQualificationComplaintPostResourceMixin,
    TenderCancellationComplaintPostResourceMixin,
    date_after_2020_04_19,
)


class TenderComplaintPostResourceTest(
    BaseTenderContentWebTest,
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderComplaintPostResourceMixin
):
    docservice = True

    def setUp(self):
        super(TenderComplaintPostResourceTest, self).setUp()
        response = self.app.post_json(
            "/tenders/{}/complaints".format(
                self.tender_id
            ),
            {"data": test_tender_below_draft_complaint},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderQualificationComplaintPostResourceTest(
    BaseTenderContentWebTest,
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderQualificationComplaintPostResourceMixin
):
    docservice = True
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_below_author

    def setUp(self):
        super(TenderQualificationComplaintPostResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})

        # simulate chronograph tick
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.qualification_id = qualifications[0]["id"]

        for qualification in qualifications:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "active")

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {
                "status": "active.pre-qualification.stand-still"
            }},
        )
        self.assertEqual(response.status, "200 OK")

        # Create complaint for qualification
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
                self.tender_id, self.qualification_id, list(self.initial_bids_tokens.values())[0]
            ),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]

        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderAwardComplaintResourceTest(
    BaseTenderContentWebTest,
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderAwardComplaintPostResourceMixin
):
    docservice = True
    initial_status = "active.qualification.stand-still"
    initial_lots = test_tender_cfaua_lots
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderAwardComplaintResourceTest, self).setUp()
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))

        self.awards_ids = [award["id"] for award in response.json["data"]]
        self.award_id = self.awards_ids[0]

        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(
                self.tender_id, self.award_id, self.initial_bids_tokens[self.initial_bids[0]["id"]]
            ),
            {"data": test_tender_below_draft_complaint},
        )

        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", date_after_2020_04_19)
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", date_after_2020_04_19)
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", date_after_2020_04_19)
class TenderCancellationComplaintPostResourceTest(
    BaseTenderContentWebTest,
    ComplaintPostResourceMixin,
    TenderCancellationComplaintPostResourceMixin
):
    docservice = True

    @patch("openprocurement.tender.core.models.RELEASE_2020_04_19", date_after_2020_04_19)
    @patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", date_after_2020_04_19)
    @patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", date_after_2020_04_19)
    def setUp(self):
        super(TenderCancellationComplaintPostResourceTest, self).setUp()

        # Create cancellation
        cancellation = dict(**test_tender_below_cancellation)
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

        self.app.post_json(
            "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
                self.tender_id, self.cancellation_id, self.tender_token
            ),
            {"data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }},
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
            {"data": test_tender_below_draft_complaint},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
