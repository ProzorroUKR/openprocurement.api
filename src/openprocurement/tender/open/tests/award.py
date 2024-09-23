import unittest
from datetime import timedelta
from unittest import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.award import (
    Tender2LotAwardDocumentResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
    TenderAwardComplaintResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_lots_award_complaint_document,
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    patch_tender_lot_award_lots_none,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
    test_tender_below_lots,
)
from openprocurement.tender.core.tests.base import test_exclusion_criteria
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.open.tests.award_blanks import (
    another_award_for_one_lot_has_considered_complaint,
    another_award_has_considered_complaint,
    any_award_has_not_considered_complaint,
    any_lot_award_has_not_considered_complaint,
    award_for_another_lot_has_considered_complaint,
    award_has_resolved_complaint,
    award_has_satisfied_complaint,
    award_sign,
    bot_patch_tender_award_complaint,
    bot_patch_tender_award_complaint_forbidden,
    check_tender_award_complaint_period_dates,
    create_award_requirement_response,
    create_award_requirement_response_evidence,
    create_tender_award,
    create_tender_award_claim,
    create_tender_award_complaint,
    create_tender_award_complaint_after_2020_04_19,
    create_tender_award_complaint_not_active,
    create_tender_award_invalid,
    create_tender_award_no_scale_invalid,
    create_tender_lot_award,
    create_tender_lot_award_complaint,
    create_tender_lots_award,
    create_tender_lots_award_complaint,
    create_tender_lots_unsuccessful_award_complaint_check_bidders,
    get_award_requirement_response,
    get_award_requirement_response_evidence,
    get_tender_award,
    last_award_unsuccessful_next_check,
    lot_award_has_resolved_complaint,
    lot_award_has_satisfied_complaint,
    patch_award_requirement_response,
    patch_award_requirement_response_evidence,
    patch_tender_award,
    patch_tender_award_active,
    patch_tender_award_complaint,
    patch_tender_award_complaint_document,
    patch_tender_award_unsuccessful,
    patch_tender_award_unsuccessful_complaint_first,
    patch_tender_award_unsuccessful_complaint_second,
    patch_tender_award_unsuccessful_complaint_third,
    patch_tender_lot_award,
    patch_tender_lot_award_complaint,
    patch_tender_lot_award_unsuccessful,
    patch_tender_lots_award,
    patch_tender_lots_award_complaint,
    patch_tender_lots_award_complaint_document,
    prolongation_award,
    put_tender_lots_award_complaint_document,
    qualified_eligible_awards,
    review_tender_award_claim,
    review_tender_award_complaint,
    review_tender_award_stopping_complaint,
    tender_award_complaint_period,
)
from openprocurement.tender.open.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_below_organization,
    test_tender_open_bids,
    test_tender_open_three_bids,
)


class TenderUAAwardComplaintResourceTestMixin:
    test_create_tender_award_claim = snitch(create_tender_award_claim)
    test_create_tender_award_complaint_not_active = snitch(create_tender_award_complaint_not_active)
    test_create_tender_award_complaint_after_2020_04_19 = snitch(create_tender_award_complaint_after_2020_04_19)
    test_create_tender_award_complaint = snitch(create_tender_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_award_complaint)
    test_review_tender_award_complaint = snitch(review_tender_award_complaint)
    test_review_tender_award_claim = snitch(review_tender_award_claim)
    test_review_tender_award_stopping_complaint = snitch(review_tender_award_stopping_complaint)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)
    test_bot_patch_tender_award_complaint = snitch(bot_patch_tender_award_complaint)
    test_bot_patch_tender_award_complaint_forbidden = snitch(bot_patch_tender_award_complaint_forbidden)


class TenderAwardRequirementResponseTestMixin:
    initial_criteria = test_exclusion_criteria
    initial_lots = test_tender_below_lots

    test_create_award_requirement_response = snitch(create_award_requirement_response)
    test_patch_award_requirement_response = snitch(patch_award_requirement_response)
    test_get_award_requirement_response = snitch(get_award_requirement_response)


class TenderAwardRequirementResponseEvidenceTestMixin:
    initial_criteria = test_exclusion_criteria
    initial_lots = test_tender_below_lots

    test_create_award_requirement_response_evidence = snitch(create_award_requirement_response_evidence)
    test_patch_award_requirement_response_evidence = snitch(patch_award_requirement_response_evidence)
    test_get_award_requirement_response_evidence = snitch(get_award_requirement_response_evidence)


class TenderAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_open_bids

    test_create_tender_award = snitch(create_tender_award)
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)
    test_get_tender_award = snitch(get_tender_award)
    test_check_tender_award_complaint_period_dates = snitch(check_tender_award_complaint_period_dates)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_tender_award_complaint_period = snitch(tender_award_complaint_period)
    test_last_award_unsuccessful_next_check = snitch(last_award_unsuccessful_next_check)
    test_award_sign = snitch(award_sign)
    test_prolongation_award = snitch(prolongation_award)


class TenderAwardQualificationAfterComplaintMixin:
    test_award_has_satisfied_complaint = snitch(award_has_satisfied_complaint)
    test_award_has_resolved_complaint = snitch(award_has_resolved_complaint)
    test_any_award_has_non_considered_complaint = snitch(any_award_has_not_considered_complaint)
    test_another_award_has_considered_complaint = snitch(another_award_has_considered_complaint)


@mock.patch(
    "openprocurement.tender.core.procedure.state.award.QUALIFICATION_AFTER_COMPLAINT_FROM",
    get_now() - timedelta(days=1),
)
class TenderAwardQualificationAfterComplaint(TenderAwardQualificationAfterComplaintMixin, BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_open_three_bids

    test_patch_tender_award_unsuccessful_complaint_first = snitch(patch_tender_award_unsuccessful_complaint_first)
    test_patch_tender_award_unsuccessful_complaint_second = snitch(patch_tender_award_unsuccessful_complaint_second)


class TenderLotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_open_bids

    test_create_lot_award = snitch(create_tender_lot_award)
    test_patch_tender_lot_award = snitch(patch_tender_lot_award)
    test_patch_tender_lot_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class Tender2LotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_tender_below_lots
    initial_bids = test_tender_open_bids

    test_create_tender_lots_award = snitch(create_tender_lots_award)
    test_patch_tender_lots_award = snitch(patch_tender_lots_award)
    test_qualified_eligible_awards = snitch(qualified_eligible_awards)


class TenderAwardPendingResourceTestCase(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_bids

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
                        "lotID": self.initial_bids[0]["lotValues"][0]["relatedLot"] if self.initial_lots else None,
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]


@mock.patch(
    "openprocurement.tender.core.procedure.state.award.QUALIFICATION_AFTER_COMPLAINT_FROM",
    get_now() - timedelta(days=1),
)
class TenderAwardQualificationAfterComplaint(TenderAwardPendingResourceTestCase):
    initial_status = "active.qualification"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_open_three_bids

    test_patch_tender_award_unsuccessful_complaint_first = snitch(patch_tender_award_unsuccessful_complaint_first)
    test_patch_tender_award_unsuccessful_complaint_second = snitch(patch_tender_award_unsuccessful_complaint_second)
    test_patch_tender_award_unsuccessful_complaint_third = snitch(patch_tender_award_unsuccessful_complaint_third)
    test_create_tender_lots_unsuccessful_award_complaint_check_bidders = snitch(
        create_tender_lots_unsuccessful_award_complaint_check_bidders
    )


@mock.patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class Tender2LotAwardQualificationAfterComplaintMixin:
    test_lot_award_has_satisfied_complaint = snitch(lot_award_has_satisfied_complaint)
    test_lot_award_has_resolved_complaint = snitch(lot_award_has_resolved_complaint)
    test_any_lot_award_has_not_considered_complaint = snitch(any_lot_award_has_not_considered_complaint)
    test_another_award_for_one_lot_has_considered_complaint = snitch(another_award_for_one_lot_has_considered_complaint)
    test_award_for_another_lot_has_considered_complaint = snitch(award_for_another_lot_has_considered_complaint)


class Tender2LotAwardQualificationAfterComplaintResourceTest(
    Tender2LotAwardQualificationAfterComplaintMixin, TenderAwardPendingResourceTestCase
):
    initial_lots = 2 * test_tender_below_lots


class TenderAwardActiveResourceTestCase(TenderAwardPendingResourceTestCase):
    def setUp(self):
        super().setUp()
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")

        with change_auth(self.app, ("Basic", ("token", ""))):
            self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class TenderAwardComplaintResourceTest(
    TenderAwardActiveResourceTestCase, TenderAwardComplaintResourceTestMixin, TenderUAAwardComplaintResourceTestMixin
):
    initial_lots = test_tender_below_lots


class TenderLotAwardComplaintResourceTest(TenderAwardActiveResourceTestCase):
    initial_lots = test_tender_below_lots

    test_create_tender_lot_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_lot_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_lot_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_lot_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest):
    initial_lots = 2 * test_tender_below_lots

    test_create_tender_lots_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_lots_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderAwardComplaintResourceTestCase(TenderAwardActiveResourceTestCase):
    def setUp(self):
        super().setUp()

        # Create complaint for award
        bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]


class TenderAwardComplaintDocumentResourceTest(
    TenderAwardComplaintResourceTestCase,
    TenderAwardComplaintDocumentResourceTestMixin,
):
    initial_lots = test_tender_below_lots

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(TenderAwardComplaintResourceTestCase):
    initial_lots = 2 * test_tender_below_lots

    test_create_tender_lots_award_document = snitch(create_tender_lots_award_complaint_document)
    test_put_tender_lots_award_complaint_document = snitch(put_tender_lots_award_complaint_document)
    test_patch_tender_lots_award_complaint_document = snitch(patch_tender_lots_award_complaint_document)


class TenderAwardDocumentResourceTest(
    TenderAwardPendingResourceTestCase,
    TenderAwardDocumentResourceTestMixin,
):
    initial_lots = test_tender_below_lots


class Tender2LotAwardDocumentResourceTest(
    TenderAwardPendingResourceTestCase,
    Tender2LotAwardDocumentResourceTestMixin,
):
    initial_lots = 2 * test_tender_below_lots


class TenderAwardRequirementResponseResourceTest(
    TenderAwardRequirementResponseTestMixin, TenderAwardPendingResourceTestCase
):
    def setUp(self):
        super().setUp()
        response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
        criteria = response.json["data"]
        requirement = criteria[6]["requirementGroups"][0]["requirements"][0]
        self.requirement_id = requirement["id"]
        self.requirement_title = requirement["title"]


class TenderAwardRequirementResponseEvidenceResourceTest(
    TenderAwardRequirementResponseEvidenceTestMixin,
    TenderAwardPendingResourceTestCase,
):
    def setUp(self):
        super().setUp()
        response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
        criteria = response.json["data"]
        requirement = criteria[6]["requirementGroups"][0]["requirements"][0]
        self.requirement_id = requirement["id"]
        self.requirement_title = requirement["title"]

        request_path = "/tenders/{}/awards/{}/requirement_responses?acc_token={}".format(
            self.tender_id, self.award_id, self.tender_token
        )

        rr_data = [
            {
                "title": "Requirement response",
                "description": "some description",
                "requirement": {
                    "id": self.requirement_id,
                    "title": self.requirement_title,
                },
                "value": True,
            }
        ]

        response = self.app.post_json(request_path, {"data": rr_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.rr_id = response.json["data"][0]["id"]

        response = self.app.post_json(
            "/tenders/{}/awards/{}/documents?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.doc_id = response.json["data"]["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardQualificationAfterComplaint))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
