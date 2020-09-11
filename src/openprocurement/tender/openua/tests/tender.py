# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_lots

from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    # TenderUAResourceTest
    guarantee,
    patch_tender_lots_none,
    # TenderUAProcessTest
    invalid_tender_conditions,
    create_tender_with_inn,
    create_tender_with_inn_before,
    tender_milestones_required,
    create_tender_central,
    create_tender_central_invalid,
    tender_minimalstep_validation,
    patch_tender_minimalstep_validation,
)

from openprocurement.tender.openua.tests.base import test_tender_data, test_bids, BaseTenderUAWebTest, BaseApiWebTest
from openprocurement.tender.openua.tests.tender_blanks import (
    # Tender UA Test
    simple_add_tender,
    # TenderUAResourceTest
    empty_listing,
    patch_draft_invalid_json,
    create_tender_invalid,
    create_tender_generated,
    tender_fields,
    patch_tender,
    patch_tender_period,
    tender_with_main_procurement_category,
    tender_finance_milestones,
    # TenderUAProcessTest
    invalid_bid_tender_features,
    invalid_bid_tender_lot,
    one_valid_bid_tender_ua,
    invalid1_and_1draft_bids_tender,
    activate_bid_after_adding_lot,
    first_bid_tender,
    lost_contract_for_active_award,
)


class TenderUAResourceTestMixin(object):
    test_empty_listing = snitch(empty_listing)
    test_tender_fields = snitch(tender_fields)
    test_patch_tender_period = snitch(patch_tender_period)


class TenderUaProcessTestMixin(object):
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_first_bid_tender = snitch(first_bid_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


class TenderUATest(BaseApiWebTest):
    initial_data = test_tender_data
    test_simple_add_tender = snitch(simple_add_tender)


class TenderUAResourceTest(BaseTenderUAWebTest, TenderResourceTestMixin, TenderUAResourceTestMixin):
    initial_data = test_tender_data
    test_lots_data = test_lots

    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_draft_invalid_json = snitch(patch_draft_invalid_json)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_create_tender_with_inn_before = snitch(create_tender_with_inn_before)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_milestones_required = snitch(tender_milestones_required)
    test_tender_minimalstep_validation = snitch(tender_minimalstep_validation)
    test_patch_tender_minimalstep_validation = snitch(patch_tender_minimalstep_validation)


class TenderUAProcessTest(BaseTenderUAWebTest, TenderUaProcessTestMixin):
    initial_data = test_tender_data
    test_bids_data = test_bids

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_valid_bid_tender_ua = snitch(one_valid_bid_tender_ua)
    test_invalid1_and_1draft_bids_tender = snitch(invalid1_and_1draft_bids_tender)
    test_activate_bid_after_adding_lot = snitch(activate_bid_after_adding_lot)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderUAProcessTest))
    suite.addTest(unittest.makeSuite(TenderUAResourceTest))
    suite.addTest(unittest.makeSuite(TenderUATest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
