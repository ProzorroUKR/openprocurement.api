# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_lots
)
from openprocurement.tender.openua.tests.base import (
    test_bids, BaseTenderUAContentWebTest, test_tender_data
)
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    # TenderLotResourceTest
    create_tender_lot,
    delete_tender_lot,
    create_tender_lot_invalid,
    tender_lot_guarantee,
    # TenderLotFeatureResourceTest
    tender_value,
    tender_features_invalid,
    tender_lot_document,
    # TenderLotProcessTest
    proc_1lot_0bid,
    proc_2lot_0bid,
    proc_2lot_2can
)
from openprocurement.tender.openua.tests.lot_blanks import (
    # TenderLotResourceTest
    patch_tender_lot,
    patch_tender_currency,
    patch_tender_vat,
    get_tender_lot,
    get_tender_lots,
    # TenderLotEdgeCasesTest
    question_blocking,
    claim_blocking,
    next_check_value_with_unanswered_question,
    next_check_value_with_unanswered_claim,
    # TenderLotBidderResourceTest
    create_tender_bidder_invalid,
    patch_tender_bidder,
    # TenderLotFeatureBidderResourceTest
    create_tender_bidder_feature_invalid,
    create_tender_bidder_feature,
    # TenderLotProcessTest
    proc_1lot_1bid,
    proc_1lot_1bid_patch,
    proc_1lot_2bid,
    proc_1lot_3bid_1un,
    proc_2lot_1bid_0com_1can,
    proc_2lot_2bid_1lot_del,
    proc_2lot_1bid_2com_1win,
    proc_2lot_1bid_0com_0win,
    proc_2lot_1bid_1com_1win,
    proc_2lot_2bid_2com_2win,
)


class TenderLotResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    test_lots_data = test_lots
    test_status_that_denies_delete_create_lots = 'active.auction'

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_create_tender_lot = snitch(create_tender_lot)
    test_patch_tender_lot = snitch(patch_tender_lot)
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_delete_tender_lot = snitch(delete_tender_lot)
    test_tender_lot_guarantee = snitch(tender_lot_guarantee)



class TenderLotEdgeCasesTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    initial_lots = test_lots * 2
    initial_bids = test_bids

    test_question_blocking = snitch(question_blocking)
    test_claim_blocking = snitch(claim_blocking)
    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)
    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class TenderLotFeatureResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    initial_lots = 2 * test_lots

    test_tender_value = snitch(tender_value)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_lot_document = snitch(tender_lot_document)


class TenderLotBidderResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    initial_lots = test_lots

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderLotFeatureBidderResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    initial_lots = test_lots

    def setUp(self):
        super(TenderLotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {
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

    test_create_tender_bidder_feature_invalid = snitch(create_tender_bidder_feature_invalid)
    test_create_tender_bidder_feature = snitch(create_tender_bidder_feature)


class TenderLotProcessTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    test_lots_data = test_lots
    setUp = BaseTenderUAContentWebTest.setUp

    days_till_auction_starts = 16

    test_proc_1lot_0bid = snitch(proc_1lot_0bid)
    test_proc_1lot_1bid = snitch(proc_1lot_1bid)
    test_proc_1lot_1bid_patch = snitch(proc_1lot_1bid_patch)
    test_proc_1lot_2bid = snitch(proc_1lot_2bid)
    test_proc_1lot_3bid_1un = snitch(proc_1lot_3bid_1un)
    test_proc_2lot_0bid = snitch(proc_2lot_0bid)
    test_proc_2lot_2can = snitch(proc_2lot_2can)
    test_proc_2lot_1bid_0com_1can = snitch(proc_2lot_1bid_0com_1can)
    test_proc_2lot_2bid_1lot_del = snitch(proc_2lot_2bid_1lot_del)
    test_proc_2lot_1bid_2com_1win = snitch(proc_2lot_1bid_2com_1win)
    test_proc_2lot_1bid_0com_0win = snitch(proc_2lot_1bid_0com_0win)
    test_proc_2lot_1bid_1com_1win = snitch(proc_2lot_1bid_1com_1win)
    test_proc_2lot_2bid_2com_2win = snitch(proc_2lot_2bid_2com_2win)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotProcessTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
