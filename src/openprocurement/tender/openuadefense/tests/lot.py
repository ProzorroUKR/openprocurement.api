import unittest
from copy import deepcopy
from datetime import timedelta
from unittest import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotFeatureResourceTestMixin,
    TenderLotProcessTestMixin,
    TenderLotResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    create_tender_lot_minimalstep_validation,
    patch_tender_lot_minimalstep_validation,
    tender_lot_milestones,
)
from openprocurement.tender.openua.tests.lot import (
    TenderUALotProcessTestMixin,
    TenderUALotResourceTestMixin,
)
from openprocurement.tender.openua.tests.lot_blanks import (
    claim_blocking,
    create_tender_bidder_feature,
    next_check_value_with_unanswered_claim,
    patch_tender_bidder,
)
from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openuadefense_bids,
    test_tender_openuadefense_data,
)
from openprocurement.tender.openuadefense.tests.lot_blanks import (
    next_check_value_with_unanswered_question,
    one_lot_1bid,
    question_blocking,
    two_lot_1bid_0com_0win,
    two_lot_1bid_0com_1can,
    two_lot_1bid_1com_1win,
    two_lot_1bid_2com_1win,
    two_lot_2bid_on_first_and_1_on_second_awarding,
)


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
    get_now() + timedelta(days=1),
)
class TenderLotResourceTest(BaseTenderUAContentWebTest, TenderLotResourceTestMixin, TenderUALotResourceTestMixin):
    test_lots_data = test_tender_below_lots
    test_tender_lot_milestones = snitch(tender_lot_milestones)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)


class TenderLotEdgeCasesTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots * 2
    initial_bids = test_tender_openuadefense_bids

    test_question_blocking = snitch(question_blocking)
    test_claim_blocking = snitch(claim_blocking)
    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)
    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class TenderLotFeatureResourceTest(BaseTenderUAContentWebTest, TenderLotFeatureResourceTestMixin):
    initial_data = test_tender_openuadefense_data
    initial_lots = 2 * test_tender_below_lots
    invalid_feature_value = 0.5
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3


class TenderLotBidderResourceTest(BaseTenderUAContentWebTest):
    # initial_status = 'active.tendering'
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_openuadefense_bids

    # TODO: uncomment when bid activation will be removed
    # test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderLotFeatureBidderResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_openuadefense_bids

    def setUp(self):
        super().setUp()
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


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
    get_now() + timedelta(days=1),
)
class TenderLotProcessTest(BaseTenderUAContentWebTest, TenderLotProcessTestMixin, TenderUALotProcessTestMixin):
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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotFeatureBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotProcessTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
