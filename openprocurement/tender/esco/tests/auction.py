# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.auction import (
    TenderAuctionResourceTestMixin,
    TenderLotAuctionResourceTestMixin,
    TenderMultipleLotAuctionResourceTestMixin
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    # TenderSameValueAuctionResourceTest
    post_tender_auction_reversed,
    post_tender_auction_not_changed,
)

from openprocurement.tender.openeu.tests.auction_blanks import (
    # TenderMultipleLotAuctionResourceTest
    patch_tender_2lot_auction,
)

from openprocurement.tender.esco.tests.base import (
    BaseESCOContentWebTest,
    test_features_tender_data,
    test_bids,
    test_lots,
)

from openprocurement.tender.esco.tests.auction_blanks import (
    # TenderAuctionResourceTest
    get_tender_auction,
    post_tender_auction,
    # TenderLotAuctionResourceTest
    get_tender_lot_auction,
    post_tender_lot_auction,
    # TenderMultipleLotAuctionResourceTest
    get_tender_lots_auction,
    post_tender_lots_auction,
    # TenderAuctionNBUdiscountRateTest
    auction_check_NBUdiscountRate,
    # TenderFeaturesAuctionResourceTest
    get_tender_auction_feature,
)


class TenderAuctionResourceTest(BaseESCOContentWebTest, TenderAuctionResourceTestMixin):
    #initial_data = tender_data
    initial_auth = ('Basic', ('broker', ''))
    initial_bids = test_bids
    initial_bids[1]['value'] = {'yearlyPaymentsPercentage': 0.9,
                                'annualCostsReduction': [100] * 21,
                                'contractDuration': {'years': 10, 'days': 10}}

    def setUp(self):
        super(TenderAuctionResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        for qualific in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualific['id'], self.tender_token), {'data': {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        # # switch to active.pre-qualification.stand-still

    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)


class TenderSameValueAuctionResourceTest(BaseESCOContentWebTest):

    initial_status = 'active.auction'
    tenderer_info = deepcopy(test_bids[0]['tenderers'])
    initial_bids = [
        {
            "tenderers": tenderer_info,
            "value": {
                'yearlyPaymentsPercentage': 0.9,
                'annualCostsReduction': [751.5] * 21,
                'contractDuration': {'years': 10, 'days': 10}
            },
            'selfQualified': True,
            'selfEligible': True
        }
        for i in range(3)
    ]

    def setUp(self):
        super(TenderSameValueAuctionResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        for qualific in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(
                self.tender_id, qualific['id']), {'data': {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status('active.auction', {'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.auction")
        # self.app.authorization = ('Basic', ('token', ''))

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderAuctionNBUdiscountRateTest(BaseESCOContentWebTest):
    #initial_data = tender_data
    initial_auth = ('Basic', ('broker', ''))
    initial_bids = test_bids

    def setUp(self):
        super(TenderAuctionNBUdiscountRateTest, self).setUp()
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        for qualific in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualific['id'], self.tender_token), {'data': {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        # # switch to active.pre-qualification.stand-still

    test_auction_check_NBUdiscountRate = snitch(auction_check_NBUdiscountRate)


class TenderLotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = test_lots
    # initial_data = test_tender_data
    test_get_tender_auction = snitch(get_tender_lot_auction)
    test_post_tender_auction = snitch(post_tender_lot_auction)


class TenderMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = 2 * test_lots

    test_get_tender_auction = snitch(get_tender_lots_auction)
    test_patch_tender_auction = snitch(patch_tender_2lot_auction)
    test_post_tender_auction = snitch(post_tender_lots_auction)


class TenderFeaturesAuctionResourceTest(BaseESCOContentWebTest):
    initial_data = test_features_tender_data
    initial_status = 'active.auction'
    tenderer_info = deepcopy(test_bids[0]['tenderers'])
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in test_features_tender_data['features']
            ],
            "tenderers": tenderer_info,
            "value": {
                'yearlyPaymentsPercentage': 0.9,
                'annualCostsReduction': [751.5] * 21,
                'contractDuration': {'years': 10}
            },
            'selfQualified': True,
            'selfEligible': True
        },
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15,
                }
                for i in test_features_tender_data['features']
            ],
            "tenderers": tenderer_info,
            "value": {
                'yearlyPaymentsPercentage': 0.9,
                'annualCostsReduction': [785.5] * 21,
                'contractDuration': {'years': 10}
            },
            'selfQualified': True,
            'selfEligible': True
        }
    ]

    test_get_tender_auction = snitch(get_tender_auction_feature)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderAuctionNBUdiscountRateTest))
    suite.addTest(unittest.makeSuite(TenderLotAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderMultipleLotAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFeaturesAuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
