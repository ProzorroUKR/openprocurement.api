import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest,
    BaseApiWebTest,
    test_tender_below_data,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.models import Tender
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    one_valid_bid_tender,
    one_invalid_bid_tender,
    first_bid_tender,
    create_tender,
    invalid_tender_conditions,
    lost_contract_for_active_award,
    listing,
    get_tender,
    tender_features_invalid,
    tender_not_found,
    dateModified_tender,
    guarantee,
    patch_not_author,
    listing_draft,
    tender_fields,
    tender_items_float_quantity,
    tender_items_zero_quantity,
    tender_items_negative_quantity,
    listing_changes,
    create_tender_invalid,
    validate_enquiryTender,
    validate_tenderPeriod,
    create_tender_generated,
    create_tender_draft,
    patch_tender_draft,
    tender_features,
    patch_tender_jsonpatch,
    patch_tender,
    required_field_deletion,
    tender_funders,
    tender_with_main_procurement_category,
    tender_finance_milestones,
    patch_tender_lots_none,
    create_tender_with_inn,
    create_tender_with_inn_before,
    tender_milestones_required,
    tender_token_invalid,
    create_tender_central,
    create_tender_central_invalid,
    tender_minimalstep_validation,
    tender_lot_minimalstep_validation,
    patch_tender_minimalstep_validation,
    create_tender_with_earlier_non_required_unit,
    create_tender_with_required_unit,
    patch_item_with_zero_quantity,
    patch_items_related_buyer_id,
    patch_enquiry_tender_periods,
    create_tender_config_test,
)


class TenderResourceTestMixin(object):
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
    test_create_tender_config_test = snitch(create_tender_config_test)


class TenderTest(BaseApiWebTest):
    docservice = True
    tender_model = Tender
    initial_data = test_tender_below_data


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin):
    docservice = True
    initial_data = test_tender_below_data
    initial_auth = ("Basic", ("broker", ""))
    test_lots_data = test_tender_below_lots

    test_guarantee = snitch(guarantee)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_validate_enquiryTender = snitch(validate_enquiryTender)
    test_validate_periodTender = snitch(validate_tenderPeriod)
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
    test_create_tender_with_inn_before = snitch(create_tender_with_inn_before)
    test_tender_milestones_required = snitch(tender_milestones_required)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_minimalstep_validation = snitch(tender_minimalstep_validation)
    test_tender_lot_minimalstep_validation = snitch(tender_lot_minimalstep_validation)
    test_patch_tender_minimalstep_validation = snitch(patch_tender_minimalstep_validation)
    test_create_tender_with_earlier_non_required_unit = snitch(create_tender_with_earlier_non_required_unit)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_patch_enquiry_tender_periods = snitch(patch_enquiry_tender_periods)


class TenderProcessTest(BaseTenderWebTest):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_valid_bid_tender = snitch(one_valid_bid_tender)
    test_one_invalid_bid_tender = snitch(one_invalid_bid_tender)
    test_first_bid_tender = snitch(first_bid_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderProcessTest))
    suite.addTest(unittest.makeSuite(TenderResourceTest))
    suite.addTest(unittest.makeSuite(TenderTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
