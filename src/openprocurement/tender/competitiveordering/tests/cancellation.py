import unittest

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
from openprocurement.tender.competitiveordering.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_co_bids,
    test_tender_co_config,
    test_tender_co_data,
)
from openprocurement.tender.competitiveordering.tests.cancellation_blanks import (
    create_tender_co_lot_cancellation_complaint,
    patch_tender_co_lot_cancellation,
)
from openprocurement.tender.open.tests.cancellation_blanks import (
    activate_cancellation,
    cancellation_active_award,
    cancellation_lot_during_qualification_after_first_winner_chosen,
    cancellation_lot_during_qualification_before_winner_chosen,
    cancellation_unsuccessful_award,
    create_cancellation_in_award_complaint_period,
    create_lot_cancellation_with_tender_cancellation,
    create_tender_cancellation,
    create_tender_cancellation_2020_04_19,
    create_tender_cancellation_before_19_04_2020,
    create_tender_cancellation_with_cancellation_lots,
    patch_tender_cancellation,
    patch_tender_cancellation_2020_04_19,
    patch_tender_cancellation_2020_04_19_to_pending,
    patch_tender_cancellation_before_19_04_2020,
)


class TenderCancellationResourceNewReleaseTestMixin:
    valid_reasonType_choices = ["noDemand", "unFixable", "forceMajeure", "expensesCut", "noOffer"]

    test_create_tender_cancellation_before_19_04_2020 = snitch(create_tender_cancellation_before_19_04_2020)
    test_patch_tender_cancellation_before_19_04_2020 = snitch(patch_tender_cancellation_before_19_04_2020)
    test_create_tender_cancellation_2020_04_19 = snitch(create_tender_cancellation_2020_04_19)
    test_patch_tender_cancellation_2020_04_19 = snitch(patch_tender_cancellation_2020_04_19)
    test_patch_tender_cancellation_2020_04_19_to_pending = snitch(patch_tender_cancellation_2020_04_19_to_pending)


class TenderAwardsCancellationResourceTestMixin:
    test_create_cancellation_in_award_complaint_period = snitch(create_cancellation_in_award_complaint_period)


class TenderCancellationResourceTest(
    BaseTenderUAContentWebTest, TenderCancellationResourceTestMixin, TenderCancellationResourceNewReleaseTestMixin
):
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots
    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_activate_cancellation = snitch(activate_cancellation)


class TenderLotCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots

    test_create_tender_lot_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_lot_cancellation = snitch(patch_tender_lot_cancellation)


class TenderCOLotCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots
    initial_data = test_tender_co_data
    initial_config = test_tender_co_config

    test_tender_lot_cancellation_complaint = snitch(create_tender_co_lot_cancellation_complaint)
    test_patch_tender_lot_cancellation = snitch(patch_tender_co_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_tender_below_lots

    test_create_tender_lots_cancellation = snitch(create_tender_lots_cancellation)
    test_create_tender_cancellation_with_cancellation_lots = snitch(create_tender_cancellation_with_cancellation_lots)
    test_create_lot_cancellation_with_tender_cancellation = snitch(create_lot_cancellation_with_tender_cancellation)


class TenderAwardsCancellationResourceTest(BaseTenderUAContentWebTest, TenderAwardsCancellationResourceTestMixin):
    initial_lots = 2 * test_tender_below_lots
    initial_status = "active.auction"
    initial_bids = test_tender_co_bids

    test_cancellation_active_award = snitch(cancellation_active_award)
    test_cancellation_unsuccessful_award = snitch(cancellation_unsuccessful_award)


class TenderLotsCancellationQualificationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_tender_below_lots
    initial_status = "active.auction"
    initial_bids = test_tender_co_bids

    test_cancellation_lot_during_qualification_after_first_winner_chosen = snitch(
        cancellation_lot_during_qualification_after_first_winner_chosen
    )
    test_cancellation_lot_during_qualification_before_winner_chosen = snitch(
        cancellation_lot_during_qualification_before_winner_chosen
    )


class TenderCancellationDocumentResourceTest(BaseTenderUAContentWebTest, TenderCancellationDocumentResourceTestMixin):
    initial_lots = test_tender_below_lots

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
