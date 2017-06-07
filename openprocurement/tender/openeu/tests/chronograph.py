# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    # TenderSwitchUnsuccessfulResourceTest
    switch_to_unsuccessful,
)

from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest, test_bids, test_lots
)
from openprocurement.tender.openeu.tests.chronograph_blanks import (
    # TenderComplaintSwitchResourceTest
    switch_to_complaint,
    # TenderSwitchAuctionResourceTest
    switch_to_auction,
    # TenderSwitchPreQualificationResourceTest
    pre_qual_switch_to_auction,
    pre_qual_switch_to_stand_still,
    active_tendering_to_pre_qual,
)

from openprocurement.tender.openua.tests.chronograph_blanks import (
    # TenderAuctionPeriodResourceTest
    set_auction_period_0bid as set_auction_period,
    set_auction_period_lot_0bid as set_auction_period_lot,
)


class TenderSwitchPreQualificationResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.pre-qualification'
    initial_bids = test_bids

    test_switch_to_pre_qual = snitch(active_tendering_to_pre_qual)
    test_switch_to_auction = snitch(pre_qual_switch_to_auction)
    test_switch_to_stand_still = snitch(pre_qual_switch_to_stand_still)


class TenderSwitchAuctionResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.pre-qualification.stand-still'
    initial_bids = test_bids

    test_switch_to_auction = snitch(switch_to_auction)


class TenderSwitchUnsuccessfulResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderLotSwitchPreQualificationResourceTest(TenderSwitchPreQualificationResourceTest):
    initial_lots = test_lots


class TenderLotSwitchAuctionResourceTest(TenderSwitchAuctionResourceTest):
    initial_status = 'active.tendering'
    initial_lots = test_lots
    initial_bids = test_bids


class TenderLotSwitchUnsuccessfulResourceTest(TenderSwitchUnsuccessfulResourceTest):
    initial_status = 'active.tendering'
    initial_lots = test_lots


class TenderAuctionPeriodResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'

    test_set_auction_period = snitch(set_auction_period)


class TenderLotAuctionPeriodResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'
    initial_lots = test_lots

    test_set_auction_period = snitch(set_auction_period_lot)


class TenderComplaintSwitchResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids
    author_data = test_organization

    test_switch_to_complaint = snitch(switch_to_complaint)


class TenderLotComplaintSwitchResourceTest(TenderComplaintSwitchResourceTest):
    initial_lots = test_lots
#
# class TenderLotAwardComplaintSwitchResourceTest(TenderAwardComplaintSwitchResourceTest):
#     initial_lots = test_lots
#
#     def setUp(self):
#         super(TenderAwardComplaintSwitchResourceTest, self).setUp()
#         # Create award
#         response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id), {'data': {
#             'suppliers': [test_organization],
#             'status': 'pending',
#             'bid_id': self.initial_bids[0]['id'],
#             'lotID': self.initial_bids[0]['lotValues'][0]['relatedLot']
#         }})
#         award = response.json['data']
#         self.award_id = award['id']


def suite():
    suite = unittest.TestSuite()
    # suite.addTest(unittest.makeSuite(TenderAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintSwitchResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
