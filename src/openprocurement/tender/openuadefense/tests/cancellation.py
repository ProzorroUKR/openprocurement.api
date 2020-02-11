# -*- coding: utf-8 -*-
import unittest
import mock
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
    TenderCancellationDocumentResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderCancellationResourceTest
    create_tender_cancellation,
    patch_tender_cancellation,
    # TenderLotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    # TenderLotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
)

from openprocurement.tender.openuadefense.tests.base import BaseTenderUAContentWebTest


MOCKED_RELEASE_DATE = "openprocurement.tender.core.models.RELEASE_2020_04_19"
date_after_release = get_now() - timedelta(days=1)
date_before_release = get_now() + timedelta(days=1)


@mock.patch(MOCKED_RELEASE_DATE, date_before_release)
class TenderCancellationResourceTest(BaseTenderUAContentWebTest, TenderCancellationResourceTestMixin):

    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)


@mock.patch(MOCKED_RELEASE_DATE, date_after_release)
class TenderCancellationResourceTest(
        BaseTenderUAContentWebTest, TenderCancellationResourceNewReleaseTestMixin):
    valid_reasonType_choices = ["noDemand", "unFixable", "expensesCut"]


class TenderLotCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_lots

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)


class TenderCancellationDocumentResourceTest(BaseTenderUAContentWebTest, TenderCancellationDocumentResourceTestMixin):
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
