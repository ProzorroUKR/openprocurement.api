import unittest
from unittest.mock import patch
from datetime import timedelta
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch
from copy import deepcopy
from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotResourceTestMixin,
    TenderLotValueTestMixin,
    TenderLotFeatureResourceTestMixin,
    TenderLotProcessTestMixin,
)

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_author
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    patch_tender_lot_minimalstep_validation,
    create_tender_lot_minimalstep_validation,
)

from openprocurement.tender.openua.tests.lot_blanks import (
    get_tender_lot,
    get_tender_lots,
)

from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_tender_openeu_data,
    test_tender_openeu_lots,
    test_tender_openeu_bids,
)
from openprocurement.tender.openeu.tests.lot_blanks import (
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
    create_tender_feature_bidder_invalid,
    create_tender_feature_bidder,
    create_tender_bidder_invalid,
    patch_tender_bidder,
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


@patch("openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
       get_now() + timedelta(days=1))
class TenderLotResourceTest(BaseTenderContentWebTest, TenderLotResourceTestMixin, TenderLotValueTestMixin):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))
    test_lots_data = test_tender_openeu_lots  # TODO: change attribute identifier
    initial_data = test_tender_openeu_data

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)


class TenderLotEdgeCasesTest(BaseTenderContentWebTest, TenderLotEdgeCasesTestMixin):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_openeu_lots * 2
    initial_bids = test_tender_openeu_bids
    test_author = test_tender_below_author


class TenderLotFeatureResourceTest(BaseTenderContentWebTest, TenderLotFeatureResourceTestMixin):
    docservice = True
    initial_lots = 2 * test_tender_openeu_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_openeu_data
    invalid_feature_value = 0.4
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3


class TenderLotBidderResourceTest(BaseTenderContentWebTest):
    docservice = True
    initial_lots = test_tender_openeu_lots
    initial_auth = ("Basic", ("broker", ""))
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderLotFeatureBidderResourceTest(BaseTenderContentWebTest):
    docservice = True
    initial_lots = test_tender_openeu_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_openeu_data
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier
    initial_criteria = test_exclusion_criteria + test_language_criteria

    def setUp(self):
        super(TenderLotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]["id"]
        items = deepcopy(self.initial_data["items"])
        items[0].update({"relatedLot": self.lot_id, "id": "1"})
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

    test_create_tender_bidder_invalid = snitch(create_tender_feature_bidder_invalid)
    test_create_tender_bidder = snitch(create_tender_feature_bidder)


class TenderLotProcessTest(BaseTenderContentWebTest, TenderLotProcessTestMixin):
    docservice = True
    setUp = BaseTenderContentWebTest.setUp
    test_lots_data = test_tender_openeu_lots  # TODO: change attribute identifier
    initial_data = test_tender_openeu_data
    test_bids_data = test_tender_openeu_bids  # TODO: change attribute identifier

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
