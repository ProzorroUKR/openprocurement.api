import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_author
from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotResourceTestMixin,
    TenderLotValueTestMixin,
)
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    create_tender_lot_minimalstep_validation,
    get_tender_lot,
    get_tender_lots,
    patch_tender_lot_minimalstep_validation,
    tender_features_invalid,
    tender_value,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUContentWebTest,
    BaseCompetitiveDialogUAContentWebTest,
    test_tender_cd_lots,
    test_tender_cd_stage1_bids,
    test_tender_cdeu_data,
    test_tender_cdua_config,
    test_tender_cdua_data,
)
from openprocurement.tender.competitivedialogue.tests.stage1.lot_blanks import (
    create_tender_bidder_invalid,
    create_tender_with_features_bidder_invalid,
    one_lot_0bid,
    one_lot_2bid,
    one_lot_2bid_1unqualified,
    one_lot_3bid_1del,
    one_lot_3bid_1un,
    patch_tender_bidder,
    two_lot_0bid,
    two_lot_2bid_0com_1can,
    two_lot_2bid_1lot_del,
    two_lot_2bid_2com_2win,
    two_lot_2can,
)
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.tender.openeu.tests.lot import TenderLotEdgeCasesTestMixin


class CompetitiveDialogueEULotResourceTest(
    BaseCompetitiveDialogEUContentWebTest, TenderLotResourceTestMixin, TenderLotValueTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_cdeu_data
    initial_lots = test_lots_data = test_tender_cd_lots  # TODO: change attribute identifier
    initial_criteria = test_exclusion_criteria + test_language_criteria

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)


class CompetitiveDialogueEULotEdgeCasesTest(BaseCompetitiveDialogEUContentWebTest, TenderLotEdgeCasesTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_cd_lots * 2
    test_author = test_tender_below_author

    def setUp(self):
        uniq_bids = [deepcopy(bid) for bid in test_tender_cd_stage1_bids]
        for n, bid in enumerate(uniq_bids):
            bid["tenderers"][0]["identifier"]["id"] = "00000{}".format(n)
        self.initial_bids = uniq_bids
        super().setUp()


class CompetitiveDialogueEULotFeatureResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_cdeu_data
    invalid_feature_value = 1
    max_feature_value = 0.99
    sum_of_max_value_of_all_features = 0.99
    initial_criteria = test_exclusion_criteria + test_language_criteria

    test_tender_value = snitch(tender_value)
    test_tender_features_invalid = snitch(tender_features_invalid)


class CompetitiveDialogueEULotBidderResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_cd_stage1_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class CompetitiveDialogueEULotProcessTest(BaseCompetitiveDialogEUContentWebTest):
    initial_data = test_tender_cdeu_data
    initial_lots = test_lots_data = test_tender_cd_lots  # TODO: change attribute identifier
    initial_bids = test_bids_data = test_tender_cd_stage1_bids  # TODO: change attribute identifier

    test_1lot_0bid = snitch(one_lot_0bid)
    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1unqualified)
    test_1lot_2bid = snitch(one_lot_2bid)
    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del)
    test_1lot_3bid_1del = snitch(one_lot_3bid_1del)
    test_1lot_3bid_1un = snitch(one_lot_3bid_1un)
    test_2lot_0bid = snitch(two_lot_0bid)
    test_2lot_2can = snitch(two_lot_2can)
    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can)
    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win)


class CompetitiveDialogueUALotResourceTest(
    BaseCompetitiveDialogUAContentWebTest, TenderLotResourceTestMixin, TenderLotValueTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_cdua_data
    initial_lots = test_lots_data = test_tender_cd_lots  # TODO: change attribute identifier
    test_status_that_denies_delete_create_patch_lots = "unsuccessful"
    initial_criteria = test_exclusion_criteria + test_language_criteria

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)


class CompetitiveDialogueUALotEdgeCasesTest(CompetitiveDialogueEULotEdgeCasesTest):
    initial_data = test_tender_cdua_data
    initial_config = test_tender_cdua_config


class CompetitiveDialogueUALotFeatureResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = 2 * test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_cdua_data
    invalid_feature_value = 1
    max_feature_value = 0.99
    sum_of_max_value_of_all_features = 0.99
    initial_criteria = test_exclusion_criteria + test_language_criteria

    test_tender_value = snitch(tender_value)
    test_tender_features_invalid = snitch(tender_features_invalid)


class CompetitiveDialogueUALotBidderResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_cd_stage1_bids  # TODO: change attribute identifier
    initial_criteria = test_exclusion_criteria + test_language_criteria

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class CompetitiveDialogueUALotFeatureBidderResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_cdua_data
    test_bids_data = test_tender_cd_stage1_bids  # TODO: change attribute identifier
    initial_criteria = test_exclusion_criteria + test_language_criteria

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

    test_create_tender_bidder_invalid = snitch(create_tender_with_features_bidder_invalid)


class CompetitiveDialogueUALotProcessTest(BaseCompetitiveDialogUAContentWebTest):
    initial_data = test_tender_cdua_data
    initial_lots = test_lots_data = test_tender_cd_lots  # TODO: change attribute identifier
    iniitial_bids = test_bids_data = test_tender_cd_stage1_bids  # TODO: change attribute identifier

    test_1lot_0bid = snitch(one_lot_0bid)
    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1unqualified)
    test_1lot_2bid = snitch(one_lot_2bid)
    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del)
    test_1lot_3bid_1del = snitch(one_lot_3bid_1del)
    test_1lot_3bid_1un = snitch(one_lot_3bid_1un)
    test_2lot_0bid = snitch(two_lot_0bid)
    test_2lot_2can = snitch(two_lot_2can)
    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can)
    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogueEULotResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogueEULotBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogueEULotFeatureResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogueEULotProcessTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogueUALotResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogueUALotFeatureResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogueUALotBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogueUALotProcessTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogueUALotFeatureBidderResourceTest))

    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
