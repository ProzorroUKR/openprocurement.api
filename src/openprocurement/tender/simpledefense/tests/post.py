from copy import deepcopy
from unittest.mock import patch

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_draft_complaint,
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.open.tests.base import test_tender_open_complaint_objection
from openprocurement.tender.open.tests.post import (
    ComplaintPostResourceMixin,
    TenderAwardComplaintPostResourceMixin,
    TenderCancellationComplaintPostResourceMixin,
    TenderComplaintPostResourceMixin,
    date_after_2020_04_19,
)
from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest,
    test_tender_simpledefense_bids,
)


class TenderComplaintPostResourceTest(
    BaseSimpleDefContentWebTest, ComplaintPostResourceMixin, TenderComplaintPostResourceMixin
):

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
    BaseSimpleDefContentWebTest, ComplaintPostResourceMixin, TenderAwardComplaintPostResourceMixin
):
    initial_status = "active.qualification"
    initial_bids = test_tender_simpledefense_bids

    def setUp(self):
        super().setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_organization],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                    }
                },
            )

        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")

        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
                {"data": {"status": "active", "qualified": True}},
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
    BaseSimpleDefContentWebTest, ComplaintPostResourceMixin, TenderCancellationComplaintPostResourceMixin
):

    def setUp(self):
        super().setUp()
        self.set_complaint_period_end()

        # Create cancellation
        test_tender_below_cancellation.update({"reasonType": "noDemand"})
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_tender_below_cancellation},
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
                    "title": "укр.doc",
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
