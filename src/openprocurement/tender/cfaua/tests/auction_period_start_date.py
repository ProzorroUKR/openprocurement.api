import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.cfaua.tests.auction_period_start_date_blanks import (
    tender_lot_put_auction_period_in_active_tendering,
    tender_lot_put_auction_period_success_in_active_auction_status,
    tender_lot_put_auction_period_for_not_allowed_tender_status,
    tender_collection_put_auction_period,
    tender_lot_put_auction_period_in_active_pre_qualification,
)
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest, test_lots
)


class TenderLotAuctionPeriodStartDateResourceTest(BaseTenderContentWebTest):
    initial_lots = test_lots
    days_till_auction_starts = 10
    test_tender_lot_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_lot_put_auction_period_for_not_allowed_tender_status
    )
    test_tender_lot_put_auction_period_in_active_tendering = snitch(
        tender_lot_put_auction_period_in_active_tendering
    )
    test_tender_lot_put_auction_period_success_in_active_status = snitch(
        tender_lot_put_auction_period_success_in_active_auction_status
    )
    test_tender_collection_put_auction_period = snitch(
        tender_collection_put_auction_period
    )
    test_tender_lot_put_auction_period_in_active_pre_qualification = snitch(
        tender_lot_put_auction_period_in_active_pre_qualification
    )



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotAuctionPeriodStartDateResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
