# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_lots,
    test_bids,
    test_organization
)
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
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
    switch_to_pending,
    switch_to_complaint,
    # TenderAwardComplaintSwitchResourceTest
    award_switch_to_pending,
    award_switch_to_complaint,
)


class TenderSwitchTenderingResourceTest(TenderContentWebTest):
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker

    test_switch_to_tendering_by_tenderPeriod_startDate = snitch(switch_to_tendering_by_tenderPeriod_startDate)


class TenderSwitchQualificationResourceTest(TenderContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids[:1]
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker

    test_switch_to_qualification = snitch(switch_to_qualification)


class TenderSwitchAuctionResourceTest(TenderContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker

    test_switch_to_auction = snitch(switch_to_auction)


class TenderSwitchUnsuccessfulResourceTest(TenderContentWebTest):
    initial_status = 'active.tendering'
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderLotSwitchQualificationResourceTest(TenderSwitchQualificationResourceTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker


class TenderLotSwitchAuctionResourceTest(TenderSwitchAuctionResourceTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker


class TenderLotSwitchUnsuccessfulResourceTest(TenderSwitchUnsuccessfulResourceTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker


class TenderAuctionPeriodResourceTest(TenderContentWebTest):
    initial_bids = test_bids
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker

    test_set_auction_period = snitch(set_auction_period)
    test_reset_auction_period = snitch(reset_auction_period)


class TenderLotAuctionPeriodResourceTest(TenderAuctionPeriodResourceTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker


class TenderComplaintSwitchResourceTest(TenderContentWebTest):
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker

    test_switch_to_pending = snitch(switch_to_pending)
    test_switch_to_complaint = snitch(switch_to_complaint)


class TenderLotComplaintSwitchResourceTest(TenderComplaintSwitchResourceTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker


class TenderAwardComplaintSwitchResourceTest(TenderContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_auth = ('Basic', ('token', ''))  # XXX TODO: broker

    def setUp(self):
        super(TenderAwardComplaintSwitchResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']

    test_award_switch_to_pending = snitch(award_switch_to_pending)
    test_award_switch_to_complaint = snitch(award_switch_to_complaint)


class TenderLotAwardComplaintSwitchResourceTest(TenderAwardComplaintSwitchResourceTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('token', '')) # XXX TODO: broker

    def setUp(self):
        super(TenderAwardComplaintSwitchResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id), {'data': {
            'suppliers': [test_organization],
            'status': 'pending',
            'bid_id': self.initial_bids[0]['id'],
            'lotID': self.initial_bids[0]['lotValues'][0]['relatedLot']
        }})
        award = response.json['data']
        self.award_id = award['id']


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
