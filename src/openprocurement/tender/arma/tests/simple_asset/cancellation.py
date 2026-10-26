import unittest

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.arma.tests.complex_asset.cancellation import (
    TenderCancellationBidsAvailabilityUtils,
)
from openprocurement.tender.arma.tests.complex_asset.cancellation_blanks import (
    bids_on_tender_cancellation_in_tendering,
    check_sign_doc_before_cancellation_activation,
)
from openprocurement.tender.arma.tests.simple_asset.base import (
    BaseTenderSimpleAssetContentWebTest,
    test_tender_arma_simple_bids,
    test_tender_arma_simple_lots,
)
from openprocurement.tender.arma.tests.simple_asset.cancellation_blanks import (
    bids_on_tender_cancellation_in_awarded,
    bids_on_tender_cancellation_in_qualification,
)
from openprocurement.tender.open.tests.above_threshold_ua.cancellation_blanks import (
    create_tender_cancellation_before_19_04_2020,
    patch_tender_cancellation_before_19_04_2020,
)
from openprocurement.tender.open.tests.below_threshold.base import (
    test_tender_below_cancellation,
)
from openprocurement.tender.open.tests.below_threshold.cancellation import (
    TenderCancellationDocumentResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
    TenderCancellationResourceTestMixin,
)
from openprocurement.tender.open.tests.below_threshold.cancellation_blanks import (
    create_tender_lot_cancellation,
    create_tender_lots_cancellation,
    patch_tender_lot_cancellation,
)


class TenderCancellationResourceTest(
    BaseTenderSimpleAssetContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
):
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation_before_19_04_2020 = snitch(create_tender_cancellation_before_19_04_2020)
    test_patch_tender_cancellation_before_19_04_2020 = snitch(patch_tender_cancellation_before_19_04_2020)
    test_check_sign_doc_before_cancellation_activation = snitch(check_sign_doc_before_cancellation_activation)


class TenderCancellationBidsAvailabilityTest(
    BaseTenderSimpleAssetContentWebTest, TenderCancellationBidsAvailabilityUtils
):
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_tender_arma_simple_bids * 2
    initial_lots = test_tender_arma_simple_lots
    bid_visible_fields = [
        "status",
        "documents",
        "tenderers",
        "id",
        "eligibilityDocuments",
        "lotValues",
    ]
    doc_id_by_type = {}
    valid_bids = []

    def setUp(self):
        super().setUp()
        self.valid_bids = list(self.initial_bids_tokens.keys())
        self._prepare_bids_docs()

    test_bids_on_tender_cancellation_in_tendering = snitch(bids_on_tender_cancellation_in_tendering)
    test_bids_on_tender_cancellation_in_qualification = snitch(bids_on_tender_cancellation_in_qualification)
    test_bids_on_tender_cancellation_in_awarded = snitch(bids_on_tender_cancellation_in_awarded)


class TenderLotCancellationResourceTest(BaseTenderSimpleAssetContentWebTest):
    initial_lots = test_tender_arma_simple_lots
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseTenderSimpleAssetContentWebTest):
    initial_lots = 2 * test_tender_arma_simple_lots
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)


class TenderCancellationDocumentResourceTest(
    BaseTenderSimpleAssetContentWebTest, TenderCancellationDocumentResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        if RELEASE_2020_04_19 < get_now():
            self.set_complaint_period_end()

        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_tender_below_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationBidsAvailabilityTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotCancellationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotsCancellationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
