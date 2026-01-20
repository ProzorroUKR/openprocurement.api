from copy import deepcopy
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_draft_complaint,
    test_tender_below_supplier,
)
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_tender_negotiation_config,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_config,
    test_tender_negotiation_quick_data,
)
from openprocurement.tender.open.tests.base import test_tender_open_complaint_objection
from openprocurement.tender.open.tests.post import (
    TenderAwardComplaintPostResourceMixin,
    TenderCancellationComplaintPostResourceMixin,
    date_after_2020_04_19,
)
from openprocurement.tender.open.tests.post_blanks import (
    create_complaint_post_complaint_owner,
    create_complaint_post_status_forbidden,
    create_complaint_post_tender_owner,
    create_complaint_post_validate_recipient,
    create_complaint_post_validate_related_post,
    create_tender_complaint_post_document_json,
    get_complaint_post,
    get_complaint_posts,
    patch_complaint_post,
    put_tender_complaint_document_json,
)


class ComplaintPostResourceMixin:
    test_create_complaint_post_status_forbidden = snitch(create_complaint_post_status_forbidden)
    test_create_complaint_post_complaint_owner = snitch(create_complaint_post_complaint_owner)
    test_create_complaint_post_tender_owner = snitch(create_complaint_post_tender_owner)
    test_create_complaint_post_validate_recipient = snitch(create_complaint_post_validate_recipient)
    test_create_complaint_post_validate_related_post = snitch(create_complaint_post_validate_related_post)
    test_patch_complaint_post = snitch(patch_complaint_post)
    test_get_complaint_post = snitch(get_complaint_post)
    test_get_complaint_posts = snitch(get_complaint_posts)
    test_create_tender_complaint_post_document_json = snitch(create_tender_complaint_post_document_json)
    test_put_tender_complaint_document_json = snitch(put_tender_complaint_document_json)


class TenderNegotiationAwardComplaintPostResourceTest(
    BaseTenderContentWebTest, ComplaintPostResourceMixin, TenderAwardComplaintPostResourceMixin
):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config

    def setUp(self):
        super().setUp()
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )

        award = response.json["data"]
        self.award_id = award["id"]

        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True}},
        )

        # Create complaint for award
        objection_data = deepcopy(test_tender_open_complaint_objection)
        objection_data["relatesTo"] = "award"
        objection_data["relatedItem"] = self.award_id
        complaint_data = deepcopy(test_tender_below_draft_complaint)
        complaint_data["objections"] = [objection_data]
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints".format(self.tender_id, self.award_id),
            {"data": complaint_data},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.objection_id = response.json["data"]["objections"][0]["id"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderNegotiationQuickAwardComplaintPostResourceTest(TenderNegotiationAwardComplaintPostResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


@patch("openprocurement.tender.core.procedure.validation.RELEASE_2020_04_19", date_after_2020_04_19)
class TenderNegotiationCancellationComplaintPostResourceTest(
    BaseTenderContentWebTest, ComplaintPostResourceMixin, TenderCancellationComplaintPostResourceMixin
):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config

    @patch("openprocurement.tender.core.procedure.validation.RELEASE_2020_04_19", date_after_2020_04_19)
    def setUp(self):
        super().setUp()
        # Create award

        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "qualified": True,
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True}},
        )
        self.set_all_awards_complaint_period_end()

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

        self.add_sign_doc(
            self.tender_id,
            self.tender_token,
            docs_url=f"/cancellations/{self.cancellation_id}/documents",
            document_type="cancellationReport",
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
