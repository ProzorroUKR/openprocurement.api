# -*- coding: utf-8 -*-
import unittest
import mock
from datetime import timedelta

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now

from openprocurement.tender.belowthreshold.tests.base import TenderContentWebTest, test_lots, test_bids
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderCancellationResourceTest
    create_tender_cancellation_invalid,
    create_tender_cancellation,
    create_tender_cancellation_after_19_04_2020,
    patch_tender_cancellation,
    patch_tender_cancellation_after_19_04_2020,
    get_tender_cancellation,
    get_tender_cancellations,
    # TenderLotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    # TenderLotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
    # TenderCancellationDocumentResourceTest
    not_found,
    create_tender_cancellation_document,
    put_tender_cancellation_document,
    patch_tender_cancellation_document,
)


MOCKED_RELEASE_DATE = "openprocurement.tender.core.models.RELEASE_2020_04_19"
date_after_release = get_now() - timedelta(days=1)
date_before_release = get_now() + timedelta(days=1)


class TenderCancellationResourceTestMixin(object):
    test_create_tender_cancellation_invalid = snitch(create_tender_cancellation_invalid)
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_get_tender_cancellation = snitch(get_tender_cancellation)
    test_get_tender_cancellations = snitch(get_tender_cancellations)


class TenderCancellationResourceNewReleaseTestMixin(object):
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    test_create_tender_cancellation_after_19_04_2020 = snitch(create_tender_cancellation_after_19_04_2020)
    test_patch_tender_cancellation_after_19_04_2020 = snitch(patch_tender_cancellation_after_19_04_2020)


class TenderCancellationDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_tender_cancellation_document = snitch(create_tender_cancellation_document)
    test_put_tender_cancellation_document = snitch(put_tender_cancellation_document)
    test_patch_tender_cancellation_document = snitch(patch_tender_cancellation_document)


@mock.patch(MOCKED_RELEASE_DATE, date_before_release)
class TenderCancellationResourceTest(TenderContentWebTest, TenderCancellationResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_bids


@mock.patch(MOCKED_RELEASE_DATE, date_after_release)
class TenderCancellationResourceNewReleaseTest(TenderContentWebTest, TenderCancellationResourceNewReleaseTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_bids
    valid_reasonType_choices = ["noDemand", "unFixable", "expensesCut"]


class TenderLotCancellationResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_tender_lot_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_lot_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_tender_lots_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_lots_cancellation = snitch(patch_tender_lots_cancellation)


class TenderCancellationDocumentResourceTest(TenderContentWebTest, TenderCancellationDocumentResourceTestMixin):
    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"reason": "cancellation reason"}},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
