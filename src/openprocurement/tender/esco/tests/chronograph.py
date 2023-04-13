# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_author
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    switch_to_unsuccessful,
)

from openprocurement.tender.esco.tests.base import (
    BaseESCOContentWebTest,
    test_tender_esco_bids,
    test_tender_esco_lots,
)
from openprocurement.tender.openeu.tests.chronograph_blanks import (
    switch_to_complaint,
    switch_to_auction,
    pre_qual_switch_to_auction,
    pre_qual_switch_to_stand_still,
    active_tendering_to_pre_qual,
)

from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_0bid as set_auction_period,
    set_auction_period_lot_0bid as set_auction_period_lot,
)


class TenderSwitchPreQualificationResourceTest(BaseESCOContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_esco_bids

    test_switch_to_auction = snitch(pre_qual_switch_to_auction)
    test_switch_to_pre_qual = snitch(active_tendering_to_pre_qual)
    test_switch_to_stand_still = snitch(pre_qual_switch_to_stand_still)


class TenderLotSwitchPreQualificationResourceTest(TenderSwitchPreQualificationResourceTest):
    initial_lots = test_tender_esco_lots


class TenderSwitchAuctionResourceTest(BaseESCOContentWebTest):
    initial_status = "active.pre-qualification.stand-still"
    initial_bids = test_tender_esco_bids

    test_switch_to_auction = snitch(switch_to_auction)


class TenderLotSwitchAuctionResourceTest(TenderSwitchAuctionResourceTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_esco_lots


class TenderSwitchUnsuccessfulResourceTest(BaseESCOContentWebTest):
    initial_status = "active.tendering"

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderLotSwitchUnsuccessfulResourceTest(TenderSwitchUnsuccessfulResourceTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_esco_lots


class TenderAuctionPeriodResourceTest(BaseESCOContentWebTest):
    initial_status = "active.tendering"

    test_set_auction_period = snitch(set_auction_period)


class TenderLotAuctionPeriodResourceTest(BaseESCOContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_esco_lots

    test_set_auction_period = snitch(set_auction_period_lot)


class TenderComplaintSwitchResourceTest(BaseESCOContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_esco_bids
    author_data = test_tender_below_author

    test_switch_to_complaint = snitch(switch_to_complaint)


class TenderLotComplaintSwitchResourceTest(TenderComplaintSwitchResourceTest):
    initial_lots = test_tender_esco_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderSwitchPreQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchPreQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderAuctionPeriodResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAuctionPeriodResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotComplaintSwitchResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
