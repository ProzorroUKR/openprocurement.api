# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots

from openprocurement.tender.open.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_open_bids,
)
from openprocurement.tender.open.tests.chronograph_blanks import (
    switch_to_complaint,
    switch_to_unsuccessful_lot_0bid,
    set_auction_period_lot_0bid,
    not_switch_to_unsuccessful_lot_1bid,
    not_switch_to_unsuccessful_2lot_1bid,
    switch_to_auction_lot,
    switch_to_unsuccessful_lot,
    set_auction_period_lot,
)


class TenderLotSwitchAuctionResourceTestMixin:
    test_switch_to_complaint = snitch(switch_to_complaint)
    test_switch_to_auction_lot = snitch(switch_to_auction_lot)
    test_switch_to_unsuccessful_lot = snitch(switch_to_unsuccessful_lot)
    test_set_auction_period_lot = snitch(set_auction_period_lot)


class TenderLotSwitch0BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots
    initial_status = "active.tendering"
    test_switch_to_unsuccessful_lot_0bid = snitch(switch_to_unsuccessful_lot_0bid)
    test_set_auction_period_lot_0bid = snitch(set_auction_period_lot_0bid)


class TenderLotSwitch1BidResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_open_bids[:1]
    initial_status = "active.tendering"
    test_not_switch_to_unsuccessful_lot_1bid = snitch(not_switch_to_unsuccessful_lot_1bid)


class TenderLotSwitchAuctionResourceTest(BaseTenderUAContentWebTest, TenderLotSwitchAuctionResourceTestMixin):
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_open_bids


class Tender2LotSwitch0BidResourceTest(TenderLotSwitch0BidResourceTest):
    initial_lots = 2 * test_tender_below_lots


class Tender2LotSwitch1BidResourceTest(TenderLotSwitch1BidResourceTest):
    initial_lots = 2 * test_tender_below_lots

    test_not_switch_to_unsuccessful_lot_1bid = snitch(not_switch_to_unsuccessful_2lot_1bid)


class Tender2LotSwitchAuctionResourceTest(TenderLotSwitchAuctionResourceTest):
    initial_lots = 2 * test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
