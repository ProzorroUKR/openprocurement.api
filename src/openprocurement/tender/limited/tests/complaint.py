from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
    test_tender_below_organization,
)
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_tender_negotiation_data,
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
    docservice = True
    initial_data = test_tender_negotiation_data

    def create_complaint(self, complaint_data, status=201, with_valid_relates_to=False):
        if with_valid_relates_to:
            complaint_data["objections"][0]["relatesTo"] = "award"
            complaint_data["objections"][0]["relatedItem"] = self.award_id
        url = f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={self.tender_token}"
        return self.app.post_json(url, {"data": complaint_data}, status=status)

    def setUp(self):
        super(TenderNegotiationAwardComplaintObjectionResourceTest, self).setUp()
        # Create award
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
            {"data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "qualified": True,
                "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
            }}
        )

        award = response.json["data"]
        self.award_id = award["id"]

        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active"}}
        )


class TenderNegotiationQuickAwardComplaintPostResourceTest(TenderNegotiationAwardComplaintObjectionResourceTest):
    docservice = True
    initial_data = test_tender_negotiation_quick_data


class TenderNegotiationCancellationComplaintObjectionResourceTest(
    BaseTenderContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_data = test_tender_negotiation_data

    def setUp(self):
        super(TenderNegotiationCancellationComplaintObjectionResourceTest, self).setUp()
        # Create award
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
            {"data": {"suppliers": [test_tender_below_organization], "qualified": True,
                      "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False}, }}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active"}}
        )
        self.set_all_awards_complaint_period_end()
        self.create_cancellation()
