import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.simpledefense.tests.auction_period_start_date_blanks import (
    tender_collection_put_auction_period_in_active_tendering,
    tender_collection_put_auction_period_in_active_auction,
    tender_put_auction_period_permission_error,
    tender_collection_put_auction_period_for_not_allowed_tender_status,
    tender_lot_put_auction_period_for_not_allowed_tender_status,
    tender_lot_put_auction_period_in_active_tendering,
    tender_lot_put_auction_period_in_active_auction,
    tender_multe_lot_put_auction_period_for_not_allowed_tender_status,
    tender_multe_lot_put_auction_period_in_active_tendering,
    tender_multe_lot_put_auction_period_in_active_auction,
)
from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest, test_lots
)


class TenderAuctionPeriodStartDateResourceTest(BaseSimpleDefContentWebTest):
    days_till_auction_starts = 10
    test_tender_collection_put_auction_period_in_active_tendering = snitch(
        tender_collection_put_auction_period_in_active_tendering)
    test_tender_collection_put_auction_period_in_active_auction = snitch(
        tender_collection_put_auction_period_in_active_auction)
    test_tender_put_auction_period_permission_error = snitch(tender_put_auction_period_permission_error)
    test_tender_collection_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_collection_put_auction_period_for_not_allowed_tender_status)


class TenderLotAuctionPeriodStartDateResourceTest(BaseSimpleDefContentWebTest):
    initial_lots = test_lots
    days_till_auction_starts = 10
    test_tender_lot_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_lot_put_auction_period_for_not_allowed_tender_status)
    test_tender_lot_put_auction_period_in_active_tendering = snitch(
        tender_lot_put_auction_period_in_active_tendering)
    test_tender_lot_put_auction_period_in_active_auction = snitch(
        tender_lot_put_auction_period_in_active_auction)


class TenderMultipleLotAuctionPeriodStartDateResourceTest(BaseSimpleDefContentWebTest):
    days_till_auction_starts = 10
    initial_lots = 2 * test_lots
    test_tender_multe_lot_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_multe_lot_put_auction_period_for_not_allowed_tender_status)
    test_tender_multe_lot_put_auction_period_in_active_tendering = snitch(
        tender_multe_lot_put_auction_period_in_active_tendering)
    test_tender_multe_lot_put_auction_period_in_active_auction = snitch(
        tender_multe_lot_put_auction_period_in_active_auction)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAuctionPeriodStartDateResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAuctionPeriodStartDateResourceTest))
    suite.addTest(unittest.makeSuite(TenderMultipleLotAuctionPeriodStartDateResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
