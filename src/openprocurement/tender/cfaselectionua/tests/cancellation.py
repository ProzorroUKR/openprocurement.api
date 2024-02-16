import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
)
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceNewReleaseTestMixin,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_tender_cfaselectionua_bids,
    test_tender_cfaselectionua_lots,
)
from openprocurement.tender.cfaselectionua.tests.cancellation_blanks import (
    create_tender_cancellation,
    create_tender_cancellation_document,
    create_tender_cancellation_invalid,
    create_tender_lots_cancellation,
    get_tender_cancellation,
    get_tender_cancellations,
    not_found,
    patch_tender_cancellation,
    patch_tender_cancellation_document,
    patch_tender_lots_cancellation,
    put_tender_cancellation_document,
)


class TenderCancellationResourceTestMixin:
    test_create_tender_cancellation_invalid = snitch(create_tender_cancellation_invalid)
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_get_tender_cancellation = snitch(get_tender_cancellation)
    test_get_tender_cancellations = snitch(get_tender_cancellations)


class TenderCancellationDocumentResourceTestMixin:
    test_not_found = snitch(not_found)
    test_create_tender_cancellation_document = snitch(create_tender_cancellation_document)
    test_put_tender_cancellation_document = snitch(put_tender_cancellation_document)
    test_patch_tender_cancellation_document = snitch(patch_tender_cancellation_document)


class TenderLotCancellationResourceTest(
    TenderContentWebTest, TenderCancellationResourceTestMixin, TenderCancellationResourceNewReleaseTestMixin
):
    initial_status = "active.tendering"
    initial_lots = test_tender_cfaselectionua_lots
    initial_bids = test_tender_cfaselectionua_bids


@unittest.skip("Skip multi-lots tests")
class TenderLotsCancellationResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = 2 * test_tender_cfaselectionua_lots
    initial_bids = test_tender_cfaselectionua_bids

    test_create_tender_lots_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_lots_cancellation = snitch(patch_tender_lots_cancellation)


class TenderCancellationDocumentResourceTest(TenderContentWebTest, TenderCancellationDocumentResourceTestMixin):
    initial_lots = test_tender_cfaselectionua_lots
    initial_status = "active.tendering"

    def setUp(self):
        super().setUp()

        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_tender_below_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotCancellationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
