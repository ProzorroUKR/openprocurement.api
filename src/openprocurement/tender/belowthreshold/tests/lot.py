# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import BaseTenderWebTest, TenderContentWebTest, test_lots
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    # Tender Lot Resouce Test
    create_tender_lot_invalid,
    create_tender_lot,
    patch_tender_lot,
    patch_tender_currency,
    patch_tender_vat,
    get_tender_lot,
    get_tender_lots,
    delete_tender_lot,
    tender_lot_guarantee,
    tender_lot_milestones,
    # Tender Lot Feature Resource Test
    tender_value,
    tender_features_invalid,
    tender_lot_document,
    # Tender Lot Bid Resource Test
    create_tender_bid_invalid,
    patch_tender_bid,
    # Tender Lot Feature Bid Resource Test
    create_tender_bid_invalid_feature,
    create_tender_bid_feature,
    # Tender Lot Process Test
    proc_1lot_0bid,
    proc_1lot_1bid,
    proc_1lot_2bid,
    proc_2lot_0bid,
    proc_2lot_2can,
    proc_2lot_2bid_0com_1can_before_auction,
    proc_2lot_1bid_0com_1can,
    proc_2lot_1bid_2com_1win,
    proc_2lot_1bid_0com_0win,
    proc_2lot_1bid_1com_1win,
    proc_2lot_2bid_2com_2win,
    proc_2lot_1feature_2bid_2com_2win,
    proc_2lot_2diff_bids_check_auction,
    create_tender_lot_minimalstep_validation,
    patch_tender_lot_minimalstep_validation,
)


class TenderLotResourceTestMixin(object):
    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_create_tender_lot = snitch(create_tender_lot)
    test_patch_tender_lot = snitch(patch_tender_lot)
    test_delete_tender_lot = snitch(delete_tender_lot)


class TenderLotValueTestMixin(object):
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_tender_lot_guarantee = snitch(tender_lot_guarantee)
    test_tender_lot_milestones = snitch(tender_lot_milestones)


class TenderLotFeatureResourceTestMixin(object):
    test_tender_value = snitch(tender_value)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_lot_document = snitch(tender_lot_document)


class TenderLotProcessTestMixin(object):
    test_proc_1lot_0bid = snitch(proc_1lot_0bid)
    test_proc_2lot_0bid = snitch(proc_2lot_0bid)
    test_proc_2lot_2can = snitch(proc_2lot_2can)


class TenderLotResourceTest(TenderContentWebTest, TenderLotResourceTestMixin, TenderLotValueTestMixin):
    test_lots_data = test_lots

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)


class TenderLotFeatureResourceTest(TenderContentWebTest, TenderLotFeatureResourceTestMixin):
    initial_lots = 2 * test_lots
    invalid_feature_value = 0.5
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3


class TenderLotBidResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_lots

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_patch_tender_bid = snitch(patch_tender_bid)


class TenderLotFeatureBidResourceTest(TenderContentWebTest):
    initial_lots = test_lots

    def setUp(self):
        super(TenderLotFeatureBidResourceTest, self).setUp()
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
        self.set_status("active.tendering")

    test_create_tender_bid_invalid_feature = snitch(create_tender_bid_invalid_feature)
    test_create_tender_bid_feature = snitch(create_tender_bid_feature)


class TenderLotProcessTest(BaseTenderWebTest, TenderLotProcessTestMixin):
    test_lots_data = test_lots

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
    suite.addTest(unittest.makeSuite(TenderLotResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotBidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotFeatureBidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotProcessTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
