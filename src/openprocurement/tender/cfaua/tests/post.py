from openprocurement.tender.belowthreshold.tests.base import test_author
from openprocurement.tender.cfaua.tests.base import BaseTenderContentWebTest, test_bids, test_lots
from openprocurement.tender.openua.tests.post import (
    ComplaintPostResourceMixin,
    TenderComplaintPostResourceMixin,
    TenderAwardComplaintPostResourceMixin,
    TenderQualificationComplaintPostResourceMixin,
)


class TenderComplaintPostResourceTest(
    BaseTenderContentWebTest,
    ComplaintPostResourceMixin,
    TenderComplaintPostResourceMixin
):
    def setUp(self):
        super(TenderComplaintPostResourceTest, self).setUp()
        response = self.app.post_json(
            "/tenders/{}/complaints".format(
                self.tender_id
            ),
            {"data": {
                "title": "complaint title",
                "description": "complaint description",
                "author": test_author
            }},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderQualificationComplaintPostResourceTest(
    BaseTenderContentWebTest,
    ComplaintPostResourceMixin,
    TenderQualificationComplaintPostResourceMixin
):
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_author

    def setUp(self):
        super(TenderQualificationComplaintPostResourceTest, self).setUp()

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
            {"data": {
                "title": "complaint title",
                "description": "complaint description",
                "author": self.author_data
            }},
        )
        complaint = response.json["data"]

        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderAwardComplaintResourceTest(
    BaseTenderContentWebTest,
    ComplaintPostResourceMixin,
    TenderAwardComplaintPostResourceMixin
):
    initial_status = "active.qualification.stand-still"
    initial_lots = test_lots
    initial_bids = test_bids
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
            {"data": {
                "title": "complaint title",
                "description": "complaint description",
                "author": test_author
            }},
        )

        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
