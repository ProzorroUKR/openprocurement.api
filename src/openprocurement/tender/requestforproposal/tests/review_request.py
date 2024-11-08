import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.review_request_blanks import (
    activate_contract_with_without_approve,
    after_change_tender_re_approve,
    create_review_request,
    patch_review_request,
    patch_tender_with_review_request,
    review_request_for_multilot,
    review_request_multilot_unsuccessful,
)
from openprocurement.tender.requestforproposal.tests.base import (
    TenderContentWebTest,
    test_tender_rfp_bids,
    test_tender_rfp_lots,
    test_tender_rfp_with_inspector_data,
)


class TenderReviewRequestActiveEnquiresTestMixin:
    test_patch_tender_with_review_request = snitch(patch_tender_with_review_request)
    test_patch_review_request = snitch(patch_review_request)
    test_create_review_request = snitch(create_review_request)


class TenderReviewRequestActiveQualificationTestMixin:
    test_activate_contract_with_without_approve = snitch(activate_contract_with_without_approve)
    test_review_request_for_multilot = snitch(review_request_for_multilot)
    test_review_request_multilot_unsuccessful = snitch(review_request_multilot_unsuccessful)


class TenderReviewRequestActiveEnquiresResourceTest(TenderContentWebTest, TenderReviewRequestActiveEnquiresTestMixin):
    initial_data = test_tender_rfp_with_inspector_data
    initial_status = "active.enquiries"
    initial_lots = test_lots_data = test_tender_rfp_lots

    test_after_change_tender_re_approve = snitch(after_change_tender_re_approve)


class TenderReviewRequestActiveAwardedResourceTest(
    TenderContentWebTest, TenderReviewRequestActiveQualificationTestMixin
):
    tender_for_funders = True
    initial_data = test_tender_rfp_with_inspector_data
    initial_status = "active.qualification"
    initial_bids = test_tender_rfp_bids
    initial_lots = test_lots_data = test_tender_rfp_lots * 2


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderReviewRequestActiveEnquiresResourceTest))
    suite.addTest(unittest.makeSuite(TenderReviewRequestActiveAwardedResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
