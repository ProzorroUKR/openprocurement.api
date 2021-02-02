# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots, test_author
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    # TenderSwitchAuctionResourceTest
    switch_to_auction,
    # TenderSwitch0BidResourceTest
    switch_to_unsuccessful as switch_to_unsuccessful_0bid,
)

from openprocurement.tender.openua.tests.base import test_bids, BaseTenderUAContentWebTest
from openprocurement.tender.openua.tests.chronograph_blanks import (
    # TenderSwitch0BidResourceTest
    set_auction_period_0bid,
    # TenderSwitch1BidResourceTest
    switch_to_unsuccessful_1bid,
    # TenderSwitchAuctionResourceTest
    switch_to_complaint,
    switch_to_unsuccessful,
    set_auction_period,
    # TenderLotSwitch0BidResourceTest
    switch_to_unsuccessful_lot_0bid,
    set_auction_period_lot_0bid,
    # TenderLotSwitch1BidResourceTest
    switch_to_unsuccessful_lot_1bid,
    # TenderLotSwitchAuctionResourceTest
    switch_to_auction_lot,
    switch_to_unsuccessful_lot,
    set_auction_period_lot,
)


class TenderSwitchAuctionResourceTestMixin(object):
    test_switch_to_complaint = snitch(switch_to_complaint)
    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)
    test_set_auction_period = snitch(set_auction_period)


class TenderLotSwitchAuctionResourceTestMixin(object):
    test_switch_to_auction_lot = snitch(switch_to_auction_lot)
    test_switch_to_unsuccessful_lot = snitch(switch_to_unsuccessful_lot)
    test_set_auction_period_lot = snitch(set_auction_period_lot)


class TenderSwitch0BidResourceTest(BaseTenderUAContentWebTest):

    test_switch_to_unsuccessful_0bid = snitch(switch_to_unsuccessful_0bid)
    test_set_auction_period_0bid = snitch(set_auction_period_0bid)


class TenderSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_bids = test_bids[:1]

    test_switch_to_unsuccessful_1bid = snitch(switch_to_unsuccessful_1bid)


class TenderSwitchAuctionResourceTest(BaseTenderUAContentWebTest, TenderSwitchAuctionResourceTestMixin):
    initial_bids = test_bids
    author_data = test_author

    test_switch_to_auction = snitch(switch_to_auction)


class TenderLotSwitch0BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots

    test_switch_to_unsuccessful_lot_0bid = snitch(switch_to_unsuccessful_lot_0bid)
    test_set_auction_period_lot_0bid = snitch(set_auction_period_lot_0bid)


class TenderLotSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots
    initial_bids = test_bids[:1]

    test_switch_to_unsuccessful_lot_1bid = snitch(switch_to_unsuccessful_lot_1bid)


class TenderLotSwitchAuctionResourceTest(BaseTenderUAContentWebTest, TenderLotSwitchAuctionResourceTestMixin):
    initial_lots = test_lots
    initial_bids = test_bids


class Tender2LotSwitch0BidResourceTest(TenderLotSwitch0BidResourceTest):
    initial_lots = 2 * test_lots


class Tender2LotSwitch1BidResourceTest(TenderLotSwitch1BidResourceTest):
    initial_lots = 2 * test_lots


class Tender2LotSwitchAuctionResourceTest(TenderLotSwitchAuctionResourceTest):
    initial_lots = 2 * test_lots


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
