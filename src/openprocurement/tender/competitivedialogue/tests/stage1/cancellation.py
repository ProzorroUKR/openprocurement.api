# -*- coding: utf-8 -*-
import unittest
from mock import patch
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_cancellation

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
    test_tender_cd_stage1_bids,
    test_tender_cd_lots,
)

from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
    TenderCancellationDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
)
from openprocurement.tender.competitivedialogue.tests.stage1.cancellation_blanks import (
    cancellation_active_qualification_j1427,
)
from openprocurement.tender.openua.tests.cancellation import (
    TenderCancellationResourceNewReleaseTestMixin,
    TenderCancellationComplaintResourceTestMixin,
)
from openprocurement.tender.openua.tests.cancellation_blanks import (
    activate_cancellation,
    create_tender_cancellation_with_cancellation_lots
)


class CompetitiveDialogUACancellationResourceTest(
    BaseCompetitiveDialogUAContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin
):
    test_activate_cancellation = snitch(activate_cancellation)


class CompetitiveDialogUALotCancellationResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_tender_cd_lots
    initial_bids = test_tender_cd_stage1_bids
    test_bids_data = test_tender_cd_stage1_bids

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)


class CompetitiveDialogUALotsCancellationResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = 2 * test_tender_cd_lots
    initial_bids = test_tender_cd_stage1_bids
    test_bids_data = test_tender_cd_stage1_bids

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)
    test_create_tender_cancellation_with_cancellation_lots = snitch(create_tender_cancellation_with_cancellation_lots)


class CompetitiveDialogUACancellationComplaintResourceTest(
    BaseCompetitiveDialogUAContentWebTest, TenderCancellationComplaintResourceTestMixin
):

    initial_bids = test_tender_cd_stage1_bids
    test_bids_data = test_tender_cd_stage1_bids

    @patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    @patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super(CompetitiveDialogUACancellationComplaintResourceTest, self).setUp()

        # Create cancellation
        cancellation = dict(**test_tender_below_cancellation)
        cancellation.update({
            "reasonType": "noDemand"
        })
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


class CompetitiveDialogUACancellationDocumentResourceTest(
    BaseCompetitiveDialogUAContentWebTest, TenderCancellationDocumentResourceTestMixin
):
    def setUp(self):
        super(CompetitiveDialogUACancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_tender_below_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


class CompetitiveDialogEUCancellationResourceTest(
    BaseCompetitiveDialogEUContentWebTest,
    TenderCancellationResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_activate_cancellation = snitch(activate_cancellation)


class CompetitiveDialogEULotCancellationResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_tender_cd_lots
    initial_bids = test_tender_cd_stage1_bids
    test_bids_data = test_tender_cd_stage1_bids

    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)


class CompetitiveDialogEULotsCancellationResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_tender_cd_lots
    initial_bids = test_tender_cd_stage1_bids
    test_bids_data = test_tender_cd_stage1_bids
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)


class CompetitiveDialogEUCancellationDocumentResourceTest(
    BaseCompetitiveDialogEUContentWebTest, TenderCancellationDocumentResourceTestMixin
):

    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(CompetitiveDialogEUCancellationDocumentResourceTest, self).setUp()

        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_tender_below_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogUACancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUALotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUALotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEULotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEULotsCancellationResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
