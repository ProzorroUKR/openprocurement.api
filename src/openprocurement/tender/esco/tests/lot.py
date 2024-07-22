import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from esculator import escp, npv

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_author
from openprocurement.tender.belowthreshold.tests.lot import TenderLotProcessTestMixin
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    create_tender_lot,
    delete_tender_lot,
    patch_tender_lot,
    tender_lot_document,
    tender_lot_guarantee,
    tender_lot_milestones,
)
from openprocurement.tender.esco.procedure.utils import to_decimal
from openprocurement.tender.esco.tests.base import (
    NBU_DISCOUNT_RATE,
    BaseESCOContentWebTest,
    test_tender_esco_bids,
    test_tender_esco_data,
    test_tender_esco_lots,
)
from openprocurement.tender.esco.tests.lot_blanks import (
    bids_invalidation_on_lot_change,
    create_tender_bid_invalid,
    create_tender_feature_bid,
    create_tender_feature_bid_invalid,
    create_tender_lot_invalid,
    get_tender_lot,
    get_tender_lots,
    lot_minimal_step_invalid,
    lot_yppr_validation,
    patch_tender_bid,
    patch_tender_lot_minValue,
    tender_1lot_fundingKind_default,
    tender_2lot_fundingKind_default,
    tender_features_invalid,
    tender_lot_Administrator_change_yppr,
    tender_lot_funding_kind,
    tender_lot_fundingKind_yppr,
    tender_lot_yearlyPaymentsPercentageRange,
    tender_min_value,
    tender_minimal_step_percentage,
)
from openprocurement.tender.openeu.tests.lot import TenderLotEdgeCasesTestMixin
from openprocurement.tender.openeu.tests.lot_blanks import (
    one_lot_1bid,
    one_lot_2bid,
    one_lot_2bid_1unqualified,
    one_lot_3bid_1del,
    one_lot_3bid_1un,
    two_lot_1can,
    two_lot_2bid_0com_1can,
    two_lot_2bid_1lot_del,
    two_lot_2bid_2com_2win,
    two_lot_3bid_1win_bug,
)

lot_bid_amountPerformance = round(
    float(
        to_decimal(
            npv(
                test_tender_esco_bids[0]["value"]["contractDuration"]["years"],
                test_tender_esco_bids[0]["value"]["contractDuration"]["days"],
                test_tender_esco_bids[0]["value"]["yearlyPaymentsPercentage"],
                test_tender_esco_bids[0]["value"]["annualCostsReduction"],
                get_now(),
                NBU_DISCOUNT_RATE,
            )
        )
    ),
    2,
)

lot_bid_amount = round(
    float(
        to_decimal(
            escp(
                test_tender_esco_bids[0]["value"]["contractDuration"]["years"],
                test_tender_esco_bids[0]["value"]["contractDuration"]["days"],
                test_tender_esco_bids[0]["value"]["yearlyPaymentsPercentage"],
                test_tender_esco_bids[0]["value"]["annualCostsReduction"],
                get_now(),
            )
        )
    ),
    2,
)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
    get_now() + timedelta(days=1),
)
@patch(
    "openprocurement.tender.core.procedure.state.tender_details.MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
    get_now() + timedelta(days=1),
)
class TenderLotResourceTest(BaseESCOContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    test_lots_data = test_tender_esco_lots  # TODO: change attribute identifier
    test_bids = test_tender_esco_bids
    initial_data = test_tender_esco_data

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_create_tender_lot = snitch(create_tender_lot)
    test_lot_yppr_validation = snitch(lot_yppr_validation)
    test_patch_tender_lot = snitch(patch_tender_lot)
    test_patch_tender_lot_minValue = snitch(patch_tender_lot_minValue)
    test_delete_tender_lot = snitch(delete_tender_lot)

    test_tender_lot_guarantee = snitch(tender_lot_guarantee)
    test_tender_lot_milestones = snitch(tender_lot_milestones)

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_lot_minimal_step_invalid = snitch(lot_minimal_step_invalid)
    test_tender_minimal_step_percentage = snitch(tender_minimal_step_percentage)
    test_tender_lot_funding_kind = snitch(tender_lot_funding_kind)
    test_tender_1lot_fundingKind_default = snitch(tender_1lot_fundingKind_default)
    test_tender_2lot_fundingKind_default = snitch(tender_2lot_fundingKind_default)
    test_tender_lot_yearlyPaymentsPercentageRange = snitch(tender_lot_yearlyPaymentsPercentageRange)
    test_tender_lot_fundingKind_yppr = snitch(tender_lot_fundingKind_yppr)
    test_tender_lot_Administrator_change_yppr = snitch(tender_lot_Administrator_change_yppr)


class TenderLotEdgeCasesTest(BaseESCOContentWebTest, TenderLotEdgeCasesTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_esco_lots * 2
    initial_bids = test_tender_esco_bids
    test_author = test_tender_below_author


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
    get_now() + timedelta(days=1),
)
class TenderLotFeatureResourceTest(BaseESCOContentWebTest):
    initial_lots = 2 * test_tender_esco_lots
    # for passing test_tender_min_value while min value = 0
    # initial_lots[0]["minValue"] = {"amount": 0}
    # initial_lots[1]["minValue"] = {"amount": 0}
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_esco_data
    test_lots_data = test_tender_esco_lots
    invalid_feature_value = 0.4
    max_feature_value = 0.25
    sum_of_max_value_of_all_features = 0.25

    test_tender_min_value = snitch(tender_min_value)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_lot_document = snitch(tender_lot_document)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
    get_now() + timedelta(days=1),
)
class TenderLotBidResourceTest(BaseESCOContentWebTest):
    initial_lots = test_tender_esco_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_esco_bids  # TODO: change attribute identifier
    expected_bid_amount_performance = lot_bid_amountPerformance
    expected_bid_amount = lot_bid_amount

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_bids_invalidation_on_lot_change = snitch(bids_invalidation_on_lot_change)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
    get_now() + timedelta(days=1),
)
class TenderLotFeatureBidResourceTest(BaseESCOContentWebTest):
    initial_lots = test_tender_esco_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_esco_data
    test_bids_data = test_tender_esco_bids  # TODO: change attribute identifier

    def setUp(self):
        super().setUp()
        self.lot_id = self.initial_lots[0]["id"]
        items = deepcopy(self.initial_data["items"])
        items[0].update(relatedLot=self.lot_id, id="1")

        with patch(
            "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
            get_now() + timedelta(days=1),
        ):
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

    test_create_tender_bid_invalid = snitch(create_tender_feature_bid_invalid)
    test_create_tender_bid = snitch(create_tender_feature_bid)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
    get_now() + timedelta(days=1),
)
class TenderLotProcessTest(BaseESCOContentWebTest, TenderLotProcessTestMixin):
    setUp = BaseESCOContentWebTest.setUp
    test_lots_data = test_tender_esco_lots  # TODO: change attribute identifier
    test_bids_data = test_tender_esco_bids
    initial_data = test_tender_esco_data

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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotEdgeCasesTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotFeatureResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotFeatureBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotProcessTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
