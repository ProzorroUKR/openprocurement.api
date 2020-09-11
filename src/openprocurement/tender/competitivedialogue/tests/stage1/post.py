from copy import deepcopy
from mock import patch

from openprocurement.tender.belowthreshold.tests.base import test_draft_complaint, test_cancellation
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
    test_author,
    test_bids,
)
from openprocurement.tender.openua.tests.post import (
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderComplaintPostResourceMixin,
    TenderQualificationComplaintPostResourceMixin,
    TenderCancellationComplaintPostResourceMixin,
    date_after_2020_04_19,
)


class TenderCompetitiveDialogUAComplaintPostResourceTest(
    BaseCompetitiveDialogUAContentWebTest,
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderComplaintPostResourceMixin
):
    docservice = True

    def setUp(self):
        super(TenderCompetitiveDialogUAComplaintPostResourceTest, self).setUp()
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



class TenderCompetitiveDialogEUComplaintPostResourceTest(
    BaseCompetitiveDialogEUContentWebTest,
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderComplaintPostResourceMixin
):
    docservice = True

    def setUp(self):
        super(TenderCompetitiveDialogEUComplaintPostResourceTest, self).setUp()
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


class TenderCompetitiveDialogUAQualificationComplaintPostResourceTest(
    BaseCompetitiveDialogUAContentWebTest,
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderQualificationComplaintPostResourceMixin
):
    docservice = True
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_author

    def setUp(self):
        super(TenderCompetitiveDialogUAQualificationComplaintPostResourceTest, self).setUp()
        # Create bid
        bid_data = deepcopy(test_bids[0])
        bid_data["value"] = {"amount": 500}
        bidder_data = bid_data["tenderers"][0]
        bidder_data["identifier"]["id"] = u"00037256"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

        # Create bid
        bid_data["value"] = {"amount": 101}
        bidder_data["identifier"]["id"] = u"00037257"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        # Create another bid
        bid_data["value"] = {"amount": 111}
        bidder_data["identifier"]["id"] = u"00037258"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})

        # simulate chronograph tick
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("chronograph", ""))
        response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
        self.app.authorization = auth

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
                self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
            ),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]

        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderCompetitiveDialogEUQualificationComplaintPostResourceTest(
    BaseCompetitiveDialogEUContentWebTest,
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderQualificationComplaintPostResourceMixin
):
    docservice = True
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_author

    def setUp(self):
        super(TenderCompetitiveDialogEUQualificationComplaintPostResourceTest, self).setUp()
        # Create bid
        bid_data = deepcopy(self.initial_bids[0])
        bid_data["value"] = {"amount": 500}
        bidder_data = bid_data["tenderers"][0]
        bidder_data["identifier"]["id"] = u"00037256"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

        # Create bid
        bid_data["value"] = {"amount": 101}
        bidder_data["identifier"]["id"] = u"00037257"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        # Create another bid
        bid_data["value"] = {"amount": 111}
        bidder_data["identifier"]["id"] = u"00037258"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})

        # simulate chronograph tick
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("chronograph", ""))
        response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
        self.app.authorization = auth

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
                self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
            ),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]

        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", date_after_2020_04_19)
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", date_after_2020_04_19)
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", date_after_2020_04_19)
class TenderCancellationComplaintPostResourceTest(
    BaseCompetitiveDialogUAContentWebTest,
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
