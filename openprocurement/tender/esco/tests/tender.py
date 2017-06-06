# -*- coding: utf-8 -*-
import unittest
from openprocurement.tender.openeu.constants import TENDERING_DAYS
from openprocurement.tender.esco.tests.base import (
    test_tender_data, test_lots, test_bids,
    BaseESCOWebTest, BaseESCOEUContentWebTest,
)
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    #TenderProcessTest
    invalid_tender_conditions,
    #TenderResourceTest
    guarantee,
)

from openprocurement.tender.openua.tests.tender import TenderUAResourceTestMixin

from openprocurement.tender.openeu.tests.tender_blanks import (
    #TenderProcessTest
    one_bid_tender,
    unsuccessful_after_prequalification_tender,
    one_qualificated_bid_tender,
    multiple_bidders_tender,
    lost_contract_for_active_award,
    #TenderResourceTest
    patch_tender,
    invalid_bid_tender_lot,
)

from openprocurement.tender.esco.tests.tender_blanks import (
    #TenderESCOEUTest
    simple_add_tender,
    tender_value,
    tender_min_value,
    #TestTenderEU
    create_tender_invalid,
    tender_with_nbu_discount_rate,
    invalid_bid_tender_features,
    create_tender_generated,
)


class TenderESCOEUTest(BaseESCOWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data

    test_simple_add_tender = snitch(simple_add_tender)
    test_tender_value = snitch(tender_value)
    test_tender_min_value = snitch(tender_min_value)


class TestTenderEU(BaseESCOEUContentWebTest, TenderResourceTestMixin, TenderUAResourceTestMixin):
    """ ESCO EU tender test """
    initialize_initial_data = False
    initial_data = test_tender_data
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_bids_data = test_bids
    tender_period_duration = TENDERING_DAYS

    test_tender_with_nbu_discount_rate = snitch(tender_with_nbu_discount_rate)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)


class TestTenderEUProcess(BaseESCOEUContentWebTest):

    initialize_initial_data = False
    initial_data = test_tender_data
    test_bids_data = test_bids

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_bid_tender = snitch(one_bid_tender)
    test_unsuccessful_after_prequalification_tender = snitch(unsuccessful_after_prequalification_tender)
    test_one_qualificated_bid_tender = snitch(one_qualificated_bid_tender)
    test_multiple_bidders_tender = snitch(multiple_bidders_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderESCOEUTest))
    suite.addTest(unittest.makeSuite(TestTenderEU))
    suite.addTest(unittest.makeSuite(TestTenderEUProcess))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
