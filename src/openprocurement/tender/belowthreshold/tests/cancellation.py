# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_lots,
    test_tender_below_bids,
    test_tender_below_cancellation,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    create_tender_cancellation_invalid,
    create_tender_cancellation,
    patch_tender_cancellation,
    get_tender_cancellation,
    get_tender_cancellations,
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
    not_found,
    create_tender_cancellation_document,
    put_tender_cancellation_document,
    patch_tender_cancellation_document,
    patch_tender_cancellation_2020_04_19,
    create_tender_cancellation_before_19_04_2020,
    permission_cancellation_pending,

)
from openprocurement.tender.openua.tests.cancellation_blanks import create_tender_cancellation_2020_04_19


class TenderCancellationResourceTestMixin(object):
    test_create_tender_cancellation_invalid = snitch(create_tender_cancellation_invalid)
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_get_tender_cancellation = snitch(get_tender_cancellation)
    test_get_tender_cancellations = snitch(get_tender_cancellations)


class TenderCancellationResourceNewReleaseTestMixin(object):
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    test_create_tender_cancellation_19_04_2020 = snitch(create_tender_cancellation_2020_04_19)
    test_patch_tender_cancellation_19_04_2020 = snitch(patch_tender_cancellation_2020_04_19)
    test_create_tender_cancellation_before_19_04_2020 = snitch(create_tender_cancellation_before_19_04_2020)
    test_permission_cancellation_pending = snitch(permission_cancellation_pending)


class TenderCancellationDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_tender_cancellation_document = snitch(create_tender_cancellation_document)
    test_put_tender_cancellation_document = snitch(put_tender_cancellation_document)
    test_patch_tender_cancellation_document = snitch(patch_tender_cancellation_document)


class TenderCancellationResourceTest(
    TenderContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin
):
    initial_status = "active.tendering"
    initial_bids = test_tender_below_bids
    valid_reasonType_choices = ["noDemand", "unFixable", "expensesCut"]


class TenderLotCancellationResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_below_bids

    test_create_tender_lot_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_lot_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = 2 * test_tender_below_lots
    initial_bids = test_tender_below_bids

    test_create_tender_lots_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_lots_cancellation = snitch(patch_tender_lots_cancellation)


class TenderCancellationDocumentResourceTest(TenderContentWebTest, TenderCancellationDocumentResourceTestMixin):
    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_tender_below_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    # PASSED_PY3
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
