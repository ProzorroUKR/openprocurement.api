# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    # TenderSwitch0BidResourceTest
    switch_to_unsuccessful,
)

from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.openua.tests.chronograph_blanks import (
    # TenderSwitch0BidResourceTest
    set_auction_period_0bid,
    switch_to_unsuccessful as auction_switch_to_unsuccessful,
    set_auction_period as auction_set_auction_period,
    switch_to_complaint,
    switch_to_auction_lot as with_lot_switch_to_auction,
    switch_to_unsuccessful_lot as with_lot_switch_to_unsuccessful,
    set_auction_period_lot as with_lot_set_auction_period,

)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest
)
from openprocurement.tender.openuadefense.tests.chronograph_blanks import (
    # TenderSwitch1BidResourceTest
    not_switch_to_unsuccessful,
    # TenderSwitchAuctionResourceTest
    switch_to_auction,
    # TenderLotSwitch0BidResourceTest
    without_bids_switch_to_unsuccessful,
    without_bids_set_auction_period,
    # TenderLotSwitch1BidResourceTest
    switch_to_qualification,
    # TenderLotSwitchAuctionResourceTest

)


class TenderSwitch0BidResourceTest(BaseTenderUAContentWebTest):

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)

    test_set_auction_period = snitch(set_auction_period_0bid)


class TenderSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_bids = test_bids[:1]

    test_not_switch_to_unsuccessful = snitch(not_switch_to_unsuccessful)


class TenderSwitchAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_bids = test_bids

    test_switch_to_auction = snitch(switch_to_auction)

    test_switch_to_complaint = snitch(switch_to_complaint)

    test_switch_to_unsuccessful = snitch(auction_switch_to_unsuccessful)

    test_set_auction_period = snitch(auction_set_auction_period)


class TenderLotSwitch0BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots

    test_switch_to_unsuccessful = snitch(without_bids_switch_to_unsuccessful)

    test_set_auction_period = snitch(without_bids_set_auction_period)


class TenderLotSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots
    initial_bids = test_bids[:1]

    test_switch_to_qualification = snitch(switch_to_qualification)


class TenderLotSwitchAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots
    initial_bids = test_bids

    test_switch_to_auction = snitch(with_lot_switch_to_auction)

    test_switch_to_unsuccessful = snitch(with_lot_switch_to_unsuccessful)

    test_set_auction_period = snitch(with_lot_set_auction_period)


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


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
