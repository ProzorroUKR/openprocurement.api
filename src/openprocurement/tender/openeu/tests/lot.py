# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotResourceTestMixin,
    TenderLotValueTestMixin,
    TenderLotFeatureResourceTestMixin,
    TenderLotProcessTestMixin,
)

from openprocurement.tender.belowthreshold.tests.base import test_author
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    patch_tender_lot_minimalstep_validation,
    create_tender_lot_minimalstep_validation,
)

from openprocurement.tender.openua.tests.lot_blanks import (
    # TenderLotResourceTest
    get_tender_lot,
    get_tender_lots,
)

from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest, test_tender_data, test_lots, test_bids
from openprocurement.tender.openeu.tests.lot_blanks import (
    # TenderLotProcessTest
    one_lot_1bid,
    one_lot_2bid_1unqualified,
    one_lot_2bid,
    two_lot_2bid_1lot_del,
    one_lot_3bid_1del,
    one_lot_3bid_1un,
    two_lot_1can,
    two_lot_2bid_0com_1can,
    two_lot_2bid_2com_2win,
    two_lot_3bid_1win_bug,
    # TenderLotFeatureBidderResourceTest
    create_tender_feature_bidder_invalid,
    create_tender_feature_bidder,
    # TenderLotBidderResourceTest
    create_tender_bidder_invalid,
    patch_tender_bidder,
    # TenderLotEdgeCasesTest
    question_blocking,
    claim_blocking,
    next_check_value_with_unanswered_question,
    next_check_value_with_unanswered_claim,
)


class TenderLotEdgeCasesTestMixin(object):

    test_question_blocking = snitch(question_blocking)
    test_claim_blocking = snitch(claim_blocking)
    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)
    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class TenderLotResourceTest(BaseTenderContentWebTest, TenderLotResourceTestMixin, TenderLotValueTestMixin):

    initial_auth = ("Basic", ("broker", ""))
    test_lots_data = test_lots  # TODO: change attribute identifier
    initial_data = test_tender_data

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)


class TenderLotEdgeCasesTest(BaseTenderContentWebTest, TenderLotEdgeCasesTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_lots * 2
    initial_bids = test_bids
    test_author = test_author


class TenderLotFeatureResourceTest(BaseTenderContentWebTest, TenderLotFeatureResourceTestMixin):
    initial_lots = 2 * test_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_data
    invalid_feature_value = 0.4
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3


class TenderLotBidderResourceTest(BaseTenderContentWebTest):
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderLotFeatureBidderResourceTest(BaseTenderContentWebTest):
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_data
    test_bids_data = test_bids  # TODO: change attribute identifier

    def setUp(self):
        super(TenderLotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]["id"]
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "items": [{"relatedLot": self.lot_id, "id": "1"}],
                    "features": [
                        {
                            "code": "code_item",
                            "featureOf": "item",
                            "relatedItem": "1",
                            "title": u"item feature",
                            "enum": [{"value": 0.01, "title": u"good"}, {"value": 0.02, "title": u"best"}],
                        },
                        {
                            "code": "code_lot",
                            "featureOf": "lot",
                            "relatedItem": self.lot_id,
                            "title": u"lot feature",
                            "enum": [{"value": 0.01, "title": u"good"}, {"value": 0.02, "title": u"best"}],
                        },
                        {
                            "code": "code_tenderer",
                            "featureOf": "tenderer",
                            "title": u"tenderer feature",
                            "enum": [{"value": 0.01, "title": u"good"}, {"value": 0.02, "title": u"best"}],
                        },
                    ],
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["items"][0]["relatedLot"], self.lot_id)

    test_create_tender_bidder_invalid = snitch(create_tender_feature_bidder_invalid)
    test_create_tender_bidder = snitch(create_tender_feature_bidder)


class TenderLotProcessTest(BaseTenderContentWebTest, TenderLotProcessTestMixin):
    setUp = BaseTenderContentWebTest.setUp
    test_lots_data = test_lots  # TODO: change attribute identifier
    initial_data = test_tender_data
    test_bids_data = test_bids  # TODO: change attribute identifier

    days_till_auction_starts = 16

    test_1lot_1bid = snitch(one_lot_1bid)
    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1unqualified)
    test_1lot_2bid = snitch(one_lot_2bid)
    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del)
    test_1lot_3bid_1del = snitch(one_lot_3bid_1del)
    test_1lot_3bid_1un = snitch(one_lot_3bid_1un)
    test_2lot_1can = snitch(two_lot_1can)
    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can)
    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win)
    test_2lot_3bid_1win_bug = snitch(two_lot_3bid_1win_bug)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotProcessTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
