from mock import patch
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_claim,
    test_organization,
    test_draft_complaint,
    test_cancellation,
)
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
    create_complaint_post_release_forbidden,
    create_tender_complaint_post_document_json,
    put_tender_complaint_document_json,
    get_tender_complaint_post_document_json,
    create_tender_complaint_post_by_complaint_owner_document_json,
    create_tender_complaint_post_by_tender_owner_document_json,
    create_complaint_post_review_date_forbidden,
)
from copy import deepcopy

date_after_2020_04_19 = get_now() - timedelta(days=1)


class TenderComplaintPostResourceMixin(object):
    app = None
    tender_id = None
    complaint_id = None
    post_id = None
    document_id = None
    claim_data = deepcopy(test_claim)

    def post_claim(self, status=201):
        url = "/tenders/{}/complaints".format(self.tender_id)
        result = self.app.post_json(url, {"data": self.claim_data}, status=status)
        self.complaint_id = result.json["data"]["id"]
        return result

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

    def post_post_document(self, data, acc_token=None, status=201):
        url = "/tenders/{}/complaints/{}/posts/{}/documents".format(
            self.tender_id, self.complaint_id, self.post_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def put_post_document(self, data, acc_token=None, status=200):
        url = "/tenders/{}/complaints/{}/posts/{}/documents/{}".format(
            self.tender_id, self.complaint_id, self.post_id, self.document_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.put_json(url, {"data": data}, status=status)

    def get_post_documents(self, status=200, params=None):
        url = "/tenders/{}/complaints/{}/posts/{}/documents".format(
            self.tender_id, self.complaint_id, self.post_id)
        if params:
            url = "{}?{}".format(url, "&".join(["{}={}".format(k, v) for k, v in params.iteritems()]))
        return self.app.get(url, status=status)

    def get_post_document(self, status=200):
        url = "/tenders/{}/complaints/{}/posts/{}/documents/{}".format(
            self.tender_id, self.complaint_id, self.post_id, self.document_id)
        return self.app.get(url, status=status)


class TenderQualificationComplaintPostResourceMixin(object):
    app = None
    tender_id = None
    qualification_id = None
    complaint_id = None
    post_id = None
    document_id = None
    claim_data = deepcopy(test_claim)

    def post_claim(self, status=201):
        url = "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id,  self.initial_bids_tokens.values()[0]
        )
        result = self.app.post_json(url, {"data": self.claim_data}, status=status)
        self.complaint_id = result.json["data"]["id"]
        return result

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

    def post_post_document(self, data, acc_token=None, status=201):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts/{}/documents".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.post_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def put_post_document(self, data, acc_token=None, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts/{}/documents/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.post_id, self.document_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.put_json(url, {"data": data}, status=status)

    def get_post_documents(self, status=200, params=None):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts/{}/documents".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.post_id)
        if params:
            url = "{}?{}".format(url, "&".join(["{}={}".format(k, v) for k, v in params.iteritems()]))
        return self.app.get(url, status=status)

    def get_post_document(self, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts/{}/documents/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.post_id, self.document_id)
        return self.app.get(url, status=status)


class TenderAwardComplaintPostResourceMixin(object):
    app = None
    tender_id = None
    award_id = None
    complaint_id = None
    post_id = None
    document_id = None
    claim_data = deepcopy(test_claim)

    def post_claim(self, status=201):
        url = "/tenders/{}/awards/{}/complaints?acc_token={}".format(
            self.tender_id, self.award_id, self.initial_bids_tokens.values()[0]
        )
        result = self.app.post_json(url, {"data": self.claim_data}, status=status)
        self.complaint_id = result.json["data"]["id"]
        return result

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

    def post_post_document(self, data, acc_token=None, status=201):
        url = "/tenders/{}/awards/{}/complaints/{}/posts/{}/documents".format(
            self.tender_id, self.award_id, self.complaint_id, self.post_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def put_post_document(self, data, acc_token=None, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/posts/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, self.post_id, self.document_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.put_json(url, {"data": data}, status=status)

    def get_post_documents(self, status=200, params=None):
        url = "/tenders/{}/awards/{}/complaints/{}/posts/{}/documents".format(
            self.tender_id, self.award_id, self.complaint_id, self.post_id)
        if params:
            url = "{}?{}".format(url, "&".join(["{}={}".format(k, v) for k, v in params.iteritems()]))
        return self.app.get(url, status=status)

    def get_post_document(self, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/posts/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, self.post_id, self.document_id)
        return self.app.get(url, status=status)


class TenderCancellationComplaintPostResourceMixin(object):
    app = None
    tender_id = None
    cancellation_id = None
    complaint_id = None
    post_id = None
    document_id = None

    def patch_complaint(self, data, acc_token=None, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.patch_json(url, {"data": data}, status=status)

    def post_post(self, data, acc_token=None, status=201):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts".format(
            self.tender_id, self.cancellation_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def patch_post(self, data, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.post_id)
        return self.app.patch_json(url, {"data": data}, status=status)

    def get_posts(self, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts".format(
            self.tender_id, self.cancellation_id, self.complaint_id)
        return self.app.get(url, status=status)

    def get_post(self, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.post_id)
        return self.app.get(url, status=status)

    def post_post_document(self, data, acc_token=None, status=201):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts/{}/documents".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.post_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def put_post_document(self, data, acc_token=None, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts/{}/documents/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.post_id, self.document_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.put_json(url, {"data": data}, status=status)

    def get_post_documents(self, status=200, params=None):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts/{}/documents".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.post_id)
        if params:
            url = "{}?{}".format(url, "&".join(["{}={}".format(k, v) for k, v in params.iteritems()]))
        return self.app.get(url, status=status)

    def get_post_document(self, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts/{}/documents/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.post_id, self.document_id)
        return self.app.get(url, status=status)


class ClaimPostResourceMixin(object):
    test_create_complaint_post_claim_forbidden = snitch(create_complaint_post_claim_forbidden)


class ComplaintPostResourceMixin(object):
    test_create_complaint_post_release_forbidden = snitch(create_complaint_post_release_forbidden)
    test_create_complaint_post_status_forbidden = snitch(create_complaint_post_status_forbidden)
    test_create_complaint_post_review_date_forbidden = snitch(create_complaint_post_review_date_forbidden)
    test_create_complaint_post_complaint_owner = snitch(create_complaint_post_complaint_owner)
    test_create_complaint_post_tender_owner = snitch(create_complaint_post_tender_owner)
    test_create_complaint_post_validate_recipient = snitch(create_complaint_post_validate_recipient)
    test_create_complaint_post_validate_related_post = snitch(create_complaint_post_validate_related_post)
    test_patch_complaint_post = snitch(patch_complaint_post)
    test_get_complaint_post = snitch(get_complaint_post)
    test_get_complaint_posts = snitch(get_complaint_posts)
    test_get_tender_complaint_post_document_json = snitch(get_tender_complaint_post_document_json)
    test_create_tender_complaint_post_document_json = snitch(create_tender_complaint_post_document_json)
    test_create_tender_complaint_post_by_complaint_owner_document_json = snitch(
        create_tender_complaint_post_by_complaint_owner_document_json
    )
    test_create_tender_complaint_post_by_tender_owner_document_json = snitch(
        create_tender_complaint_post_by_tender_owner_document_json
    )
    test_put_tender_complaint_document_json = snitch(put_tender_complaint_document_json)


class TenderComplaintPostResourceTest(
    BaseTenderUAContentWebTest,
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
            {"data": test_draft_complaint},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderAwardComplaintPostResourceTest(
    BaseTenderUAContentWebTest,
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
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
