from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_claim,
    test_tender_below_draft_complaint,
    test_tender_below_lots,
    test_tender_below_supplier,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.open.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_open_bids,
    test_tender_open_complaint_objection,
)
from openprocurement.tender.open.tests.post_blanks import (
    create_complaint_post_claim_forbidden,
    create_complaint_post_complaint_owner,
    create_complaint_post_explanation,
    create_complaint_post_explanation_invalid,
    create_complaint_post_release_forbidden,
    create_complaint_post_status_forbidden,
    create_complaint_post_tender_owner,
    create_complaint_post_validate_recipient,
    create_complaint_post_validate_related_post,
    create_tender_complaint_post_by_complaint_owner_document_json,
    create_tender_complaint_post_by_tender_owner_document_json,
    create_tender_complaint_post_document_json,
    get_complaint_post,
    get_complaint_posts,
    get_tender_complaint_post_document_json,
    patch_complaint_post,
    put_tender_complaint_document_json,
)

date_after_2020_04_19 = get_now() - timedelta(days=1)


class TenderComplaintPostResourceMixin:
    app = None
    tender_id = None
    complaint_id = None
    post_id = None
    document_id = None
    claim_data = deepcopy(test_tender_below_claim)

    def post_claim(self, status=201):
        url = "/tenders/{}/complaints".format(self.tender_id)
        result = self.app.post_json(url, {"data": self.claim_data}, status=status)
        self.complaint_id = result.json["data"]["id"]
        return result

    def patch_complaint(self, data, acc_token=None, status=200):
        url = "/tenders/{}/complaints/{}".format(self.tender_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.patch_json(url, {"data": data}, status=status)

    def post_post(self, data, acc_token=None, status=201):
        url = "/tenders/{}/complaints/{}/posts".format(self.tender_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def patch_post(self, data, status=200):
        url = "/tenders/{}/complaints/{}/posts/{}".format(self.tender_id, self.complaint_id, self.post_id)
        return self.app.patch_json(url, {"data": data}, status=status)

    def get_posts(self, status=200):
        url = "/tenders/{}/complaints/{}/posts".format(self.tender_id, self.complaint_id)
        return self.app.get(url, status=status)

    def get_post(self, status=200):
        url = "/tenders/{}/complaints/{}/posts/{}".format(self.tender_id, self.complaint_id, self.post_id)
        return self.app.get(url, status=status)

    def post_post_document(self, data, acc_token=None, status=201):
        url = "/tenders/{}/complaints/{}/documents".format(self.tender_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def put_post_document(self, data, acc_token=None, status=200):
        url = "/tenders/{}/complaints/{}/documents/{}".format(self.tender_id, self.complaint_id, self.document_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.put_json(url, {"data": data}, status=status)

    def get_post_documents(self, status=200, params=None):
        url = "/tenders/{}/complaints/{}/documents".format(self.tender_id, self.complaint_id)
        if params:
            url = "{}?{}".format(url, "&".join(["{}={}".format(k, v) for k, v in params.items()]))
        return self.app.get(url, status=status)

    def get_post_document(self, status=200):
        url = "/tenders/{}/complaints/{}/documents/{}".format(self.tender_id, self.complaint_id, self.document_id)
        return self.app.get(url, status=status)


class TenderQualificationComplaintPostResourceMixin:
    app = None
    tender_id = None
    qualification_id = None
    complaint_id = None
    post_id = None
    document_id = None
    claim_data = deepcopy(test_tender_below_claim)

    def post_claim(self, status=201):
        url = "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, list(self.initial_bids_tokens.values())[0]
        )
        result = self.app.post_json(url, {"data": self.claim_data}, status=status)
        self.complaint_id = result.json["data"]["id"]
        return result

    def patch_complaint(self, data, acc_token=None, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id
        )
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.patch_json(url, {"data": data}, status=status)

    def post_post(self, data, acc_token=None, status=201):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts".format(
            self.tender_id, self.qualification_id, self.complaint_id
        )
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def patch_post(self, data, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.post_id
        )
        return self.app.patch_json(url, {"data": data}, status=status)

    def get_posts(self, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts".format(
            self.tender_id, self.qualification_id, self.complaint_id
        )
        return self.app.get(url, status=status)

    def get_post(self, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.post_id
        )
        return self.app.get(url, status=status)

    def post_post_document(self, data, acc_token=None, status=201):
        url = "/tenders/{}/qualifications/{}/complaints/{}/documents".format(
            self.tender_id, self.qualification_id, self.complaint_id
        )
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def put_post_document(self, data, acc_token=None, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.document_id
        )
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.put_json(url, {"data": data}, status=status)

    def get_post_documents(self, status=200, params=None):
        url = "/tenders/{}/qualifications/{}/complaints/{}/documents".format(
            self.tender_id, self.qualification_id, self.complaint_id
        )
        if params:
            url = "{}?{}".format(url, "&".join(["{}={}".format(k, v) for k, v in params.items()]))
        return self.app.get(url, status=status)

    def get_post_document(self, status=200):
        url = "/tenders/{}/qualifications/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.document_id
        )
        return self.app.get(url, status=status)


class TenderAwardComplaintPostResourceMixin:
    app = None
    tender_id = None
    award_id = None
    complaint_id = None
    post_id = None
    document_id = None
    claim_data = deepcopy(test_tender_below_claim)

    def post_claim(self, status=201):
        url = "/tenders/{}/awards/{}/complaints?acc_token={}".format(
            self.tender_id, self.award_id, list(self.initial_bids_tokens.values())[0]
        )
        result = self.app.post_json(url, {"data": self.claim_data}, status=status)
        self.complaint_id = result.json["data"]["id"]
        return result

    def patch_complaint(self, data, acc_token=None, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.patch_json(url, {"data": data}, status=status)

    def post_post(self, data, acc_token=None, status=201):
        url = "/tenders/{}/awards/{}/complaints/{}/posts".format(self.tender_id, self.award_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def patch_post(self, data, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.award_id, self.complaint_id, self.post_id
        )
        return self.app.patch_json(url, {"data": data}, status=status)

    def get_posts(self, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/posts".format(self.tender_id, self.award_id, self.complaint_id)
        return self.app.get(url, status=status)

    def get_post(self, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.award_id, self.complaint_id, self.post_id
        )
        return self.app.get(url, status=status)

    def post_post_document(self, data, acc_token=None, status=201):
        url = "/tenders/{}/awards/{}/complaints/{}/documents".format(self.tender_id, self.award_id, self.complaint_id)
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def put_post_document(self, data, acc_token=None, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, self.document_id
        )
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.put_json(url, {"data": data}, status=status)

    def get_post_documents(self, status=200, params=None):
        url = "/tenders/{}/awards/{}/complaints/{}/documents".format(self.tender_id, self.award_id, self.complaint_id)
        if params:
            url = "{}?{}".format(url, "&".join(["{}={}".format(k, v) for k, v in params.items()]))
        return self.app.get(url, status=status)

    def get_post_document(self, status=200):
        url = "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, self.document_id
        )
        return self.app.get(url, status=status)


class TenderCancellationComplaintPostResourceMixin:
    app = None
    tender_id = None
    cancellation_id = None
    complaint_id = None
    post_id = None
    document_id = None

    def patch_complaint(self, data, acc_token=None, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id
        )
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.patch_json(url, {"data": data}, status=status)

    def post_post(self, data, acc_token=None, status=201):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts".format(
            self.tender_id, self.cancellation_id, self.complaint_id
        )
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def patch_post(self, data, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.post_id
        )
        return self.app.patch_json(url, {"data": data}, status=status)

    def get_posts(self, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts".format(
            self.tender_id, self.cancellation_id, self.complaint_id
        )
        return self.app.get(url, status=status)

    def get_post(self, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/posts/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.post_id
        )
        return self.app.get(url, status=status)

    def post_post_document(self, data, acc_token=None, status=201):
        url = "/tenders/{}/cancellations/{}/complaints/{}/documents".format(
            self.tender_id, self.cancellation_id, self.complaint_id
        )
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.post_json(url, {"data": data}, status=status)

    def put_post_document(self, data, acc_token=None, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.document_id
        )
        if acc_token:
            url = "{}?acc_token={}".format(url, acc_token)
        return self.app.put_json(url, {"data": data}, status=status)

    def get_post_documents(self, status=200, params=None):
        url = "/tenders/{}/cancellations/{}/complaints/{}/documents".format(
            self.tender_id, self.cancellation_id, self.complaint_id
        )
        if params:
            url = "{}?{}".format(url, "&".join(["{}={}".format(k, v) for k, v in params.items()]))
        return self.app.get(url, status=status)

    def get_post_document(self, status=200):
        url = "/tenders/{}/cancellations/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.cancellation_id, self.complaint_id, self.document_id
        )
        return self.app.get(url, status=status)


class ClaimPostResourceMixin:
    test_create_complaint_post_claim_forbidden = snitch(create_complaint_post_claim_forbidden)


class ComplaintPostResourceMixin:
    test_create_complaint_post_release_forbidden = snitch(create_complaint_post_release_forbidden)
    test_create_complaint_post_status_forbidden = snitch(create_complaint_post_status_forbidden)
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

    # explanations
    test_create_complaint_post_explanation_invalid = snitch(create_complaint_post_explanation_invalid)
    test_create_complaint_post_explanation = snitch(create_complaint_post_explanation)


class TenderComplaintPostResourceTest(
    BaseTenderUAContentWebTest, ComplaintPostResourceMixin, TenderComplaintPostResourceMixin
):
    initial_lots = test_tender_below_lots

    def setUp(self):
        super().setUp()
        objection_data = deepcopy(test_tender_open_complaint_objection)
        objection_data["relatesTo"] = "tender"
        objection_data["relatedItem"] = self.tender_id
        complaint_data = deepcopy(test_tender_below_draft_complaint)
        complaint_data["objections"] = [objection_data]
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {"data": complaint_data},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.objection_id = response.json["data"]["objections"][0]["id"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderAwardComplaintPostResourceTest(
    BaseTenderUAContentWebTest,
    ComplaintPostResourceMixin,
    ClaimPostResourceMixin,
    TenderAwardComplaintPostResourceMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_bids
    initial_lots = test_tender_below_lots

    def setUp(self):
        super().setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_supplier],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                        "lotID": self.initial_lots[0]["id"],
                    }
                },
            )

        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")

        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )

        # Create complaint for award
        objection_data = deepcopy(test_tender_open_complaint_objection)
        objection_data["relatesTo"] = "award"
        objection_data["relatedItem"] = self.award_id
        complaint_data = deepcopy(test_tender_below_draft_complaint)
        complaint_data["objections"] = [objection_data]
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(
                self.tender_id, self.award_id, self.initial_bids_tokens[self.initial_bids[0]["id"]]
            ),
            {"data": complaint_data},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.objection_id = response.json["data"]["objections"][0]["id"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


@patch("openprocurement.tender.core.procedure.validation.RELEASE_2020_04_19", date_after_2020_04_19)
class TenderCancellationComplaintPostResourceTest(
    BaseTenderUAContentWebTest, ComplaintPostResourceMixin, TenderCancellationComplaintPostResourceMixin
):
    initial_lots = test_tender_below_lots

    @patch("openprocurement.tender.core.procedure.validation.RELEASE_2020_04_19", date_after_2020_04_19)
    def setUp(self):
        super().setUp()

        # Create cancellation
        cancellation = deepcopy(test_tender_below_cancellation)
        cancellation.update({"reasonType": "noDemand"})
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
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, self.cancellation_id, self.tender_token),
            {"data": {"status": "pending"}},
        )

        # Create complaint for cancellation
        objection_data = deepcopy(test_tender_open_complaint_objection)
        objection_data["relatesTo"] = "cancellation"
        objection_data["relatedItem"] = self.cancellation_id
        complaint_data = deepcopy(test_tender_below_draft_complaint)
        complaint_data["objections"] = [objection_data]
        response = self.app.post_json(
            "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, self.cancellation_id),
            {"data": complaint_data},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.objection_id = response.json["data"]["objections"][0]["id"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
