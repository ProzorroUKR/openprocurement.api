# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_lots,
    test_bids,
    test_organization
)
from openprocurement.tender.cfaselectionua.tests.chronograph_blanks import (
    # TenderSwitchTenderingResourceTest
    switch_to_tendering_by_tenderPeriod_startDate,
    # TenderSwitchQualificationResourceTest
    switch_to_qualification,
    # TenderSwitchAuctionResourceTest
    switch_to_auction,
    # TenderSwitchUnsuccessfulResourceTest
    switch_to_unsuccessful,
    # TenderAuctionPeriodResourceTest
    set_auction_period,
    reset_auction_period,
    # TenderComplaintSwitchResourceTest
    switch_to_ignored_on_complete,
    switch_from_pending_to_ignored,
    switch_from_pending,
    switch_to_complaint,
    # TenderAwardComplaintSwitchResourceTest
    award_switch_to_ignored_on_complete,
    award_switch_from_pending_to_ignored,
    award_switch_from_pending,
    award_switch_to_complaint,
)


class TenderSwitchTenderingResourceTest(TenderContentWebTest):

    initial_status = 'active.enquiries'
    test_switch_to_tendering_by_tenderPeriod_startDate = snitch(switch_to_tendering_by_tenderPeriod_startDate)


class TenderSwitchQualificationResourceTest(TenderContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids[:1]

    test_switch_to_qualification = snitch(switch_to_qualification)


class TenderSwitchAuctionResourceTest(TenderContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids

    test_switch_to_auction = snitch(switch_to_auction)


class TenderSwitchUnsuccessfulResourceTest(TenderContentWebTest):
    initial_status = 'active.tendering'

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderLotSwitchQualificationResourceTest(TenderSwitchQualificationResourceTest):
    initial_lots = test_lots


class TenderLotSwitchAuctionResourceTest(TenderSwitchAuctionResourceTest):
    initial_lots = test_lots


class TenderLotSwitchUnsuccessfulResourceTest(TenderSwitchUnsuccessfulResourceTest):
    initial_lots = test_lots


class TenderAuctionPeriodResourceTest(TenderContentWebTest):
    initial_bids = test_bids

    test_set_auction_period = snitch(set_auction_period)
    test_reset_auction_period = snitch(reset_auction_period)


class TenderLotAuctionPeriodResourceTest(TenderAuctionPeriodResourceTest):
    initial_lots = test_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
