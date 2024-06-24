import unittest
from copy import deepcopy
from datetime import timedelta
from unittest import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest,
    TenderContentWebTest,
    test_tender_below_bids,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    create_tender_bid_feature,
    create_tender_bid_invalid,
    create_tender_bid_invalid_feature,
    create_tender_lot,
    create_tender_lot_invalid,
    create_tender_lot_minimalstep_validation,
    delete_tender_lot,
    get_tender_lot,
    get_tender_lots,
    patch_tender_bid,
    patch_tender_currency,
    patch_tender_lot,
    patch_tender_lot_minimalstep_validation,
    patch_tender_vat,
    proc_1lot_0bid,
    proc_1lot_1bid,
    proc_1lot_2bid,
    proc_2lot_0bid,
    proc_2lot_1bid_0com_0win,
    proc_2lot_1bid_0com_1can,
    proc_2lot_1bid_1com_1win,
    proc_2lot_1bid_2com_1win,
    proc_2lot_1feature_2bid_2com_2win,
    proc_2lot_2bid_0com_1can_before_auction,
    proc_2lot_2bid_2com_2win,
    proc_2lot_2can,
    proc_2lot_2diff_bids_check_auction,
    tender_features_invalid,
    tender_lot_document,
    tender_lot_guarantee,
    tender_lot_milestones,
    tender_value,
)


class TenderLotResourceTestMixin:
    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_create_tender_lot = snitch(create_tender_lot)
    test_patch_tender_lot = snitch(patch_tender_lot)
    test_delete_tender_lot = snitch(delete_tender_lot)


class TenderLotValueTestMixin:
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_tender_lot_guarantee = snitch(tender_lot_guarantee)
    test_tender_lot_milestones = snitch(tender_lot_milestones)


class TenderLotFeatureResourceTestMixin:
    test_tender_value = snitch(tender_value)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_lot_document = snitch(tender_lot_document)


class TenderLotProcessTestMixin:
    test_proc_1lot_0bid = snitch(proc_1lot_0bid)
    test_proc_2lot_0bid = snitch(proc_2lot_0bid)
    test_proc_2lot_2can = snitch(proc_2lot_2can)


class TenderLotResourceTest(TenderContentWebTest, TenderLotResourceTestMixin, TenderLotValueTestMixin):
    docservice = True
    initial_lots = test_lots_data = test_tender_below_lots

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)


class TenderLotFeatureResourceTest(TenderContentWebTest, TenderLotFeatureResourceTestMixin):
    docservice = True
    initial_status = None
    initial_lots = 2 * test_tender_below_lots
    invalid_feature_value = 0.5
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3


class TenderLotBidResourceTest(TenderContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_patch_tender_bid = snitch(patch_tender_bid)


class TenderLotFeatureBidResourceTest(TenderContentWebTest):
    docservice = True
    initial_lots = test_tender_below_lots

    def setUp(self):
        super().setUp()
        self.lot_id = self.initial_lots[0]["id"]
        items = deepcopy(self.initial_data["items"])
        items[0]["relatedLot"] = self.lot_id
        items[0]["id"] = "1"
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
        self.set_status("active.tendering")

    test_create_tender_bid_invalid_feature = snitch(create_tender_bid_invalid_feature)
    test_create_tender_bid_feature = snitch(create_tender_bid_feature)


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
    get_now() + timedelta(days=1),
)
class TenderLotProcessTest(BaseTenderWebTest, TenderLotProcessTestMixin):
    docservice = True
    test_lots_data = test_tender_below_lots

    days_till_auction_starts = 10

    test_proc_1lot_1bid = snitch(proc_1lot_1bid)
    test_proc_1lot_2bid = snitch(proc_1lot_2bid)
    test_proc_2lot_2bid_0com_1can_before_auction = snitch(proc_2lot_2bid_0com_1can_before_auction)
    test_proc_2lot_1bid_0com_1can = snitch(proc_2lot_1bid_0com_1can)
    test_proc_2lot_1bid_2com_1win = snitch(proc_2lot_1bid_2com_1win)
    test_proc_2lot_1bid_0com_0win = snitch(proc_2lot_1bid_0com_0win)
    test_proc_2lot_1bid_1com_1win = snitch(proc_2lot_1bid_1com_1win)
    test_proc_2lot_2bid_2com_2win = snitch(proc_2lot_2bid_2com_2win)
    test_proc_2lot_1feature_2bid_2com_2win = snitch(proc_2lot_1feature_2bid_2com_2win)
    test_proc_2lot_2diff_bids_check_auction = snitch(proc_2lot_2diff_bids_check_auction)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotFeatureBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotProcessTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
