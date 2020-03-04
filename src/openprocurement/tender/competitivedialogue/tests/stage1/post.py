from copy import deepcopy

from openprocurement.tender.belowthreshold.tests.base import test_draft_complaint
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
    test_author,
    test_bids,
)
from openprocurement.tender.openua.tests.post import (
    ComplaintPostResourceMixin,
    TenderComplaintPostResourceMixin,
    TenderQualificationComplaintPostResourceMixin,
)


class TenderCompetitiveDialogUAComplaintPostResourceTest(
    BaseCompetitiveDialogUAContentWebTest,
    ComplaintPostResourceMixin,
    TenderComplaintPostResourceMixin
):
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
    TenderComplaintPostResourceMixin
):
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
    TenderQualificationComplaintPostResourceMixin
):
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_author

    def setUp(self):
        super(TenderCompetitiveDialogUAQualificationComplaintPostResourceTest, self).setUp()
        # Create bid
        bidder_data = deepcopy(self.initial_bids[0]["tenderers"][0])
        bidder_data["identifier"]["id"] = u"00037256"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "selfEligible": True, "selfQualified": True, "tenderers": [bidder_data], "value": {"amount": 500}
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

        # Create bid
        bidder_data["identifier"]["id"] = u"00037257"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "selfEligible": True, "selfQualified": True, "tenderers": [bidder_data], "value": {"amount": 101}
                }
            },
        )
        # Create another bid
        bidder_data["identifier"]["id"] = u"00037258"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "selfEligible": True, "selfQualified": True, "tenderers": [bidder_data], "value": {"amount": 111}
                }
            },
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
    TenderQualificationComplaintPostResourceMixin
):
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_author

    def setUp(self):
        super(TenderCompetitiveDialogEUQualificationComplaintPostResourceTest, self).setUp()
        # Create bid
        bidder_data = deepcopy(self.initial_bids[0]["tenderers"][0])
        bidder_data["identifier"]["id"] = u"00037256"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "selfEligible": True, "selfQualified": True, "tenderers": [bidder_data], "value": {"amount": 500}
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

        # Create bid
        bidder_data["identifier"]["id"] = u"00037257"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "selfEligible": True, "selfQualified": True, "tenderers": [bidder_data], "value": {"amount": 101}
                }
            },
        )
        # Create another bid
        bidder_data["identifier"]["id"] = u"00037258"
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "selfEligible": True, "selfQualified": True, "tenderers": [bidder_data], "value": {"amount": 111}
                }
            },
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
