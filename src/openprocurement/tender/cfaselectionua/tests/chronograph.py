# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import reset_auction_period, set_auction_period

from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_tender_cfaselectionua_lots,
    test_tender_cfaselectionua_bids,
)
from openprocurement.tender.cfaselectionua.tests.chronograph_blanks import (
    switch_to_tendering,
    switch_to_tendering_by_tender_period_start_date,
    switch_to_qualification,
    switch_to_auction,
    switch_to_unsuccessful,
)


class TenderSwitchTenderingPeriodStartDateResourceTest(TenderContentWebTest):
    initial_lots = test_tender_cfaselectionua_lots
    initial_status = "active.enquiries"
    test_switch_to_tendering_by_tenderPeriod_startDate = snitch(switch_to_tendering_by_tender_period_start_date)


class TenderSwitchTenderingResourceTest(TenderContentWebTest):
    initial_lots = test_tender_cfaselectionua_lots
    test_switch_to_tendering = snitch(switch_to_tendering)


class TenderLotSwitchQualificationResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_cfaselectionua_bids[:1]
    initial_lots = test_tender_cfaselectionua_lots

    test_switch_to_qualification = snitch(switch_to_qualification)


class TenderLotSwitchAuctionResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots

    test_switch_to_auction = snitch(switch_to_auction)


class TenderLotSwitchUnsuccessfulResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_cfaselectionua_lots

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderLotAuctionPeriodResourceTest(TenderContentWebTest):
    initial_lots = test_tender_cfaselectionua_lots
    initial_bids = test_tender_cfaselectionua_bids

    test_set_auction_period = snitch(set_auction_period)
    test_reset_auction_period = snitch(reset_auction_period)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderSwitchTenderingPeriodStartDateResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchTenderingResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAuctionPeriodResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
