import unittest
from datetime import timedelta
from unittest import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.arma.tests.base import (
    BaseTenderContentWebTest,
    test_tender_arma_bids,
    test_tender_arma_data,
    test_tender_arma_lots,
)
from openprocurement.tender.arma.tests.lot_blanks import (
    claim_blocking,
    create_tender_bidder_invalid,
    create_tender_lot_invalid,
    create_tender_lot_minimalstep_validation,
    next_check_value_with_unanswered_claim,
    next_check_value_with_unanswered_question,
    one_lot_1bid,
    one_lot_2bid,
    one_lot_2bid_1unqualified,
    one_lot_3bid_1del,
    one_lot_3bid_1un,
    patch_tender_bidder,
    patch_tender_currency,
    patch_tender_lot_minimalstep_validation,
    patch_tender_vat,
    question_blocking,
    two_lot_1can,
    two_lot_2bid_0com_1can,
    two_lot_2bid_1lot_del,
    two_lot_2bid_2com_2win,
    two_lot_3bid_1win_bug,
)
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_author
from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotProcessTestMixin,
    TenderLotResourceTestMixin,
    TenderLotValueTestMixin,
)
from openprocurement.tender.openua.tests.lot_blanks import (
    get_tender_lot,
    get_tender_lots,
)


class TenderLotEdgeCasesTestMixin:
    test_question_blocking = snitch(question_blocking)
    test_claim_blocking = snitch(claim_blocking)
    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)
    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
    mock.Mock(return_value={}),
)
class TenderLotResourceTest(BaseTenderContentWebTest, TenderLotResourceTestMixin, TenderLotValueTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_lots_data = test_tender_arma_lots  # TODO: change attribute identifier
    initial_data = test_tender_arma_data

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_create_tender_lot_minimalstep_validation = snitch(create_tender_lot_minimalstep_validation)
    test_patch_tender_lot_minimalstep_validation = snitch(patch_tender_lot_minimalstep_validation)
    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)


class TenderLotEdgeCasesTest(BaseTenderContentWebTest, TenderLotEdgeCasesTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_arma_lots * 2
    initial_bids = test_tender_arma_bids

    test_author = test_tender_below_author


class TenderLotBidderResourceTest(BaseTenderContentWebTest):
    initial_lots = test_tender_arma_lots
    initial_auth = ("Basic", ("broker", ""))

    test_bids_data = test_tender_arma_bids  # TODO: change attribute identifier

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
    get_now() + timedelta(days=1),
)
class TenderLotProcessTest(BaseTenderContentWebTest, TenderLotProcessTestMixin):
    setUp = BaseTenderContentWebTest.setUp

    initial_data = test_tender_arma_data

    test_lots_data = test_tender_arma_lots  # TODO: change attribute identifier
    test_bids_data = test_tender_arma_bids  # TODO: change attribute identifier

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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotBidderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotProcessTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
