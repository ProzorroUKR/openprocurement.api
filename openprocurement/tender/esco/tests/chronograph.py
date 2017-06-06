# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    # TenderSwitchUnsuccessfulResourceTest
    switch_to_unsuccessful,
)

from openprocurement.tender.esco.tests.base import BaseESCOEUContentWebTest, test_bids
from openprocurement.tender.openeu.tests.chronograph_blanks import (
    # TenderComplaintSwitchResourceTest
    switch_to_complaint,
    # TenderSwitchAuctionResourceTest
    switch_to_auction,
    # TenderSwitchPreQualificationResourceTest
    pre_qual_switch_to_auction,
)

from openprocurement.tender.openua.tests.chronograph_blanks import (
    # TenderAuctionPeriodResourceTest
    set_auction_period_0bid as set_auction_period,
)


class TenderSwitchPreQualificationResourceTest(BaseESCOEUContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids

    test_switch_to_auction = snitch(pre_qual_switch_to_auction)


class TenderSwitchAuctionResourceTest(BaseESCOEUContentWebTest):
    initial_status = 'active.pre-qualification.stand-still'
    initial_bids = test_bids

    test_switch_to_auction = snitch(switch_to_auction)


class TenderSwitchUnsuccessfulResourceTest(BaseESCOEUContentWebTest):
    initial_status = 'active.tendering'

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderAuctionPeriodResourceTest(BaseESCOEUContentWebTest):
    initial_status = 'active.tendering'

    test_set_auction_period = snitch(set_auction_period)


class TenderComplaintSwitchResourceTest(BaseESCOEUContentWebTest):
    initial_bids = test_bids
    author_data = test_organization

    test_switch_to_complaint = snitch(switch_to_complaint)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderSwitchPreQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderAuctionPeriodResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintSwitchResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
