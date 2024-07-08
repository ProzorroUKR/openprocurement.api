import unittest
from copy import deepcopy
from datetime import timedelta
from unittest import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
)
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationDocumentResourceTestMixin,
    TenderCancellationResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    create_tender_lot_cancellation,
    create_tender_lots_cancellation,
    patch_tender_lot_cancellation,
    patch_tender_lots_cancellation,
)
from openprocurement.tender.esco.tests.base import (
    BaseESCOContentWebTest,
    test_tender_esco_bids,
    test_tender_esco_lots,
)
from openprocurement.tender.openeu.tests.cancellation import (
    TenderCancellationBidsAvailabilityUtils,
)
from openprocurement.tender.openeu.tests.cancellation_blanks import (
    bids_on_tender_cancellation_in_auction,
    bids_on_tender_cancellation_in_awarded,
    bids_on_tender_cancellation_in_pre_qualification,
    bids_on_tender_cancellation_in_pre_qualification_stand_still,
    bids_on_tender_cancellation_in_qualification,
    bids_on_tender_cancellation_in_tendering,
    cancellation_active_award,
    cancellation_active_qualification,
    cancellation_active_qualification_j1427,
    cancellation_active_tendering_j708,
    cancellation_unsuccessful_award,
    cancellation_unsuccessful_qualification,
    create_cancellation_in_qualification_complaint_period,
)
from openprocurement.tender.openua.tests.cancellation import (
    TenderAwardsCancellationResourceTestMixin,
    TenderCancellationComplaintResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
)
from openprocurement.tender.openua.tests.cancellation_blanks import (
    access_create_tender_cancellation_complaint,
    activate_cancellation,
    create_cancellation_in_award_complaint_period,
    create_tender_cancellation,
    create_tender_cancellation_with_cancellation_lots,
    patch_tender_cancellation,
)


class TenderCancellationResourceTest(
    BaseESCOContentWebTest, TenderCancellationResourceTestMixin, TenderCancellationResourceNewReleaseTestMixin
):
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_activate_cancellation = snitch(activate_cancellation)


class TenderCancellationBidsAvailabilityTest(BaseESCOContentWebTest, TenderCancellationBidsAvailabilityUtils):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_tender_esco_bids * 2
    initial_lots = test_tender_esco_lots
    bid_visible_fields = ["status", "documents", "tenderers", "id", "eligibilityDocuments"]
    doc_id_by_type = {}
    valid_bids = []

    def setUp(self):
        super().setUp()
        self.valid_bids = list(self.initial_bids_tokens.keys())
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
        create_cancellation_in_qualification_complaint_period
    )


class TenderLotCancellationResourceTest(BaseESCOContentWebTest):
    initial_lots = test_tender_esco_lots

    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseESCOContentWebTest):
    initial_lots = 2 * test_tender_esco_lots

    initial_auth = ("Basic", ("broker", ""))
    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)
    test_create_tender_cancellation_with_cancellation_lots = snitch(create_tender_cancellation_with_cancellation_lots)


class TenderAwardsCancellationResourceTest(BaseESCOContentWebTest, TenderAwardsCancellationResourceTestMixin):
    initial_lots = 2 * test_tender_esco_lots
    initial_status = "active.tendering"
    initial_bids = test_tender_esco_bids

    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)
    test_cancellation_active_tendering_j708 = snitch(cancellation_active_tendering_j708)
    test_cancellation_active_qualification = snitch(cancellation_active_qualification)
    test_cancellation_unsuccessful_qualification = snitch(cancellation_unsuccessful_qualification)
    test_cancellation_active_award = snitch(cancellation_active_award)
    test_cancellation_unsuccessful_award = snitch(cancellation_unsuccessful_award)
    test_create_cancellation_in_award_complaint_period = snitch(create_cancellation_in_award_complaint_period)


class TenderCancellationComplaintResourceTest(BaseESCOContentWebTest, TenderCancellationComplaintResourceTestMixin):
    initial_bids = test_tender_esco_bids

    @mock.patch("openprocurement.tender.core.procedure.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super().setUp()

        # Create cancellation
        cancellation = deepcopy(test_tender_below_cancellation)
        cancellation.update({"reasonType": "noDemand"})
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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationBidsAvailabilityTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotCancellationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotsCancellationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardsCancellationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
