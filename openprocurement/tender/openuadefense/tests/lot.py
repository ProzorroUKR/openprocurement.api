# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotResourceTestMixin,
    TenderLotFeatureResourceTestMixin,
    TenderLotProcessTestMixin
)

from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.openua.tests.lot import (
    TenderUALotResourceTestMixin,
    TenderUALotProcessTestMixin
)
from openprocurement.tender.openua.tests.lot_blanks import (
    # TenderLotFeatureResourceTest
    create_tender_bidder_invalid,
    patch_tender_bidder,
    # TenderLotFeatureBidderResourceTest
    create_tender_bidder_feature_invalid,
    create_tender_bidder_feature,
)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_data
)
from openprocurement.tender.openuadefense.tests.lot_blanks import (
    # TenderLotEdgeCasesTest
    question_blocking,
    claim_blocking,
    next_check_value_with_unanswered_question,
    next_check_value_with_unanswered_claim,
    # TenderLotProcessTest
    one_lot_1bid,
    two_lot_1bid_0com_1can,
    two_lot_1bid_0com_0win,
    two_lot_1bid_1com_1win,
    two_lot_1bid_2com_1win,
    two_lot_2bid_on_first_and_1_on_second_awarding,
)


class TenderLotResourceTest(BaseTenderUAContentWebTest, TenderLotResourceTestMixin, TenderUALotResourceTestMixin):
    test_lots_data = test_lots  # TODO: change attribute identifier


class TenderLotEdgeCasesTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots * 2
    initial_bids = test_bids

    test_question_blocking = snitch(question_blocking)
    test_claim_blocking = snitch(claim_blocking)
    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)
    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class TenderLotFeatureResourceTest(BaseTenderUAContentWebTest, TenderLotFeatureResourceTestMixin):
    initial_data = test_tender_data
    initial_lots = 2 * test_lots
    invalid_feature_value = 0.5
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3


class TenderLotBidderResourceTest(BaseTenderUAContentWebTest):
    # initial_status = 'active.tendering'
    initial_lots = test_lots

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderLotFeatureBidderResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots

    def setUp(self):
        super(TenderLotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {
            "items": [
                {
                    'relatedLot': self.lot_id,
                    'id': '1'
                }
            ],
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": "1",
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": self.lot_id,
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['items'][0]['relatedLot'], self.lot_id)

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_feature_invalid)
    test_create_tender_bidder = snitch(create_tender_bidder_feature)


class TenderLotProcessTest(BaseTenderUAContentWebTest, TenderLotProcessTestMixin, TenderUALotProcessTestMixin):
    setUp = BaseTenderUAContentWebTest.setUp
    initial_data = test_tender_data

    days_till_auction_starts = 6

    test_lots_data = test_lots  # TODO: change attribute identifier
    test_1lot_1bid = snitch(one_lot_1bid)
    test_2lot_1bid_0com_1can = snitch(two_lot_1bid_0com_1can)
    test_2lot_1bid_2com_1win = snitch(two_lot_1bid_2com_1win)
    test_2lot_1bid_0com_0win = snitch(two_lot_1bid_0com_0win)
    test_2lot_1bid_1com_1win = snitch(two_lot_1bid_1com_1win)
    test_2lot_2bid_on_first_and_1_on_second_awarding = snitch(two_lot_2bid_on_first_and_1_on_second_awarding)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotProcessTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
