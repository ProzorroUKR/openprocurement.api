# -*- coding: utf-8 -*-
import unittest
from openprocurement.tender.openeu.constants import TENDERING_DAYS
from openprocurement.tender.esco.tests.base import (
    test_tender_data, test_lots, test_bids,
    BaseESCOWebTest, BaseESCOContentWebTest,
)
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    # TenderProcessTest
    invalid_tender_conditions,
    # TenderResourceTest
    guarantee,
)

from openprocurement.tender.openua.tests.tender import TenderUAResourceTestMixin
from openprocurement.tender.openua.tests.tender_blanks import tender_with_main_procurement_category

from openprocurement.tender.openeu.tests.tender_blanks import (
    # TenderProcessTest
    one_bid_tender,
    unsuccessful_after_prequalification_tender,
    one_qualificated_bid_tender,
    multiple_bidders_tender,
    lost_contract_for_active_award,
    # TenderResourceTest
    invalid_bid_tender_lot,
)

from openprocurement.tender.esco.tests.tender_blanks import (
    # TenderESCOTest
    simple_add_tender,
    tender_value,
    tender_min_value,
    tender_minimal_step_invalid,
    tender_yearlyPaymentsPercentageRange,
    tender_yearlyPaymentsPercentageRange_invalid,
    tender_fundingKind_default,
    items_without_deliveryDate_quantity,
    tender_noticePublicationDate,
    # TestTenderEU
    create_tender_invalid,
    patch_tender,
    tender_fields,
    tender_with_nbu_discount_rate,
    tender_features,
    tender_features_invalid,
    invalid_bid_tender_features,
    create_tender_generated,
)


class TenderESCOTest(BaseESCOWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data
    test_bids_data = test_bids

    test_simple_add_tender = snitch(simple_add_tender)
    test_tender_value = snitch(tender_value)
    test_tender_min_value = snitch(tender_min_value)
    test_tender_minimal_step_invalid = snitch(tender_minimal_step_invalid)
    test_tender_yearlyPaymentsPercentageRange_invalid = snitch(tender_yearlyPaymentsPercentageRange_invalid)
    test_tender_yearlyPaymentsPercentageRange = snitch(tender_yearlyPaymentsPercentageRange)
    test_items_without_deliveryDate_quantity = snitch(items_without_deliveryDate_quantity)
    test_tender_fundingKind_default = snitch(tender_fundingKind_default)
    test_tender_noticePublicationDate = snitch(tender_noticePublicationDate)


class TestTenderEU(BaseESCOContentWebTest, TenderResourceTestMixin, TenderUAResourceTestMixin):
    """ ESCO tender test """
    initialize_initial_data = False
    initial_data = test_tender_data
    # for passing test from TenderUAResourceTestMixin
    initial_data['minValue'] = {"amount": 0}
    test_lots_data = test_lots
    test_bids_data = test_bids
    tender_period_duration = TENDERING_DAYS

    test_tender_fields = snitch(tender_fields)
    test_tender_with_nbu_discount_rate = snitch(tender_with_nbu_discount_rate)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_tender_features = snitch(tender_features)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)


class TestTenderEUProcess(BaseESCOContentWebTest):

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
    suite.addTest(unittest.makeSuite(TenderESCOTest))
    suite.addTest(unittest.makeSuite(TestTenderEU))
    suite.addTest(unittest.makeSuite(TestTenderEUProcess))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
