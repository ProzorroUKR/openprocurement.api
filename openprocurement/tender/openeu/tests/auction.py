# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_organization,
    test_lots
)
from openprocurement.tender.belowthreshold.tests.auction import (
    TenderAuctionResourceTestMixin,
    TenderLotAuctionResourceTestMixin,
    TenderMultipleLotAuctionResourceTestMixin
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    # TenderSameValueAuctionResourceTest
    post_tender_auction_reversed,
    post_tender_auction_not_changed,
    # TenderFeaturesAuctionResourceTest
    get_tender_auction_feature,
)

from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_features_tender_data,
    test_bids
)
from openprocurement.tender.openeu.tests.auction_blanks import (
    # TenderMultipleLotAuctionResourceTest
    patch_tender_2lot_auction,
)


class TenderAuctionResourceTest(BaseTenderContentWebTest, TenderAuctionResourceTestMixin):
    #initial_data = tender_data
    initial_auth = ('Basic', ('broker', ''))
    initial_bids = test_bids

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


class TenderSameValueAuctionResourceTest(BaseTenderContentWebTest):

    initial_status = 'active.auction'
    tenderer_info = deepcopy(test_organization)
    initial_bids = [
        {
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        }
        for i in range(3)
    ]

    def setUp(self):
        super(TenderSameValueAuctionResourceTest, self).setUp()
        auth = self.app.authorization
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")
        self.app.authorization = auth

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
        self.app.authorization = auth

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderLotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = test_lots
    # initial_data = test_tender_data


class TenderMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = 2 * test_lots

    test_patch_tender_auction = snitch(patch_tender_2lot_auction)


class TenderFeaturesAuctionResourceTest(BaseTenderContentWebTest):
    initial_data = test_features_tender_data
    initial_status = 'active.auction'
    tenderer_info = deepcopy(test_organization)
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in test_features_tender_data['features']
            ],
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
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
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
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
    suite.addTest(unittest.makeSuite(TenderFeaturesAuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
