from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_author, test_organization
from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest, test_bids
from openprocurement.tender.openua.tests.post_blanks import (
    create_complaint_post_status_forbidden,
    create_complaint_post_claim_forbidden,
    create_complaint_post_complaint_owner,
    create_complaint_post_tender_owner,
    create_complaint_post_validate_recipient,
    create_complaint_post_validate_related_post,
    patch_complaint_post,
    get_complaint_post,
    get_complaint_posts,
)


class TenderComplaintPostResourceMixin(object):
    app = None
    tender_id = None
    complaint_id = None
    post_id = None

    def patch_complaint(self, data, acc_token=None, status=200):
        url = "/tenders/{}/complaints/{}".format(
            self.tender_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.patch_json(url, {"data": data}, status=status)

    def post_post(self, data, acc_token=None, status=201):
        url = "/tenders/{}/complaints/{}/posts".format(
            self.tender_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def patch_post(self, data, status=200):
        url = "/tenders/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.complaint_id, self.post_id)
        return self.app.patch_json(url, {"data": data}, status=status)

    def get_posts(self, status=200):
        url = "/tenders/{}/complaints/{}/posts".format(
            self.tender_id, self.complaint_id)
        return self.app.get(url, status=status)

    def get_post(self, status=200):
        url = "/tenders/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.complaint_id, self.post_id)
        return self.app.get(url, status=status)


class TenderQualificationComplaintPostResourceMixin(object):
    app = None
    tender_id = None
    qualification_id = None
    complaint_id = None
    post_id = None

    def patch_complaint(self, data, acc_token=None, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.patch_json(url, {"data": data}, status=status)

    def post_post(self, data, acc_token=None, status=201):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts".format(
            self.tender_id, self.qualification_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def patch_post(self, data, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.post_id)
        return self.app.patch_json(url, {"data": data}, status=status)

    def get_posts(self, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts".format(
            self.tender_id, self.qualification_id, self.complaint_id)
        return self.app.get(url, status=status)

    def get_post(self, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.post_id)
        return self.app.get(url, status=status)


class TenderAwardComplaintPostResourceMixin(object):
    app = None
    tender_id = None
    award_id = None
    complaint_id = None
    post_id = None

    def patch_complaint(self, data, acc_token=None, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}".format(
            self.tender_id, self.award_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.patch_json(url, {"data": data}, status=status)

    def post_post(self, data, acc_token=None, status=201):
        url = "/tenders/{}/awards/{}/complaints/{}/posts".format(
            self.tender_id, self.award_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def patch_post(self, data, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.award_id, self.complaint_id, self.post_id)
        return self.app.patch_json(url, {"data": data}, status=status)

    def get_posts(self, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/posts".format(
            self.tender_id, self.award_id, self.complaint_id)
        return self.app.get(url, status=status)

    def get_post(self, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.award_id, self.complaint_id, self.post_id)
        return self.app.get(url, status=status)


class ComplaintPostResourceMixin(object):
    test_create_complaint_post_status_forbidden = snitch(create_complaint_post_status_forbidden)
    test_create_complaint_post_claim_forbidden = snitch(create_complaint_post_claim_forbidden)
    test_create_complaint_post_complaint_owner = snitch(create_complaint_post_complaint_owner)
    test_create_complaint_post_tender_owner = snitch(create_complaint_post_tender_owner)
    test_create_complaint_post_validate_recipient = snitch(create_complaint_post_validate_recipient)
    test_create_complaint_post_validate_related_post = snitch(create_complaint_post_validate_related_post)
    test_patch_complaint_post = snitch(patch_complaint_post)
    test_get_complaint_post = snitch(get_complaint_post)
    test_get_complaint_posts = snitch(get_complaint_posts)


class TenderComplaintPostResourceTest(
    BaseTenderUAContentWebTest,
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


class TenderAwardComplaintPostResourceTest(
    BaseTenderUAContentWebTest,
    ComplaintPostResourceMixin,
    TenderAwardComplaintPostResourceMixin
):
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
