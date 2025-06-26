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
    tender_lot_guarantee,
    tender_lot_milestones,
)
from openprocurement.tender.competitiveordering.tests.short.base import (
    BaseTenderCOShortContentWebTest,
    test_tender_co_short_bids,
    test_tender_co_short_criteria,
    test_tender_co_short_data,
    test_tender_co_short_features_data,
)
from openprocurement.tender.open.tests.lot_blanks import (
    claim_blocking,
    create_tender_bidder_feature,
    create_tender_bidder_feature_invalid,
    create_tender_bidder_invalid,
    get_tender_lot,
    get_tender_lots,
    lots_features_delete,
    next_check_value_with_unanswered_claim,
    patch_tender_bidder,
    patch_tender_currency,
    patch_tender_vat,
    proc_1lot_1bid,
    proc_1lot_1bid_patch,
    proc_1lot_2bid,
    proc_1lot_3bid_1un,
    proc_2lot_1bid_0com_0win,
    proc_2lot_1bid_0com_1can,
    proc_2lot_1bid_1com_1win,
    proc_2lot_1bid_2com_1win,
    proc_2lot_2bid_1claim_1com_1win,
    proc_2lot_2bid_1lot_del,
    proc_2lot_2bid_2com_2win,
)


class TenderCOLotResourceTestMixin:
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)


class TenderCOLotProcessTestMixin:
    test_proc_1lot_1bid_patch = snitch(proc_1lot_1bid_patch)
    test_proc_1lot_2bid = snitch(proc_1lot_2bid)
    test_proc_1lot_3bid_1un = snitch(proc_1lot_3bid_1un)
    test_proc_2lot_2bid_2com_2win = snitch(proc_2lot_2bid_2com_2win)


class TenderLotResourceTest(BaseTenderCOShortContentWebTest, TenderLotResourceTestMixin, TenderCOLotResourceTestMixin):
    initial_data = test_tender_co_short_data
    initial_lots = test_tender_below_lots
    initial_criteria = test_tender_co_short_criteria

    test_lots_data = test_tender_below_lots

    test_tender_lot_guarantee = snitch(tender_lot_guarantee)
    test_tender_lot_milestones = snitch(tender_lot_milestones)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)


class TenderLotEdgeCasesTest(BaseTenderCOShortContentWebTest):
    initial_data = test_tender_co_short_data
    initial_lots = test_tender_below_lots * 2
    initial_bids = test_tender_co_short_bids

    test_claim_blocking = snitch(claim_blocking)
    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class TenderLotFeatureResourceTest(BaseTenderCOShortContentWebTest, TenderLotFeatureResourceTestMixin):
    initial_data = test_tender_co_short_data
    initial_lots = 2 * test_tender_below_lots
    test_bids_data = test_tender_co_short_bids
    initial_criteria = test_tender_co_short_criteria
    invalid_feature_value = 0.5
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3


class TenderLotBidderResourceTest(BaseTenderCOShortContentWebTest):
    initial_data = test_tender_co_short_data
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_co_short_bids
    initial_criteria = test_tender_co_short_criteria

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderLotFeatureBidderResourceTest(BaseTenderCOShortContentWebTest):
    initial_data = test_tender_co_short_data
    initial_lots = test_tender_below_lots
    test_bids_data = test_tender_co_short_bids
    initial_criteria = test_tender_co_short_criteria

    def setUp(self):
        super().setUp()
        self.lot_id = self.initial_lots[0]["id"]
        items = [deepcopy(self.initial_data["items"][0])]
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

    test_create_tender_bidder_feature_invalid = snitch(create_tender_bidder_feature_invalid)
    test_create_tender_bidder_feature = snitch(create_tender_bidder_feature)


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
    get_now() + timedelta(days=1),
)
@mock.patch(
    "openprocurement.tender.competitiveordering.procedure.state.award.NEW_ARTICLE_17_CRITERIA_REQUIRED",
    get_now() + timedelta(days=1),
)
class TenderLotProcessTest(BaseTenderCOShortContentWebTest, TenderLotProcessTestMixin, TenderCOLotProcessTestMixin):
    initial_data = test_tender_co_short_data

    test_bids_data = test_tender_co_short_bids
    test_lots_data = test_tender_below_lots
    test_features_tender_data = test_tender_co_short_features_data
    setUp = BaseTenderCOShortContentWebTest.setUp

    days_till_auction_starts = 16

    test_proc_1lot_1bid = snitch(proc_1lot_1bid)
    test_proc_2lot_1bid_0com_1can = snitch(proc_2lot_1bid_0com_1can)
    test_proc_2lot_2bid_1lot_del = snitch(proc_2lot_2bid_1lot_del)
    test_proc_2lot_1bid_2com_1win = snitch(proc_2lot_1bid_2com_1win)
    test_proc_2lot_1bid_0com_0win = snitch(proc_2lot_1bid_0com_0win)
    test_proc_2lot_1bid_1com_1win = snitch(proc_2lot_1bid_1com_1win)
    test_lots_features_delete = snitch(lots_features_delete)
    test_proc_2lot_2bid_1claim_1com_1win = snitch(proc_2lot_2bid_1claim_1com_1win)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotFeatureBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotProcessTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
