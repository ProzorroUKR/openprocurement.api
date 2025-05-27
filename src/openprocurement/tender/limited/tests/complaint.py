from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_tender_negotiation_config,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_config,
    test_tender_negotiation_quick_data,
)
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
)


class TenderNegotiationAwardComplaintObjectionResourceTest(
    BaseTenderContentWebTest,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config

    def create_complaint(self, complaint_data, status=201, with_valid_relates_to=False):
        if with_valid_relates_to:
            complaint_data["objections"][0]["relatesTo"] = "award"
            complaint_data["objections"][0]["relatedItem"] = self.award_id
        url = f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={self.tender_token}"
        return self.app.post_json(url, {"data": complaint_data}, status=status)

    def setUp(self):
        super().setUp()
        # Create award
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
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
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )


class TenderNegotiationQuickAwardComplaintPostResourceTest(TenderNegotiationAwardComplaintObjectionResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


class TenderNegotiationCancellationComplaintObjectionResourceTest(
    BaseTenderContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config

    def setUp(self):
        super().setUp()
        # Create award
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
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
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )
        self.set_all_awards_complaint_period_end()
        self.create_cancellation()
