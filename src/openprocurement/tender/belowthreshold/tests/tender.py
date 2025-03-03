import unittest
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    BaseApiWebTest,
    BaseTenderWebTest,
    test_tender_below_data,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    check_notice_doc_during_activation,
    contract_template_name_set,
    create_tender,
    create_tender_central,
    create_tender_central_invalid,
    create_tender_draft,
    create_tender_generated,
    create_tender_invalid,
    create_tender_invalid_config,
    create_tender_with_estimated_value,
    create_tender_with_inn,
    create_tender_with_required_unit,
    dateModified_tender,
    first_bid_tender,
    get_tender,
    guarantee,
    invalid_tender_conditions,
    listing,
    listing_changes,
    listing_draft,
    lost_contract_for_active_award,
    one_invalid_bid_tender,
    one_valid_bid_tender,
    patch_enquiry_tender_periods,
    patch_item_with_zero_quantity,
    patch_items_related_buyer_id,
    patch_not_author,
    patch_tender,
    patch_tender_draft,
    patch_tender_jsonpatch,
    patch_tender_lots_none,
    patch_tender_minimalstep_validation,
    required_field_deletion,
    tender_created_after_related_lot_is_required,
    tender_created_before_related_lot_is_required,
    tender_delivery_milestones,
    tender_features,
    tender_features_invalid,
    tender_fields,
    tender_finance_milestones,
    tender_financing_milestones,
    tender_funders,
    tender_inspector,
    tender_item_related_lot_validation,
    tender_items_float_quantity,
    tender_items_negative_quantity,
    tender_items_zero_quantity,
    tender_lot_minimalstep_validation,
    tender_milestones_required,
    tender_milestones_sequence_number,
    tender_minimalstep_validation,
    tender_not_found,
    tender_notice_documents,
    tender_token_invalid,
    tender_with_main_procurement_category,
    validate_enquiry_period,
    validate_tender_period,
)


class TenderResourceTestMixin:
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_listing = snitch(listing)
    test_create_tender_draft = snitch(create_tender_draft)
    test_patch_tender_draft = snitch(patch_tender_draft)
    test_create_tender = snitch(create_tender)
    test_tender_features = snitch(tender_features)
    test_get_tender = snitch(get_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_patch_not_author = snitch(patch_not_author)
    test_tender_funders = snitch(tender_funders)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_tender_token_invalid = snitch(tender_token_invalid)
    test_patch_item_with_zero_quantity = snitch(patch_item_with_zero_quantity)
    test_patch_items_related_buyer_id = snitch(patch_items_related_buyer_id)
    test_tender_financing_milestones = snitch(tender_financing_milestones)
    test_tender_delivery_milestones = snitch(tender_delivery_milestones)
    test_tender_milestones_sequence_number = snitch(tender_milestones_sequence_number)
    test_tender_notice_documents = snitch(tender_notice_documents)
    test_contract_template_name_set = snitch(contract_template_name_set)


class TenderTest(BaseApiWebTest):
    initial_data = test_tender_below_data


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin):
    initial_data = test_tender_below_data
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_lots_data = test_tender_below_lots

    test_guarantee = snitch(guarantee)
    test_tender_inspector = snitch(tender_inspector)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_validate_enquiry_period = snitch(validate_enquiry_period)
    test_validate_tender_period = snitch(validate_tender_period)
    test_create_tender_generated = snitch(create_tender_generated)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_tender_fields = snitch(tender_fields)
    test_tender_items_float_quantity = snitch(tender_items_float_quantity)
    test_tender_items_zero_quantity = snitch(tender_items_zero_quantity)
    test_tender_items_negative_quantity = snitch(tender_items_negative_quantity)
    test_patch_tender_jsonpatch = snitch(patch_tender_jsonpatch)
    test_patch_tender = snitch(patch_tender)
    test_required_field_deletion = snitch(required_field_deletion)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_tender_milestones_required = snitch(tender_milestones_required)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_minimalstep_validation = snitch(tender_minimalstep_validation)
    test_tender_item_related_lot_validation = snitch(tender_item_related_lot_validation)
    test_tender_lot_minimalstep_validation = snitch(tender_lot_minimalstep_validation)
    test_patch_tender_minimalstep_validation = snitch(patch_tender_minimalstep_validation)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_patch_enquiry_tender_periods = snitch(patch_enquiry_tender_periods)
    test_tender_created_before_related_lot_is_required = snitch(tender_created_before_related_lot_is_required)
    test_tender_created_after_related_lot_is_required = snitch(tender_created_after_related_lot_is_required)
    test_create_tender_with_estimated_value = snitch(create_tender_with_estimated_value)
    test_check_notice_doc_during_activation = snitch(check_notice_doc_during_activation)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderProcessTest(BaseTenderWebTest):
    initial_auth = ("Basic", ("broker", ""))

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_valid_bid_tender = snitch(one_valid_bid_tender)
    test_one_invalid_bid_tender = snitch(one_invalid_bid_tender)
    test_first_bid_tender = snitch(first_bid_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderProcessTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
