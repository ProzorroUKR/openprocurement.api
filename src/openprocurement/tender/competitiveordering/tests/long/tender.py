import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.constants import KIND_PROCUREMENT_METHOD_TYPE_MAPPING
from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    create_tender_central,
    create_tender_central_invalid,
    create_tender_with_inn,
    create_tender_with_required_unit,
    guarantee,
    invalid_tender_conditions,
    patch_tender_lots_none,
    patch_tender_minimalstep_validation,
    tender_lot_minimalstep_validation,
    tender_milestones_required,
)
from openprocurement.tender.competitiveordering.tests.long.base import (
    BaseTenderCOLongWebTest,
    test_tender_co_long_bids,
    test_tender_co_long_data,
)
from openprocurement.tender.competitiveordering.tests.long.tender_blanks import (
    create_tender_invalid_agreement,
    patch_tender,
    patch_tender_period,
)
from openprocurement.tender.open.tests.tender_blanks import (
    activate_bid_after_adding_lot,
    create_tender_generated,
    create_tender_invalid,
    create_tender_invalid_config,
    create_tender_with_criteria_lcc,
    empty_listing,
    first_bid_tender,
    get_ocds_schema,
    invalid1_and_1draft_bids_tender,
    invalid_bid_tender_features,
    invalid_bid_tender_lot,
    lost_contract_for_active_award,
    one_valid_bid_tender_ua,
    patch_draft_invalid_json,
    tender_fields,
    tender_finance_milestones,
    tender_with_main_procurement_category,
)


class TenderCOResourceTestMixin:
    test_empty_listing = snitch(empty_listing)
    test_tender_fields = snitch(tender_fields)
    test_patch_tender_period = snitch(patch_tender_period)


class TenderCOProcessTestMixin:
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_first_bid_tender = snitch(first_bid_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


class TenderCOResourceTest(BaseTenderCOLongWebTest, TenderResourceTestMixin, TenderCOResourceTestMixin):
    initial_data = test_tender_co_long_data
    initial_lots = test_tender_below_lots
    allowed_proc_entity_kinds = KIND_PROCUREMENT_METHOD_TYPE_MAPPING["competitiveOrdering"]

    def setUp(self):
        super().setUp()
        self.test_lots_data = deepcopy(self.initial_lots)

    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_create_tender_co_invalid_agreement = snitch(create_tender_invalid_agreement)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_draft_invalid_json = snitch(patch_draft_invalid_json)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_milestones_required = snitch(tender_milestones_required)
    test_tender_lot_minimalstep_validation = snitch(tender_lot_minimalstep_validation)
    test_patch_tender_minimalstep_validation = snitch(patch_tender_minimalstep_validation)
    test_create_tender_with_criteria_lcc = snitch(create_tender_with_criteria_lcc)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_get_ocds_schema = snitch(get_ocds_schema)


@patch(
    "openprocurement.tender.competitiveordering.procedure.state.award.NEW_ARTICLE_17_CRITERIA_REQUIRED",
    get_now() + timedelta(days=1),
)
class TenderCOProcessTest(BaseTenderCOLongWebTest, TenderCOProcessTestMixin):
    initial_data = test_tender_co_long_data
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_co_long_bids

    def setUp(self):
        super().setUp()
        self.test_bids_data = deepcopy(self.initial_bids)

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_valid_bid_tender_ua = snitch(one_valid_bid_tender_ua)
    test_invalid1_and_1draft_bids_tender = snitch(invalid1_and_1draft_bids_tender)
    test_activate_bid_after_adding_lot = snitch(activate_bid_after_adding_lot)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCOProcessTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCOResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
