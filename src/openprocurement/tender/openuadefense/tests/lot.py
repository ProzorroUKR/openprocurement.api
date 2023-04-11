# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotResourceTestMixin,
    TenderLotFeatureResourceTestMixin,
    TenderLotProcessTestMixin,
)
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    tender_lot_milestones,
    create_tender_lot_minimalstep_validation,
    patch_tender_lot_minimalstep_validation,
)

from openprocurement.tender.openua.tests.lot import TenderUALotResourceTestMixin, TenderUALotProcessTestMixin
from openprocurement.tender.openua.tests.lot_blanks import (
    patch_tender_bidder,
    create_tender_bidder_feature,
)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openuadefense_data,
    test_tender_openuadefense_bids,
)
from openprocurement.tender.openuadefense.tests.lot_blanks import (
    question_blocking,
    claim_blocking,
    next_check_value_with_unanswered_question,
    next_check_value_with_unanswered_claim,
    one_lot_1bid,
    two_lot_1bid_0com_1can,
    two_lot_1bid_0com_0win,
    two_lot_1bid_1com_1win,
    two_lot_1bid_2com_1win,
    two_lot_2bid_on_first_and_1_on_second_awarding,
)


class TenderLotResourceTest(BaseTenderUAContentWebTest, TenderLotResourceTestMixin, TenderUALotResourceTestMixin):
    docservice = True
    test_lots_data = test_tender_below_lots
    test_tender_lot_milestones = snitch(tender_lot_milestones)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)


class TenderLotEdgeCasesTest(BaseTenderUAContentWebTest):
    docservice = True
    initial_lots = test_tender_below_lots * 2
    initial_bids = test_tender_openuadefense_bids

    test_question_blocking = snitch(question_blocking)
    test_claim_blocking = snitch(claim_blocking)
    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)
    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class TenderLotFeatureResourceTest(BaseTenderUAContentWebTest, TenderLotFeatureResourceTestMixin):
    docservice = True
    initial_data = test_tender_openuadefense_data
    initial_lots = 2 * test_tender_below_lots
    invalid_feature_value = 0.5
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3


class TenderLotBidderResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    # initial_status = 'active.tendering'
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_openuadefense_bids

    # TODO: uncomment when bid activation will be removed
    # test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderLotFeatureBidderResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_openuadefense_bids

    def setUp(self):
        super(TenderLotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]["id"]
        items = deepcopy(self.initial_data["items"])
        items[0]["id"] = "1"
        items[0]["relatedLot"] = self.lot_id
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "items": items,
                    "features": [
                        {
                            "code": "code_item",
                            "featureOf": "item",
                            "relatedItem": "1",
                            "title": "item feature",
                            "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
                        },
                        {
                            "code": "code_lot",
                            "featureOf": "lot",
                            "relatedItem": self.lot_id,
                            "title": "lot feature",
                            "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
                        },
                        {
                            "code": "code_tenderer",
                            "featureOf": "tenderer",
                            "title": "tenderer feature",
                            "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
                        },
                    ],
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["items"][0]["relatedLot"], self.lot_id)

    # test_create_tender_bidder_invalid = snitch(create_tender_bidder_feature_invalid)
    test_create_tender_bidder = snitch(create_tender_bidder_feature)


class TenderLotProcessTest(BaseTenderUAContentWebTest, TenderLotProcessTestMixin, TenderUALotProcessTestMixin):
    docservice = True
    setUp = BaseTenderUAContentWebTest.setUp
    initial_data = test_tender_openuadefense_data
    test_bids_data = test_tender_openuadefense_bids

    days_till_auction_starts = 6

    test_lots_data = test_tender_below_lots  # TODO: change attribute identifier
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


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
