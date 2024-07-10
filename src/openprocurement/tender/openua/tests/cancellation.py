import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationDocumentResourceTestMixin,
    TenderCancellationResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    create_tender_lot_cancellation,
    create_tender_lots_cancellation,
    patch_tender_lot_cancellation,
)
from openprocurement.tender.open.tests.cancellation_blanks import (
    create_tender_lots_cancellation_complaint,
)
from openprocurement.tender.openua.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openua_bids,
)
from openprocurement.tender.openua.tests.cancellation_blanks import (
    access_create_tender_cancellation_complaint,
    activate_cancellation,
    bot_patch_tender_cancellation_complaint,
    cancellation_active_award,
    cancellation_unsuccessful_award,
    create_cancellation_in_award_complaint_period,
    create_cancellation_with_award_complaint,
    create_cancellation_with_tender_complaint,
    create_lot_cancellation_with_tender_cancellation,
    create_tender_cancellation,
    create_tender_cancellation_2020_04_19,
    create_tender_cancellation_before_19_04_2020,
    create_tender_cancellation_complaint,
    create_tender_cancellation_with_cancellation_lots,
    get_tender_cancellation_complaints,
    patch_tender_cancellation,
    patch_tender_cancellation_2020_04_19,
    patch_tender_cancellation_2020_04_19_to_pending,
    patch_tender_cancellation_before_19_04_2020,
    patch_tender_cancellation_complaint,
    permission_cancellation_pending,
)


class TenderCancellationComplaintResourceTestMixin:
    test_create_tender_cancellation_complaint = snitch(create_tender_cancellation_complaint)
    test_patch_tender_cancellation_complaint = snitch(patch_tender_cancellation_complaint)
    test_get_tender_cancellation_complaints = snitch(get_tender_cancellation_complaints)
    test_bot_patch_tender_cancellation_complaint = snitch(bot_patch_tender_cancellation_complaint)


class TenderCancellationResourceNewReleaseTestMixin:
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    test_create_tender_cancellation_before_19_04_2020 = snitch(create_tender_cancellation_before_19_04_2020)
    test_patch_tender_cancellation_before_19_04_2020 = snitch(patch_tender_cancellation_before_19_04_2020)
    test_create_tender_cancellation_2020_04_19 = snitch(create_tender_cancellation_2020_04_19)
    test_patch_tender_cancellation_2020_04_19 = snitch(patch_tender_cancellation_2020_04_19)
    test_patch_tender_cancellation_2020_04_19_to_pending = snitch(patch_tender_cancellation_2020_04_19_to_pending)
    test_permission_cancellation_pending = snitch(permission_cancellation_pending)
    test_create_cancellation_with_tender_complaint = snitch(create_cancellation_with_tender_complaint)


class TenderAwardsCancellationResourceTestMixin:
    test_create_cancellation_in_award_complaint_period = snitch(create_cancellation_in_award_complaint_period)
    test_create_cancellation_with_award_complaint = snitch(create_cancellation_with_award_complaint)


class TenderCancellationResourceTest(
    BaseTenderUAContentWebTest, TenderCancellationResourceTestMixin, TenderCancellationResourceNewReleaseTestMixin
):
    initial_status = "active.tendering"
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_activate_cancellation = snitch(activate_cancellation)


class TenderLotCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots

    test_create_tender_lot_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_lot_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_tender_below_lots

    test_create_tender_lots_cancellation = snitch(create_tender_lots_cancellation)
    test_create_tender_cancellation_with_cancellation_lots = snitch(create_tender_cancellation_with_cancellation_lots)
    test_create_lot_cancellation_with_tender_cancellation = snitch(create_lot_cancellation_with_tender_cancellation)
    test_create_tender_lots_cancellation_complaint = snitch(create_tender_lots_cancellation_complaint)
    # test_patch_tender_lots_cancellation = snitch(patch_tender_lots_cancellation)


class TenderAwardsCancellationResourceTest(BaseTenderUAContentWebTest, TenderAwardsCancellationResourceTestMixin):
    initial_lots = 2 * test_tender_below_lots
    initial_status = "active.auction"
    initial_bids = test_tender_openua_bids

    test_cancellation_active_award = snitch(cancellation_active_award)
    test_cancellation_unsuccessful_award = snitch(cancellation_unsuccessful_award)


class TenderCancellationComplaintResourceTest(BaseTenderUAContentWebTest, TenderCancellationComplaintResourceTestMixin):
    initial_bids = test_tender_openua_bids

    @patch("openprocurement.tender.core.procedure.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
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

    test_access_create_tender_cancellation_complaint = snitch(
        access_create_tender_cancellation_complaint,
    )


class TenderCancellationDocumentResourceTest(BaseTenderUAContentWebTest, TenderCancellationDocumentResourceTestMixin):
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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
