# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_author

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
    test_bids,
    test_tender_data_eu,
    test_tender_data_ua,
    test_lots,
)
from openprocurement.tender.belowthreshold.tests.lot import TenderLotResourceTestMixin, TenderLotValueTestMixin
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    # CompetitiveDialogueEULotFeatureResourceTest
    tender_value,
    tender_features_invalid,
    get_tender_lot,
    get_tender_lots,
    create_tender_lot_minimalstep_validation,
    patch_tender_lot_minimalstep_validation,
)
from openprocurement.tender.openua.tests.lot_blanks import (
    # CompetitiveDialogueEULotFeatureBidderResourceTest
    create_tender_bidder_feature,
)
from openprocurement.tender.openeu.tests.lot import TenderLotEdgeCasesTestMixin
from openprocurement.tender.openeu.tests.lot_blanks import (
    # CompetitiveDialogueEULotProcessTest
    one_lot_1bid,
    two_lot_1can,
)
from openprocurement.tender.competitivedialogue.tests.stage1.lot_blanks import (
    # CompetitiveDialogueEU(UA)LotBidderResourceTest
    create_tender_bidder_invalid,
    patch_tender_bidder,
    # CompetitiveDialogueEULotFeatureBidderResourceTest
    create_tender_with_features_bidder_invalid,
    # CompetitiveDialogueEULotProcessTest
    one_lot_0bid,
    one_lot_2bid_1unqualified,
    one_lot_2bid,
    two_lot_2bid_1lot_del,
    one_lot_3bid_1del,
    one_lot_3bid_1un,
    two_lot_0bid,
    two_lot_2can,
    two_lot_2bid_0com_1can,
    two_lot_2bid_2com_2win,
)


class CompetitiveDialogueEULotResourceTest(
    BaseCompetitiveDialogEUContentWebTest, TenderLotResourceTestMixin, TenderLotValueTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_tender_data = test_tender_data_eu  # TODO: change attribute identifier
    test_lots_data = test_lots  # TODO: change attribute identifier

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)


class CompetitiveDialogueEULotEdgeCasesTest(BaseCompetitiveDialogEUContentWebTest, TenderLotEdgeCasesTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_lots * 2
    test_author = test_author

    def setUp(self):
        uniq_bids = [deepcopy(bid) for bid in test_bids]
        for n, bid in enumerate(uniq_bids):
            bid["tenderers"][0]["identifier"]["id"] = "00000{}".format(n)
        self.initial_bids = uniq_bids
        super(CompetitiveDialogueEULotEdgeCasesTest, self).setUp()


class CompetitiveDialogueEULotFeatureResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ("Basic", ("broker", ""))
    test_tender_data = test_tender_data_eu
    invalid_feature_value = 1
    max_feature_value = 0.99
    sum_of_max_value_of_all_features = 0.99

    test_tender_value = snitch(tender_value)
    test_tender_features_invalid = snitch(tender_features_invalid)


class CompetitiveDialogueEULotBidderResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class CompetitiveDialogueEULotFeatureBidderResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_bids  # TODO: change attribute identifier
    test_tender_data = test_tender_data_eu

    def setUp(self):
        super(CompetitiveDialogueEULotFeatureBidderResourceTest, self).setUp()
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

    test_create_tender_bidder_invalid = snitch(create_tender_with_features_bidder_invalid)
    test_create_tender_bidder = snitch(create_tender_bidder_feature)


class CompetitiveDialogueEULotProcessTest(BaseCompetitiveDialogEUContentWebTest):
    test_tender_data = test_tender_data_eu  # TODO: change attribute identifier
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_1lot_0bid = snitch(one_lot_0bid)
    test_1lot_1bid = snitch(one_lot_1bid)
    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1unqualified)
    test_1lot_2bid = snitch(one_lot_2bid)
    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del)
    test_1lot_3bid_1del = snitch(one_lot_3bid_1del)
    test_1lot_3bid_1un = snitch(one_lot_3bid_1un)
    test_2lot_0bid = snitch(two_lot_0bid)
    test_2lot_2can = snitch(two_lot_2can)
    test_2lot_1can = snitch(two_lot_1can)
    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can)
    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win)


class CompetitiveDialogueUALotResourceTest(
    BaseCompetitiveDialogUAContentWebTest, TenderLotResourceTestMixin, TenderLotValueTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_tender_data = test_tender_data_ua  # TODO: change attribute identifier
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_status_that_denies_delete_create_patch_lots = "unsuccessful"

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)


class CompetitiveDialogueUALotEdgeCasesTest(CompetitiveDialogueEULotEdgeCasesTest):
    initial_data = test_tender_data_ua


class CompetitiveDialogueUALotFeatureResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ("Basic", ("broker", ""))
    test_tender_data = test_tender_data_ua
    invalid_feature_value = 1
    max_feature_value = 0.99
    sum_of_max_value_of_all_features = 0.99

    test_tender_value = snitch(tender_value)
    test_tender_features_invalid = snitch(tender_features_invalid)


class CompetitiveDialogueUALotBidderResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class CompetitiveDialogueUALotFeatureBidderResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    test_tender_data = test_tender_data_ua  # TODO: change attribute identifier
    test_bids_data = test_bids  # TODO: change attribute identifier

    def setUp(self):
        super(CompetitiveDialogueUALotFeatureBidderResourceTest, self).setUp()
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

    test_create_tender_bidder_invalid = snitch(create_tender_with_features_bidder_invalid)
    test_create_tender_bidder = snitch(create_tender_bidder_feature)


class CompetitiveDialogueUALotProcessTest(BaseCompetitiveDialogUAContentWebTest):
    test_tender_data = test_tender_data_ua  # TODO: change attribute identifier
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_bids_data = test_bids  # TODO: change attribute identifier

    test_1lot_0bid = snitch(one_lot_0bid)
    test_1lot_1bid = snitch(one_lot_1bid)
    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1unqualified)
    test_1lot_2bid = snitch(one_lot_2bid)
    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del)
    test_1lot_3bid_1del = snitch(one_lot_3bid_1del)
    test_1lot_3bid_1un = snitch(one_lot_3bid_1un)
    test_2lot_0bid = snitch(two_lot_0bid)
    test_2lot_2can = snitch(two_lot_2can)
    test_2lot_1can = snitch(two_lot_1can)
    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can)
    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotBidderResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotFeatureResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotProcessTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotFeatureResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotBidderResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotProcessTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotFeatureBidderResourceTest))

    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
