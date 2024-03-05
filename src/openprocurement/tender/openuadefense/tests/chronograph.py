import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    switch_to_qualification as not_switch_to_unsuccessful,
)
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    switch_to_unsuccessful as switch_to_unsuccessful_belowthreshold,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_0bid,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_lot as set_auction_period_lot_ua,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_lot_0bid as without_bids_set_auction_period,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    switch_to_auction_lot as switch_to_auction_lot_ua,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    switch_to_unsuccessful_lot_0bid as without_bids_switch_to_unsuccessful,
)
from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openuadefense_bids,
)
from openprocurement.tender.openuadefense.tests.chronograph_blanks import (
    switch_to_active_to_unsuccessful,
    switch_to_active_to_unsuccessful_lot,
    switch_to_auction,
    switch_to_qualification,
    switch_to_unsuccessful_after_new,
    switch_to_unsuccessful_before_new,
    switch_to_unsuccessful_lot_after_new,
    switch_to_unsuccessful_lot_before_new,
    switch_to_unsuccessful_lot_new,
    switch_to_unsuccessful_new,
)


class TenderSwitch0BidResourceTest(BaseTenderUAContentWebTest):
    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_belowthreshold)

    test_set_auction_period = snitch(set_auction_period_0bid)


class TenderSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_bids = test_tender_openuadefense_bids[:1]

    test_not_switch_to_unsuccessful = snitch(not_switch_to_unsuccessful)


class TenderSwitchAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_bids = test_tender_openuadefense_bids
    author_data = test_tender_below_author

    test_switch_to_unsuccessful_before_new = snitch(switch_to_unsuccessful_before_new)
    test_switch_to_unsuccessful_after_new = snitch(switch_to_unsuccessful_after_new)
    test_switch_to_unsuccessful_new = snitch(switch_to_unsuccessful_new)
    test_switch_to_active_to_unsuccessful = snitch(switch_to_active_to_unsuccessful)

    test_switch_to_auction = snitch(switch_to_auction)


class TenderLotSwitch0BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots

    test_switch_to_unsuccessful = snitch(without_bids_switch_to_unsuccessful)

    test_set_auction_period = snitch(without_bids_set_auction_period)


class TenderLotSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_openuadefense_bids[:1]

    test_switch_to_qualification = snitch(switch_to_qualification)


class TenderLotSwitchAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_openuadefense_bids

    test_switch_to_auction_lot = snitch(switch_to_auction_lot_ua)
    test_switch_to_unsuccessful_lot_before_new = snitch(switch_to_unsuccessful_lot_before_new)
    test_switch_to_unsuccessful_lot_after_new = snitch(switch_to_unsuccessful_lot_after_new)
    test_switch_to_unsuccessful_lot_new = snitch(switch_to_unsuccessful_lot_new)
    test_switch_to_active_to_unsuccessful_lot = snitch(switch_to_active_to_unsuccessful_lot)
    test_set_auction_period_lot = snitch(set_auction_period_lot_ua)


class Tender2LotSwitch0BidResourceTest(TenderLotSwitch0BidResourceTest):
    initial_lots = 2 * test_tender_below_lots


class Tender2LotSwitch1BidResourceTest(TenderLotSwitch1BidResourceTest):
    initial_lots = 2 * test_tender_below_lots


class Tender2LotSwitchAuctionResourceTest(TenderLotSwitchAuctionResourceTest):
    initial_lots = 2 * test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotSwitch0BidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotSwitch1BidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitch0BidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitch1BidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitchAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
