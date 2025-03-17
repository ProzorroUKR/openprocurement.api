import unittest
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.award import (
    Tender2LotAwardDocumentResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    patch_tender_lot_award_lots_none,
)
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.competitiveordering.tests.award_blanks import (
    qualified_eligible_awards,
)
from openprocurement.tender.competitiveordering.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_below_organization,
    test_tender_co_bids,
    test_tender_co_criteria,
)
from openprocurement.tender.core.tests.utils import change_auth, generate_req_response
from openprocurement.tender.open.tests.award_blanks import (
    award_sign,
    check_tender_award_complaint_period_dates,
    create_award_requirement_response,
    create_award_requirement_response_evidence,
    create_tender_award,
    create_tender_award_invalid,
    create_tender_award_no_scale_invalid,
    create_tender_lot_award,
    create_tender_lots_award,
    get_award_requirement_response,
    get_award_requirement_response_evidence,
    get_tender_award,
    last_award_unsuccessful_next_check,
    patch_award_requirement_response,
    patch_award_requirement_response_evidence,
    patch_tender_award,
    patch_tender_award_active,
    patch_tender_award_unsuccessful,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    patch_tender_lots_award,
    prolongation_award,
    tender_award_complaint_period,
)


class TenderAwardRequirementResponseTestMixin:
    initial_criteria = test_tender_co_criteria
    initial_lots = test_tender_below_lots

    test_create_award_requirement_response = snitch(create_award_requirement_response)
    test_patch_award_requirement_response = snitch(patch_award_requirement_response)
    test_get_award_requirement_response = snitch(get_award_requirement_response)


class TenderAwardRequirementResponseEvidenceTestMixin:
    initial_criteria = test_tender_co_criteria
    initial_lots = test_tender_below_lots

    test_create_award_requirement_response_evidence = snitch(create_award_requirement_response_evidence)
    test_patch_award_requirement_response_evidence = snitch(patch_award_requirement_response_evidence)
    test_get_award_requirement_response_evidence = snitch(get_award_requirement_response_evidence)


@patch(
    "openprocurement.tender.competitiveordering.procedure.state.award.NEW_ARTICLE_17_CRITERIA_REQUIRED",
    get_now() + timedelta(days=1),
)
class TenderAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_co_bids

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


@patch(
    "openprocurement.tender.competitiveordering.procedure.state.award.NEW_ARTICLE_17_CRITERIA_REQUIRED",
    get_now() + timedelta(days=1),
)
class TenderLotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_co_bids

    test_create_lot_award = snitch(create_tender_lot_award)
    test_patch_tender_lot_award = snitch(patch_tender_lot_award)
    test_patch_tender_lot_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


@patch(
    "openprocurement.tender.competitiveordering.procedure.state.award.NEW_ARTICLE_17_CRITERIA_REQUIRED",
    get_now() + timedelta(days=1),
)
class Tender2LotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_tender_below_lots
    initial_bids = test_tender_co_bids

    test_create_tender_lots_award = snitch(create_tender_lots_award)
    test_patch_tender_lots_award = snitch(patch_tender_lots_award)
    test_qualified_eligible_awards = snitch(qualified_eligible_awards)


class TenderAwardPendingResourceTestCase(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_co_bids

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


class TenderAwardActiveResourceTestCase(TenderAwardPendingResourceTestCase):
    def setUp(self):
        super().setUp()
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")

        with change_auth(self.app, ("Basic", ("token", ""))):
            self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
                {"data": {"status": "active", "qualified": True}},
            )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


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

        boolean_requirement_criteria = []
        for criterion in criteria:
            if criterion["source"] in ("procuringEntity",):
                if criterion["requirementGroups"][0]["requirements"][0]["dataType"] == "boolean":
                    boolean_requirement_criteria.append(criterion)

        requirement = boolean_requirement_criteria[0]["requirementGroups"][0]["requirements"][0]
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

        boolean_requirement_criteria = []
        for criterion in criteria:
            if criterion["source"] in ("procuringEntity",):
                if criterion["requirementGroups"][0]["requirements"][0]["dataType"] == "boolean":
                    boolean_requirement_criteria.append(criterion)

        requirement = boolean_requirement_criteria[0]["requirementGroups"][0]["requirements"][0]
        self.requirement_id = requirement["id"]
        self.requirement_title = requirement["title"]

        request_path = "/tenders/{}/awards/{}/requirement_responses?acc_token={}".format(
            self.tender_id, self.award_id, self.tender_token
        )

        rr_data = generate_req_response(requirement)

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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
