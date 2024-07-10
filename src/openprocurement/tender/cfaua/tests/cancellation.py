import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_cancellation,
)
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    create_tender_cancellation_document,
    create_tender_lot_cancellation,
    not_found,
    patch_tender_cancellation_document,
    patch_tender_lot_cancellation,
    put_tender_cancellation_document,
)
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_cfaua_bids,
    test_tender_cfaua_lots,
)
from openprocurement.tender.cfaua.tests.cancellation_blanks import (  # Cancellation tender; Cancellation lot
    cancel_lot_active_auction,
    cancel_lot_active_awarded,
    cancel_lot_active_pre_qualification,
    cancel_lot_active_pre_qualification_stand_still,
    cancel_lot_active_qualification,
    cancel_lot_active_qualification_stand_still,
    cancel_lot_active_tendering,
    cancellation_tender_active_auction,
    cancellation_tender_active_awarded,
    cancellation_tender_active_pre_qualification,
    cancellation_tender_active_pre_qualification_stand_still,
    cancellation_tender_active_qualification,
    cancellation_tender_active_qualification_stand_still,
    cancellation_tender_active_tendering,
)
from openprocurement.tender.openeu.tests.cancellation_blanks import (
    create_cancellation_in_qualification_complaint_period,
)
from openprocurement.tender.openua.tests.cancellation import (
    TenderCancellationComplaintResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
)
from openprocurement.tender.openua.tests.cancellation_blanks import (
    access_create_tender_cancellation_complaint,
    activate_cancellation,
    create_tender_cancellation,
    create_tender_cancellation_with_cancellation_lots,
    patch_tender_cancellation,
)

no_award_logic = True
one_lot_restriction = True


class TenderCancellationResourceTest(
    BaseTenderContentWebTest, TenderCancellationResourceTestMixin, TenderCancellationResourceNewReleaseTestMixin
):
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_activate_cancellation = snitch(activate_cancellation)


class TenderLotCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = test_tender_cfaua_lots
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)
    test_create_tender_cancellation_with_cancellation_lots = snitch(create_tender_cancellation_with_cancellation_lots)


class TenderCancellationComplaintResourceTest(BaseTenderContentWebTest, TenderCancellationComplaintResourceTestMixin):
    initial_lots = test_tender_cfaua_lots
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"

    @patch("openprocurement.tender.core.procedure.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super().setUp()
        self.set_complaint_period_end()
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


class TenderCancellationDocumentResourceTest(BaseTenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        if RELEASE_2020_04_19 < get_now():
            self.set_complaint_period_end()

        # Create cancellation
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_tender_below_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]

    test_not_found = snitch(not_found)
    test_create_tender_cancellation_document = snitch(create_tender_cancellation_document)
    test_put_tender_cancellation_document = snitch(put_tender_cancellation_document)
    test_patch_tender_cancellation_document = snitch(patch_tender_cancellation_document)


class CancellationTenderAndLotOnAllStage(BaseTenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    initial_bids = test_tender_cfaua_bids
    test_author = test_tender_below_author
    # Cancellation tender
    test_cancellation_tender_active_tendering = snitch(cancellation_tender_active_tendering)
    test_cancellation_tender_active_pre_qualification = snitch(cancellation_tender_active_pre_qualification)
    test_cancellation_tender_active_pre_qualification_stand_still = snitch(
        cancellation_tender_active_pre_qualification_stand_still
    )
    test_cancellation_tender_active_auction = snitch(cancellation_tender_active_auction)
    test_cancellation_tender_active_qualification = snitch(cancellation_tender_active_qualification)
    test_cancellation_tender_active_qualification_stand_still = snitch(
        cancellation_tender_active_qualification_stand_still
    )
    test_cancellation_tender_active_awarded = snitch(cancellation_tender_active_awarded)
    test_create_cancellation_in_qualification_complaint_period = snitch(
        create_cancellation_in_qualification_complaint_period
    )

    # Cancellation lot
    test_cancel_lot_active_tendering = snitch(cancel_lot_active_tendering)
    test_cancel_lot_active_pre_qualification = snitch(cancel_lot_active_pre_qualification)
    test_cancel_lot_active_pre_qualification_stand_still = snitch(cancel_lot_active_pre_qualification_stand_still)
    test_cancel_lot_active_auction = snitch(cancel_lot_active_auction)
    test_cancel_lot_active_qualification = snitch(cancel_lot_active_qualification)
    test_cancel_lot_active_qualification_stand_still = snitch(cancel_lot_active_qualification_stand_still)
    test_cancel_lot_active_awarded = snitch(cancel_lot_active_awarded)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CancellationTenderAndLotOnAllStage))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
