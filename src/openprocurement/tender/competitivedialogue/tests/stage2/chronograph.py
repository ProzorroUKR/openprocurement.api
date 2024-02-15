# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    switch_to_auction as switch_to_auction_ua,  # TenderStage2UASwitchAuctionResourceTest; TenderStage2UASwitchBidResourceTest
)
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    switch_to_unsuccessful,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cd_author,
    test_tender_cd_lots,
    test_tender_cd_tenderer,
    test_tender_openeu_bids,
)
from openprocurement.tender.competitivedialogue.tests.stage2.chronograph_blanks import (  # TenderStage2EUSwitchUnsuccessfulResourceTest; TenderStage2UA2LotSwitch0BidResourceTest
    set_auction_period_2_lot_0_bid_ua,
    switch_to_unsuccessful_eu,
)
from openprocurement.tender.openeu.tests.chronograph_blanks import (
    pre_qual_switch_to_auction as switch_to_auction_pre_qual,
)
from openprocurement.tender.openeu.tests.chronograph_blanks import (
    switch_to_auction as switch_to_auction_eu,  # TenderStage2EUSwitchAuctionResourceTest; TenderStage2EUSwitchPreQualificationResourceTest; TenderStage2EUComplaintSwitchResourceTest
)
from openprocurement.tender.openeu.tests.chronograph_blanks import (
    switch_to_complaint as switch_to_complaint_eu,
)
from openprocurement.tender.openua.tests.chronograph import (
    TenderLotSwitchAuctionResourceTestMixin,
    TenderSwitchAuctionResourceTestMixin,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_0bid,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_lot_0bid as set_auction_period_lot_0_bid_ua,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    switch_to_unsuccessful_lot_0bid,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    switch_to_unsuccessful_lot_1bid as switch_to_unsuccessful_lot_1_bid_ua,  # TenderStage2EUAuctionPeriodResourceTest; TenderStage2UALotSwitch1BidResourceTest; TenderStage2UALotSwitch0BidResourceTest
)

test_tender_bids = deepcopy(test_tender_openeu_bids[:2])
for test_bid in test_tender_bids:
    test_bid["tenderers"] = [test_tender_cd_tenderer]


class TenderStage2EUSwitchPreQualificationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots

    test_switch_to_auction = snitch(switch_to_auction_pre_qual)


class TenderStage2EUSwitchAuctionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.pre-qualification.stand-still"
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots

    test_switch_to_auction = snitch(switch_to_auction_eu)


class TenderStage2EUSwitchUnsuccessfulResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_eu)


class TenderStage2EUComplaintSwitchResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_bids
    author_data = test_tender_cd_author  # TODO: change attribute identifier
    initial_lots = test_tender_cd_lots

    test_switch_to_complaint = snitch(switch_to_complaint_eu)


class TenderStage2UASwitch0BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots
    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderStage2UASwitch1BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_bids[:1]
    initial_lots = test_tender_cd_lots

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderStage2UASwitchAuctionResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest, TenderSwitchAuctionResourceTestMixin
):
    initial_status = "active.tendering"
    initial_bids = test_tender_bids
    author_data = test_tender_cd_author  # TODO: change attribute identifier
    initial_lots = test_tender_cd_lots

    test_switch_to_auction = snitch(switch_to_auction_ua)


class TenderStage2UALotSwitch0BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_lot_0bid)

    test_set_auction_period = snitch(set_auction_period_lot_0_bid_ua)


class TenderStage2UALotSwitch1BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots
    initial_bids = test_tender_bids[:1]

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_lot_1_bid_ua)


class TenderStage2UALotSwitchAuctionResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest, TenderLotSwitchAuctionResourceTestMixin
):
    initial_status = "active.tendering"
    initial_lots = test_tender_cd_lots
    initial_bids = test_tender_bids


class TenderStage2UA2LotSwitch0BidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_lots = deepcopy(2 * test_tender_cd_lots)

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful_lot_0bid)

    test_set_auction_period = snitch(set_auction_period_2_lot_0_bid_ua)


class TenderStage2UA2LotSwitch1BidResourceTest(TenderStage2UALotSwitch1BidResourceTest):
    initial_lots = deepcopy(2 * test_tender_cd_lots)


class TenderStage2UA2LotSwitchAuctionResourceTest(TenderStage2UALotSwitchAuctionResourceTest):
    initial_lots = deepcopy(2 * test_tender_cd_lots)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUSwitchPreQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUSwitchUnsuccessfulResourceTest))
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


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
