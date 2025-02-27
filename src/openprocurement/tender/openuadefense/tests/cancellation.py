import unittest
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.constants_env import RELEASE_2020_04_19
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
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (  # TenderCancellationResourceTest; TenderLotCancellationResourceTest; TenderLotsCancellationResourceTest
    create_tender_cancellation,
    create_tender_lot_cancellation,
    create_tender_lots_cancellation,
    patch_tender_cancellation,
    patch_tender_lot_cancellation,
    patch_tender_lots_cancellation,
)
from openprocurement.tender.openua.tests.cancellation import (
    TenderCancellationComplaintResourceTestMixin,
    TenderCancellationResourceNewReleaseTestMixin,
)
from openprocurement.tender.openua.tests.cancellation_blanks import (
    access_create_tender_cancellation_complaint,
    activate_cancellation,
    create_tender_cancellation_with_cancellation_lots,
)
from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openuadefense_bids,
)


class TenderCancellationResourceTest(
    BaseTenderUAContentWebTest, TenderCancellationResourceTestMixin, TenderCancellationResourceNewReleaseTestMixin
):
    valid_reasonType_choices = ["noDemand", "unFixable", "expensesCut"]

    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_activate_cancellation = snitch(activate_cancellation)


class TenderLotCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_tender_below_lots

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)
    test_create_tender_cancellation_with_cancellation_lots = snitch(create_tender_cancellation_with_cancellation_lots)


class TenderCancellationComplaintResourceTest(BaseTenderUAContentWebTest, TenderCancellationComplaintResourceTestMixin):
    initial_bids = test_tender_openuadefense_bids

    @patch("openprocurement.tender.core.procedure.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
    def setUp(self):
        super().setUp()
        # Create cancellation

        self.set_complaint_period_end()

        test_tender_below_cancellation.update({"reasonType": "noDemand"})
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": test_tender_below_cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]

    test_access_create_tender_cancellation_complaint = snitch(access_create_tender_cancellation_complaint)


class TenderCancellationDocumentResourceTest(BaseTenderUAContentWebTest, TenderCancellationDocumentResourceTestMixin):
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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
