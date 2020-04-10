# -*- coding: utf-8 -*-
import unittest
import mock
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_cancellation

from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
    TenderCancellationDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderLotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
    # TenderLotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
)
from openprocurement.tender.openua.tests.cancellation import (
    TenderCancellationResourceNewReleaseTestMixin,
    TenderCancellationComplaintResourceTestMixin,
)

from openprocurement.tender.openua.tests.cancellation_blanks import (
    # TenderCancellationResourceTest
    create_tender_cancellation,
    patch_tender_cancellation,
    access_create_tender_cancellation_complaint,
    activate_cancellation,
    create_cancellation_in_tender_complaint_period,
    create_cancellation_in_award_complaint_period,
    create_tender_cancellation_with_cancellation_lots
)

from openprocurement.tender.openeu.tests.cancellation import TenderCancellationBidsAvailabilityUtils
from openprocurement.tender.openeu.tests.cancellation_blanks import (
    # TenderAwardsCancellationResourceTest
    cancellation_active_qualification,
    cancellation_unsuccessful_qualification,
    cancellation_active_award,
    cancellation_unsuccessful_award,
    cancellation_active_tendering_j708,
    cancellation_active_qualification_j1427,
    # TenderCancellationBidsAvailabilityTest
    bids_on_tender_cancellation_in_tendering,
    bids_on_tender_cancellation_in_pre_qualification,
    bids_on_tender_cancellation_in_pre_qualification_stand_still,
    bids_on_tender_cancellation_in_auction,
    bids_on_tender_cancellation_in_qualification,
    bids_on_tender_cancellation_in_awarded,
    create_cancellation_in_qualification_complaint_period,
)

from openprocurement.tender.esco.tests.base import BaseESCOContentWebTest, test_bids, test_lots
from openprocurement.api.constants import RELEASE_2020_04_19


class TenderCancellationResourceTest(
    BaseESCOContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin
):
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_activate_cancellation = snitch(activate_cancellation)
    test_create_cancellation_in_tender_complaint_period = snitch(create_cancellation_in_tender_complaint_period)


class TenderCancellationBidsAvailabilityTest(BaseESCOContentWebTest, TenderCancellationBidsAvailabilityUtils):
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_bids * 2
    bid_visible_fields = [u"status", u"documents", u"tenderers", u"id", u"eligibilityDocuments"]
    doc_id_by_type = {}
    valid_bids = []

    def setUp(self):
        super(TenderCancellationBidsAvailabilityTest, self).setUp()
        self.valid_bids = self.initial_bids_tokens.keys()
        self._prepare_bids_docs()

    test_bids_on_tender_cancellation_in_tendering = snitch(bids_on_tender_cancellation_in_tendering)
    test_bids_on_tender_cancellation_in_pre_qualification = snitch(bids_on_tender_cancellation_in_pre_qualification)
    test_bids_on_tender_cancellation_in_pre_qualification_stand_still = snitch(
        bids_on_tender_cancellation_in_pre_qualification_stand_still
    )
    test_bids_on_tender_cancellation_in_auction = snitch(bids_on_tender_cancellation_in_auction)
    test_bids_on_tender_cancellation_in_qualification = snitch(bids_on_tender_cancellation_in_qualification)
    test_bids_on_tender_cancellation_in_awarded = snitch(bids_on_tender_cancellation_in_awarded)
    create_cancellation_in_qualification_complaint_period = snitch(
        create_cancellation_in_qualification_complaint_period)


class TenderLotCancellationResourceTest(BaseESCOContentWebTest):
    initial_lots = test_lots

    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseESCOContentWebTest):
    initial_lots = 2 * test_lots

    initial_auth = ("Basic", ("broker", ""))
    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)
    test_create_tender_cancellation_with_cancellation_lots = snitch(create_tender_cancellation_with_cancellation_lots)


class TenderAwardsCancellationResourceTest(BaseESCOContentWebTest):
    initial_lots = 2 * test_lots
    initial_status = "active.tendering"
    initial_bids = test_bids

    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)
    test_cancellation_active_tendering_j708 = snitch(cancellation_active_tendering_j708)
    test_cancellation_active_qualification = snitch(cancellation_active_qualification)
    test_cancellation_unsuccessful_qualification = snitch(cancellation_unsuccessful_qualification)
    test_cancellation_active_award = snitch(cancellation_active_award)
    test_cancellation_unsuccessful_award = snitch(cancellation_unsuccessful_award)
    test_create_cancellation_in_award_complaint_period = snitch(create_cancellation_in_award_complaint_period)


class TenderCancellationComplaintResourceTest(BaseESCOContentWebTest, TenderCancellationComplaintResourceTestMixin):

    initial_bids = test_bids

    @mock.patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @mock.patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @mock.patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
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

    test_access_create_tender_cancellation_complaint = snitch(access_create_tender_cancellation_complaint)


class TenderCancellationDocumentResourceTest(BaseESCOContentWebTest, TenderCancellationDocumentResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))

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
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationBidsAvailabilityTest))
    suite.addTest(unittest.makeSuite(TenderLotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
