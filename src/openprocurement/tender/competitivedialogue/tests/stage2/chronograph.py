# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    # TenderStage2UASwitchAuctionResourceTest
    switch_to_auction as switch_to_auction_ua,
    # TenderStage2UASwitchBidResourceTest
    switch_to_unsuccessful,

)

from openprocurement.tender.openua.tests.chronograph import (
    TenderSwitchAuctionResourceTestMixin,
    TenderLotSwitchAuctionResourceTestMixin
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    # TenderStage2EUAuctionPeriodResourceTest
    set_auction_period_0bid,
    # TenderStage2UALotSwitch1BidResourceTest
    switch_to_unsuccessful_lot_1bid as switch_to_unsuccessful_lot_1_bid_ua,
    # TenderStage2UALotSwitch0BidResourceTest
    set_auction_period_lot_0bid as set_auction_period_lot_0_bid_ua,
    switch_to_unsuccessful_lot_0bid,
)

from openprocurement.tender.openeu.tests.chronograph_blanks import (
    # TenderStage2EUSwitchAuctionResourceTest
    switch_to_auction as switch_to_auction_eu,
    # TenderStage2EUSwitchPreQualificationResourceTest
    pre_qual_switch_to_auction as switch_to_auction_pre_qual,
    # TenderStage2EUComplaintSwitchResourceTest
    switch_to_complaint as switch_to_complaint_eu,

)

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_bids,
    author,
    test_lots
)

from openprocurement.tender.competitivedialogue.tests.stage2.chronograph_blanks import (
    # TenderStage2EUSwitchUnsuccessfulResourceTest
    switch_to_unsuccessful_eu,
    # TenderStage2UA2LotSwitch0BidResourceTest
    set_auction_period_2_lot_0_bid_ua,
)

test_tender_bids = deepcopy(test_bids[:2])
for test_bid in test_tender_bids:
    test_bid['tenderers'] = [author]


class TenderStage2EUSwitchPreQualificationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_tender_bids

    test_switch_to_auction = snitch(switch_to_auction_pre_qual)


class TenderStage2EUSwitchAuctionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.pre-qualification.stand-still'
    initial_bids = test_tender_bids

    test_switch_to_auction = snitch(switch_to_auction_eu)


class TenderStage2EUSwitchUnsuccessfulResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_eu)


class TenderStage2EUAuctionPeriodResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'

    test_set_auction_period = snitch(set_auction_period_0bid)


class TenderStage2EUComplaintSwitchResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_bids = test_tender_bids
    author_data = author  # TODO: change attribute identifier

    test_switch_to_complaint = snitch(switch_to_complaint_eu)


class TenderStage2UASwitch0BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)

    test_set_auction_period = snitch(set_auction_period_0bid)


class TenderStage2UASwitch1BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_bids = test_tender_bids[:1]

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderStage2UASwitchAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderSwitchAuctionResourceTestMixin):
    initial_bids = test_tender_bids
    author_data = author  # TODO: change attribute identifier

    test_switch_to_auction = snitch(switch_to_auction_ua)


class TenderStage2UALotSwitch0BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = test_lots

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_lot_0bid)

    test_set_auction_period = snitch(set_auction_period_lot_0_bid_ua)


class TenderStage2UALotSwitch1BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = test_lots
    initial_bids = test_tender_bids[:1]

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_lot_1_bid_ua)


class TenderStage2UALotSwitchAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest,
                                                 TenderLotSwitchAuctionResourceTestMixin):
    initial_lots = test_lots
    initial_bids = test_tender_bids


class TenderStage2UA2LotSwitch0BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = deepcopy(2 * test_lots)

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_lot_0bid)

    test_set_auction_period = snitch(set_auction_period_2_lot_0_bid_ua)


class TenderStage2UA2LotSwitch1BidResourceTest(TenderStage2UALotSwitch1BidResourceTest):
    initial_lots = deepcopy(2 * test_lots)


class TenderStage2UA2LotSwitchAuctionResourceTest(TenderStage2UALotSwitchAuctionResourceTest):
    initial_lots = deepcopy(2 * test_lots)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUSwitchPreQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAuctionPeriodResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UASwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UASwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UASwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotSwitch1BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UA2LotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UA2LotSwitch0BidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UA2LotSwitchAuctionResourceTest))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
