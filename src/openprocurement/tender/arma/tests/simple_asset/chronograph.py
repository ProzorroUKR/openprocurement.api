import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.arma.tests.simple_asset.base import (
    BaseTenderSimpleAssetContentWebTest,
    test_tender_arma_simple_lots,
)
from openprocurement.tender.open.tests.above_threshold_ua.chronograph_blanks import (
    set_auction_period_0bid as set_auction_period,
)
from openprocurement.tender.open.tests.above_threshold_ua.chronograph_blanks import (
    set_auction_period_lot_0bid as set_auction_period_lot,
)
from openprocurement.tender.open.tests.below_threshold.chronograph_blanks import (
    switch_to_unsuccessful,
)


class TenderSwitchUnsuccessfulResourceTest(BaseTenderSimpleAssetContentWebTest):
    initial_status = "active.tendering"

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderLotSwitchUnsuccessfulResourceTest(TenderSwitchUnsuccessfulResourceTest):
    initial_lots = test_tender_arma_simple_lots


class TenderAuctionPeriodResourceTest(BaseTenderSimpleAssetContentWebTest):
    initial_status = "active.tendering"

    test_set_auction_period = snitch(set_auction_period)


class TenderLotAuctionPeriodResourceTest(BaseTenderSimpleAssetContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_arma_simple_lots

    test_set_auction_period = snitch(set_auction_period_lot)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAuctionPeriodResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAuctionPeriodResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
