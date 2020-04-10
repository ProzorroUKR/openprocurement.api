# -*- coding: utf-8 -*-
import unittest
from mock import patch
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots, test_cancellation

from openprocurement.tender.competitivedialogue.tests.base import (
    test_bids,
    test_shortlistedFirms,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
)
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
    TenderCancellationDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderStage2LotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    # TenderStage2LotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
)
from openprocurement.tender.competitivedialogue.tests.stage2.cancellation_blanks import (
    cancellation_active_qualification_j1427,
)
from openprocurement.tender.openua.tests.cancellation import (
    TenderCancellationResourceNewReleaseTestMixin,
    TenderCancellationComplaintResourceTestMixin,

)
from openprocurement.tender.openua.tests.cancellation_blanks import (
    activate_cancellation,
    create_cancellation_in_tender_complaint_period,
)
from openprocurement.api.constants import RELEASE_2020_04_19


for bid in test_bids:
    bid["tenderers"][0]["identifier"]["id"] = test_shortlistedFirms[0]["identifier"]["id"]
    bid["tenderers"][0]["identifier"]["scheme"] = test_shortlistedFirms[0]["identifier"]["scheme"]


class TenderStage2EUCancellationResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
):
    test_activate_cancellation = snitch(activate_cancellation)
    test_create_cancellation_in_tender_complaint_period = snitch(create_cancellation_in_tender_complaint_period)


class TenderStage2EULotCancellationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)


class TenderStage2EULotsCancellationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)


class TenderStage2EUCancellationDocumentResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderCancellationDocumentResourceTestMixin
):
    def setUp(self):
        super(TenderStage2EUCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
        if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
            set_complaint_period_end()

        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


class TenderStage2EUCancellationComplaintResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderCancellationComplaintResourceTestMixin
):

    initial_bids = test_bids

    @patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderStage2EUCancellationComplaintResourceTest, self).setUp()
        set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
        if set_complaint_period_end:
            set_complaint_period_end()

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


class TenderStage2UACancellationResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin
):
    initial_auth = ("Basic", ("broker", ""))

    test_activate_cancellation = snitch(activate_cancellation)
    test_create_cancellation_in_tender_complaint_period = snitch(create_cancellation_in_tender_complaint_period)


class TenderStage2UALotCancellationResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderStage2UALotsCancellationResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)


class TenderStage2UACancellationDocumentResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest, TenderCancellationDocumentResourceTestMixin
):

    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderStage2UACancellationDocumentResourceTest, self).setUp()
        set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
        if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
            set_complaint_period_end()

        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UACancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UACancellationDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
