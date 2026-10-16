import unittest

from openprocurement.api.constants import KIND_PROCUREMENT_METHOD_TYPE_MAPPING
from openprocurement.api.tests.base import snitch
from openprocurement.tender.arma.constants import SIMPLE_ASSET_ARMA
from openprocurement.tender.arma.tests.complex_asset.tender_blanks import (
    create_tender_invalid,
    create_tender_with_required_unit,
    invalid_bid_tender_lot,
    patch_tender_lot_min_expected_income_before_date_gate,
    set_buyers_signer_info,
    set_procuring_entity_signer_info,
    tender_delivery_milestones,
    tender_financing_milestones,
)
from openprocurement.tender.arma.tests.simple_asset.base import (
    BaseTenderSimpleAssetWebTest,
    test_tender_arma_simple_bids,
    test_tender_arma_simple_data,
    test_tender_arma_simple_lots,
)
from openprocurement.tender.arma.tests.simple_asset.tender_blanks import (
    activate_tender_with_inactive_agreement,
    activate_tender_with_insufficient_agreement_contracts,
    create_tender_generated,
    create_tender_with_invalid_agreement_type,
    create_tender_with_mismatched_agreement_procuring_entity,
    create_tender_with_unknown_agreement,
    create_tender_without_agreement,
    first_bid_tender,
    lost_contract_for_active_award,
    one_bid_tender,
    patch_tender,
    patch_tender_draft,
    patch_tender_lot_min_expected_income,
    patch_tender_period,
)
from openprocurement.tender.open.tests.above_threshold.tender_blanks import tender_finance_milestones
from openprocurement.tender.open.tests.above_threshold_ua.tender_blanks import (
    empty_listing,
    tender_with_main_procurement_category,
)
from openprocurement.tender.open.tests.below_threshold.tender import TenderResourceTestMixin
from openprocurement.tender.open.tests.below_threshold.tender_blanks import (
    create_tender_with_inn,
    guarantee,
    invalid_tender_conditions,
    patch_not_author,
    patch_tender_lots_none,
)


class TenderResourceTest(BaseTenderSimpleAssetWebTest, TenderResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_arma_simple_data
    initial_lots = test_lots_data = test_tender_arma_simple_lots
    initial_bids = test_bids_data = test_tender_arma_simple_bids
    allowed_proc_entity_kinds = KIND_PROCUREMENT_METHOD_TYPE_MAPPING[SIMPLE_ASSET_ARMA]

    test_empty_listing = snitch(empty_listing)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_patch_tender = snitch(patch_tender)
    test_patch_tender_draft = snitch(patch_tender_draft)
    test_patch_tender_period = snitch(patch_tender_period)
    test_patch_not_author = snitch(patch_not_author)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_guarantee = snitch(guarantee)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_set_buyers_signer_info = unittest.skip(
        "ARMA procedure cannot have kind=central, hence cannot create buyers field"
    )(snitch(set_buyers_signer_info))
    test_set_procuring_entity_signer_info = snitch(set_procuring_entity_signer_info)
    test_tender_delivery_milestones = snitch(tender_delivery_milestones)
    test_tender_financing_milestones = snitch(tender_financing_milestones)
    test_patch_tender_lot_min_expected_income = snitch(patch_tender_lot_min_expected_income)
    test_patch_tender_lot_min_expected_income_before_date_gate = snitch(
        patch_tender_lot_min_expected_income_before_date_gate
    )

    test_set_procuring_entity_contract_owner = None
    test_contract_template_name_set = None


class TenderAgreementTest(BaseTenderSimpleAssetWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_arma_simple_data
    initial_lots = test_lots_data = test_tender_arma_simple_lots

    test_create_tender_without_agreement = snitch(create_tender_without_agreement)
    test_create_tender_with_unknown_agreement = snitch(create_tender_with_unknown_agreement)
    test_create_tender_with_invalid_agreement_type = snitch(create_tender_with_invalid_agreement_type)
    test_create_tender_with_mismatched_agreement_procuring_entity = snitch(
        create_tender_with_mismatched_agreement_procuring_entity
    )
    test_activate_tender_with_inactive_agreement = snitch(activate_tender_with_inactive_agreement)
    test_activate_tender_with_insufficient_agreement_contracts = snitch(
        activate_tender_with_insufficient_agreement_contracts
    )


class TenderProcessTest(BaseTenderSimpleAssetWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_arma_simple_data
    initial_lots = test_lots_data = test_tender_arma_simple_lots
    test_bids_data = test_tender_arma_simple_bids

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_one_bid_tender = snitch(one_bid_tender)
    test_first_bid_tender = snitch(first_bid_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAgreementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderProcessTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
