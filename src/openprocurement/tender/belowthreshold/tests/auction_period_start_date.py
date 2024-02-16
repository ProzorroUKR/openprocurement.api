import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.auction_period_start_date_blanks import (
    tender_collection_put_auction_period_for_not_allowed_tender_status,
    tender_collection_put_auction_period_in_active_auction,
    tender_collection_put_auction_period_in_active_tendering,
    tender_lot_put_auction_period_for_not_allowed_tender_status,
    tender_lot_put_auction_period_in_active_auction,
    tender_lot_put_auction_period_in_active_tendering,
    tender_put_auction_period_permission_error,
)
from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_lots,
)


class TenderAuctionPeriodStartDateResourceTest(TenderContentWebTest):
    days_till_auction_starts = 10
    test_tender_collection_put_auction_period_in_active_tendering = snitch(
        tender_collection_put_auction_period_in_active_tendering
    )
    test_tender_collection_put_auction_period_in_active_auction = snitch(
        tender_collection_put_auction_period_in_active_auction
    )
    test_tender_put_auction_period_permission_error = snitch(tender_put_auction_period_permission_error)
    test_tender_collection_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_collection_put_auction_period_for_not_allowed_tender_status
    )


class TenderLotAuctionPeriodStartDateResourceTest(TenderContentWebTest):
    initial_lots = test_tender_below_lots
    days_till_auction_starts = 10
    test_tender_lot_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_lot_put_auction_period_for_not_allowed_tender_status
    )
    test_tender_lot_put_auction_period_in_active_tendering = snitch(tender_lot_put_auction_period_in_active_tendering)
    test_tender_lot_put_auction_period_in_active_auction = snitch(tender_lot_put_auction_period_in_active_auction)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAuctionPeriodStartDateResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAuctionPeriodStartDateResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
