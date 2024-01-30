import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_bids,
    test_tender_below_with_inspector_data,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.review_request_blanks import (
    create_review_request,
    patch_review_request,
    patch_tender_with_review_request
)


class BaseReviewRequestTestMixin:
    test_create_review_request = snitch(create_review_request)
    test_patch_review_request = snitch(patch_review_request)


class TenderReviewRequestActiveEnquiresTestMixin(BaseReviewRequestTestMixin):
    test_patch_tender_with_review_request = snitch(patch_tender_with_review_request)


class TenderReviewRequestActiveAwardedTestMixin(BaseReviewRequestTestMixin):
    pass


class TenderReviewRequestActiveEnquiresResourceTest(TenderContentWebTest, TenderReviewRequestActiveEnquiresTestMixin):
    initial_data = test_tender_below_with_inspector_data
    initial_status = "active.enquiries"
    initial_lots = test_lots_data = test_tender_below_lots


class TenderReviewRequestActiveAwardedResourceTest(TenderContentWebTest, TenderReviewRequestActiveAwardedTestMixin):
    initial_data = test_tender_below_with_inspector_data
    initial_status = "active.awarded"
    initial_bids = test_tender_below_bids
    initial_lots = test_lots_data = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderReviewRequestActiveEnquiresResourceTest))
    suite.addTest(unittest.makeSuite(TenderReviewRequestActiveAwardedResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
