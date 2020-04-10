# -*- coding: utf-8 -*-
import unittest
from mock import patch
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots, test_cancellation
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
    TenderCancellationDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderLotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    # TenderLotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
)

from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest, test_bids
from openprocurement.tender.openua.tests.cancellation_blanks import (
    # TenderAwardsCancellationResourceTest
    cancellation_active_award,
    cancellation_unsuccessful_award,
    # TenderCancellationResourceTest
    create_tender_cancellation,
    patch_tender_cancellation,
    create_tender_cancellation_before_19_04_2020,
    patch_tender_cancellation_before_19_04_2020,
    create_tender_cancellation_2020_04_19,
    patch_tender_cancellation_2020_04_19,
    permission_cancellation_pending,
    activate_cancellation,
    create_tender_cancellation_complaint,
    patch_tender_cancellation_complaint,
    get_tender_cancellation_complaints,
    access_create_tender_cancellation_complaint,
    create_cancellation_in_tender_complaint_period,
    create_cancellation_in_award_complaint_period,
    create_tender_cancellation_with_cancellation_lots,
    bot_patch_tender_cancellation_complaint,
)


class TenderCancellationComplaintResourceTestMixin(object):

    test_create_tender_cancellation_complaint = snitch(create_tender_cancellation_complaint)
    test_patch_tender_cancellation_complaint = snitch(patch_tender_cancellation_complaint)
    test_get_tender_cancellation_complaints = snitch(get_tender_cancellation_complaints)
    test_bot_patch_tender_cancellation_complaint = snitch(bot_patch_tender_cancellation_complaint)


class TenderCancellationResourceNewReleaseTestMixin(object):
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    test_create_tender_cancellation_before_19_04_2020 = snitch(create_tender_cancellation_before_19_04_2020)
    test_patch_tender_cancellation_before_19_04_2020 = snitch(patch_tender_cancellation_before_19_04_2020)
    test_create_tender_cancellation_2020_04_19 = snitch(create_tender_cancellation_2020_04_19)
    test_patch_tender_cancellation_2020_04_19 = snitch(patch_tender_cancellation_2020_04_19)
    test_permission_cancellation_pending = snitch(permission_cancellation_pending)


class TenderCancellationResourceTest(
    BaseTenderUAContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin
):
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_activate_cancellation = snitch(activate_cancellation)
    test_create_cancellation_in_tender_complaint_period = snitch(create_cancellation_in_tender_complaint_period)


class TenderLotCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots

    test_create_tender_lot_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_lot_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_lots

    test_create_tender_lots_cancellation = snitch(create_tender_lots_cancellation)
    test_create_tender_cancellation_with_cancellation_lots = snitch(create_tender_cancellation_with_cancellation_lots)
    # test_patch_tender_lots_cancellation = snitch(patch_tender_lots_cancellation)


class TenderAwardsCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_lots
    initial_status = "active.auction"
    initial_bids = test_bids

    test_cancellation_active_award = snitch(cancellation_active_award)
    test_cancellation_unsuccessful_award = snitch(cancellation_unsuccessful_award)
    test_create_cancellation_in_award_complaint_period = snitch(create_cancellation_in_award_complaint_period)


class TenderCancellationComplaintResourceTest(
    BaseTenderUAContentWebTest, TenderCancellationComplaintResourceTestMixin
):
    initial_bids = test_bids

    @patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderCancellationComplaintResourceTest, self).setUp()
        self.set_complaint_period_end()

        # Create cancellation
        cancellation = dict(**test_cancellation)
        cancellation.update({
            "reasonType": "noDemand"
        })
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]

    test_access_create_tender_cancellation_complaint = snitch(access_create_tender_cancellation_complaint,)


class TenderCancellationDocumentResourceTest(
    BaseTenderUAContentWebTest, TenderCancellationDocumentResourceTestMixin
):
    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()

        if RELEASE_2020_04_19 < get_now():
            self.set_complaint_period_end()

        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_cancellation},
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
