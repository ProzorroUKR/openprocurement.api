import unittest

from openprocurement.api.constants import KIND_PROCUREMENT_METHOD_TYPE_MAPPING
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    contract_template_name_set,
    create_tender_with_required_unit,
    dateModified_tender,
    get_tender,
    patch_not_author,
    patch_tender_jsonpatch,
    tender_contract_change_rationale_types,
    tender_funders,
    tender_items_float_quantity,
    tender_items_negative_quantity,
    tender_not_found,
    tender_token_invalid,
    tender_with_main_procurement_category,
    validate_procurement_entity_kind,
    validate_procurement_entity_kind_patch,
)
from openprocurement.tender.core.tests.mock import MockCriteriaIDMixin, MockMarketMixin
from openprocurement.tender.open.tests.tender_blanks import create_tender_invalid_config
from openprocurement.tender.pricequotation.tests.base import (
    BaseTenderWebTest,
    TenderContentWebTest,
)
from openprocurement.tender.pricequotation.tests.data import test_tender_pq_data
from openprocurement.tender.pricequotation.tests.tender_blanks import (
    create_tender,
    create_tender_draft,
    create_tender_draft_with_criteria,
    create_tender_draft_with_criteria_expected_values,
    create_tender_generated,
    create_tender_in_not_draft_status,
    create_tender_invalid,
    create_tender_with_inn,
    draft_activation_validations,
    invalid_tender_conditions,
    listing,
    listing_changes,
    listing_draft,
    patch_items_related_buyer_id,
    patch_tender,
    patch_tender_status,
    required_field_deletion,
    switch_draft_to_tendering_success,
    tender_criteria_values_type,
    tender_delivery_milestones,
    tender_fields,
    tender_finance_milestones,
    tender_owner_can_change_in_draft,
    tender_owner_cannot_change_in_draft,
    tender_period_update,
)


class TenderResourceTestMixin:
    allowed_proc_entity_kinds = ...

    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_listing = snitch(listing)
    test_tender_period_update = snitch(tender_period_update)
    test_create_tender = snitch(create_tender)
    test_get_tender = snitch(get_tender)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_patch_not_author = snitch(patch_not_author)
    test_tender_funders = snitch(tender_funders)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_token_invalid = snitch(tender_token_invalid)
    test_create_tender_in_not_draft_status = snitch(create_tender_in_not_draft_status)
    test_patch_items_related_buyer_id = snitch(patch_items_related_buyer_id)
    test_tender_delivery_milestones = snitch(tender_delivery_milestones)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_contract_template_name_set = snitch(contract_template_name_set)
    test_validate_procurement_entity_kind = snitch(validate_procurement_entity_kind)
    test_validate_procurement_entity_kind_patch = snitch(validate_procurement_entity_kind_patch)
    test_tender_contract_change_rationale_types = snitch(tender_contract_change_rationale_types)


class TenderResourceTest(MockMarketMixin, MockCriteriaIDMixin, BaseTenderWebTest, TenderResourceTestMixin):
    initial_data = test_tender_pq_data
    initial_auth = ("Basic", ("broker", ""))
    allowed_proc_entity_kinds = KIND_PROCUREMENT_METHOD_TYPE_MAPPING["priceQuotation"]

    test_create_tender_draft = snitch(create_tender_draft)
    test_create_tender_draft_with_criteria = snitch(create_tender_draft_with_criteria)
    test_create_tender_draft_with_criteria_expected_values = snitch(create_tender_draft_with_criteria_expected_values)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_create_tender_generated = snitch(create_tender_generated)
    test_tender_owner_can_change_in_draft = snitch(tender_owner_can_change_in_draft)
    test_tender_owner_cannot_change_in_draft = snitch(tender_owner_cannot_change_in_draft)
    test_tender_fields = snitch(tender_fields)
    test_tender_items_float_quantity = snitch(tender_items_float_quantity)
    test_tender_items_negative_quantity = snitch(tender_items_negative_quantity)
    test_patch_tender_jsonpatch = snitch(patch_tender_jsonpatch)
    test_patch_tender = snitch(patch_tender)
    test_required_field_deletion = snitch(required_field_deletion)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_patch_tender_status = snitch(patch_tender_status)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_tender_criteria_values_type = snitch(tender_criteria_values_type)


class TenderActivationTest(TenderContentWebTest):
    test_draft_activation_validations = snitch(draft_activation_validations)
    test_switch_draft_to_tendering_success = snitch(switch_draft_to_tendering_success)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
