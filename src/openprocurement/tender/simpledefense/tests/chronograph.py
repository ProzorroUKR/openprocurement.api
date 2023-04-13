# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots, test_tender_below_author
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    switch_to_unsuccessful as switch_to_unsuccessful_belowthreshold,
    switch_to_qualification as not_switch_to_unsuccessful,
)

from openprocurement.tender.openua.tests.chronograph_blanks import (
    switch_to_complaint as switch_to_complaint_ua,
    set_auction_period as set_auction_period_ua,
    switch_to_auction_lot as switch_to_auction_lot_ua,
    set_auction_period_lot as set_auction_period_lot_ua,
    switch_to_unsuccessful_lot_0bid as without_bids_switch_to_unsuccessful,
    set_auction_period_lot_0bid as without_bids_set_auction_period,
    set_auction_period_0bid,
)

from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest,
    test_tender_simpledefense_bids,
)
from openprocurement.tender.openuadefense.tests.chronograph_blanks import (
    switch_to_unsuccessful_before_new,
    switch_to_unsuccessful_after_new,
    switch_to_unsuccessful_new,
    switch_to_active_to_unsuccessful,
    switch_to_auction,
    switch_to_unsuccessful_lot_before_new,
    switch_to_unsuccessful_lot_after_new,
    switch_to_unsuccessful_lot_new,
    switch_to_active_to_unsuccessful_lot,
    switch_to_qualification,
)



class TenderSwitch0BidResourceTest(BaseSimpleDefContentWebTest):

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_belowthreshold)

    test_set_auction_period = snitch(set_auction_period_0bid)


class TenderSwitch1BidResourceTest(BaseSimpleDefContentWebTest):
    initial_bids = test_tender_simpledefense_bids[:1]

    test_not_switch_to_unsuccessful = snitch(not_switch_to_unsuccessful)


class TenderSwitchAuctionResourceTest(BaseSimpleDefContentWebTest):
    initial_bids = test_tender_simpledefense_bids
    author_data = test_tender_below_author

    test_switch_to_complaint = snitch(switch_to_complaint_ua)
    test_switch_to_unsuccessful_before_new = snitch(switch_to_unsuccessful_before_new)
    test_switch_to_unsuccessful_after_new = snitch(switch_to_unsuccessful_after_new)
    test_switch_to_unsuccessful_new = snitch(switch_to_unsuccessful_new)
    test_switch_to_active_to_unsuccessful = snitch(switch_to_active_to_unsuccessful)
    test_set_auction_period = snitch(set_auction_period_ua)

    test_switch_to_auction = snitch(switch_to_auction)


class TenderLotSwitch0BidResourceTest(BaseSimpleDefContentWebTest):
    initial_lots = test_tender_below_lots

    test_switch_to_unsuccessful = snitch(without_bids_switch_to_unsuccessful)

    test_set_auction_period = snitch(without_bids_set_auction_period)


class TenderLotSwitch1BidResourceTest(BaseSimpleDefContentWebTest):
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_simpledefense_bids[:1]

    test_switch_to_qualification = snitch(switch_to_qualification)


class TenderLotSwitchAuctionResourceTest(BaseSimpleDefContentWebTest):
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_simpledefense_bids

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
    suite.addTest(unittest.makeSuite(TenderLotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
