# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_lots,
    test_tender_below_author,
)
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    switch_to_auction,
    switch_to_unsuccessful as switch_to_unsuccessful_0bid,
)

from openprocurement.tender.openua.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openua_bids,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_0bid,
    switch_to_unsuccessful_1bid,
    switch_to_complaint,
    switch_to_unsuccessful,
    set_auction_period,
    switch_to_unsuccessful_lot_0bid,
    set_auction_period_lot_0bid,
    switch_to_unsuccessful_lot_1bid,
    switch_to_auction_lot,
    switch_to_unsuccessful_lot,
    set_auction_period_lot,
)


class TenderSwitchAuctionResourceTestMixin:
    test_switch_to_complaint = snitch(switch_to_complaint)
    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)
    test_set_auction_period = snitch(set_auction_period)


class TenderLotSwitchAuctionResourceTestMixin:
    test_switch_to_auction_lot = snitch(switch_to_auction_lot)
    test_switch_to_unsuccessful_lot = snitch(switch_to_unsuccessful_lot)
    test_set_auction_period_lot = snitch(set_auction_period_lot)


class TenderSwitch0BidResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.tendering"
    test_switch_to_unsuccessful_0bid = snitch(switch_to_unsuccessful_0bid)
    test_set_auction_period_0bid = snitch(set_auction_period_0bid)


class TenderSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_bids = test_tender_openua_bids[:1]
    initial_status = "active.tendering"
    test_switch_to_unsuccessful_1bid = snitch(switch_to_unsuccessful_1bid)


class TenderSwitchAuctionResourceTest(BaseTenderUAContentWebTest, TenderSwitchAuctionResourceTestMixin):
    initial_bids = test_tender_openua_bids
    author_data = test_tender_below_author
    initial_status = "active.tendering"
    test_switch_to_auction = snitch(switch_to_auction)


class TenderLotSwitch0BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots
    initial_status = "active.tendering"
    test_switch_to_unsuccessful_lot_0bid = snitch(switch_to_unsuccessful_lot_0bid)
    test_set_auction_period_lot_0bid = snitch(set_auction_period_lot_0bid)


class TenderLotSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_openua_bids[:1]
    initial_status = "active.tendering"
    test_switch_to_unsuccessful_lot_1bid = snitch(switch_to_unsuccessful_lot_1bid)


class TenderLotSwitchAuctionResourceTest(BaseTenderUAContentWebTest, TenderLotSwitchAuctionResourceTestMixin):
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_openua_bids


class Tender2LotSwitch0BidResourceTest(TenderLotSwitch0BidResourceTest):
    initial_lots = 2 * test_tender_below_lots


class Tender2LotSwitch1BidResourceTest(TenderLotSwitch1BidResourceTest):
    initial_lots = 2 * test_tender_below_lots


class Tender2LotSwitchAuctionResourceTest(TenderLotSwitchAuctionResourceTest):
    initial_lots = 2 * test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
