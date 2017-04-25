# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    # TenderSwitchUnsuccessfulResourceTest
    switch_to_unsuccessful,
)

from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest, test_bids
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


class TenderSwitchPreQualificationResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids

    test_switch_to_auction = snitch(pre_qual_switch_to_auction)


class TenderSwitchAuctionResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.pre-qualification.stand-still'
    initial_bids = test_bids

    test_switch_to_auction = snitch(switch_to_auction)


class TenderSwitchUnsuccessfulResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)

# TODO: check this TestCases
# class TenderLotSwitchQualificationResourceTest(BaseTenderWebTest):
#     initial_status = 'active.tendering'
#     initial_lots = test_lots
#     initial_bids = test_bids[:1]
#
#     def test_switch_to_qualification(self):
#         response = self.set_status('active.auction', {'status': self.initial_status})
#         self.app.authorization = ('Basic', ('chronograph', ''))
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(response.json['data']["status"], "active.qualification")
#         self.assertEqual(len(response.json['data']["awards"]), 1)


# class TenderLotSwitchAuctionResourceTest(BaseTenderWebTest):
#     initial_status = 'active.tendering'
#     initial_lots = test_lots
#     initial_bids = test_bids
#
#     def test_switch_to_auction(self):
#         response = self.set_status('active.auction', {'status': self.initial_status})
#         self.app.authorization = ('Basic', ('chronograph', ''))
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(response.json['data']["status"], "active.auction")


# class TenderLotSwitchUnsuccessfulResourceTest(BaseTenderWebTest):
#     initial_status = 'active.tendering'
#     initial_lots = test_lots
#
#     def test_switch_to_unsuccessful(self):
#         response = self.set_status('active.auction', {'status': self.initial_status})
#         self.app.authorization = ('Basic', ('chronograph', ''))
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(response.json['data']["status"], "unsuccessful")
#         self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(["unsuccessful"]))


class TenderAuctionPeriodResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'

    test_set_auction_period = snitch(set_auction_period)

# TODO: check this TestCase
# class TenderLotAuctionPeriodResourceTest(BaseTenderWebTest):
#     initial_status = 'active.tendering'
#     initial_lots = test_lots
#
#     def test_set_auction_period(self):
#         self.app.authorization = ('Basic', ('chronograph', ''))
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}]}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertEqual(response.json['data']["lots"][0]['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')
#
#         response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"lots": [{"auctionPeriod": {"startDate": None}}]}})
#         self.assertEqual(response.status, '200 OK')
#         self.assertNotIn('auctionPeriod', response.json['data']["lots"][0])


class TenderComplaintSwitchResourceTest(BaseTenderContentWebTest):
    initial_bids = test_bids
    author_data = test_organization

    test_switch_to_complaint = snitch(switch_to_complaint)

# TODO: check this TestCase
# class TenderLotComplaintSwitchResourceTest(TenderComplaintSwitchResourceTest):
#     initial_lots = test_lots
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
    # suite.addTest(unittest.makeSuite(TenderLotComplaintSwitchResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotSwitchQualificationResourceTest))
    # suite.addTest(unittest.makeSuite(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
