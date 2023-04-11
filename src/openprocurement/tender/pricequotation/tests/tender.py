import unittest
from copy import deepcopy
from unittest.mock import patch
from datetime import timedelta
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.tests.data import test_tender_pq_criteria_1, \
    test_tender_pq_short_profile
from openprocurement.tender.pricequotation.tests.utils import criteria_drop_uuids
from openprocurement.tender.pricequotation.tests.base import (
    BaseTenderWebTest,
    TenderContentWebTest,
    test_tender_pq_data,
)

from openprocurement.tender.pricequotation.tests.tender_blanks import (
    listing,
    listing_draft,
    listing_changes,

    one_valid_bid_tender,
    one_invalid_bid_tender,
    first_bid_tender,

    create_tender,
    create_tender_draft,
    create_tender_generated,
    create_tender_invalid,
    create_tender_with_inn,
    create_tender_draft_with_criteria,
    create_tender_draft_with_criteria_expected_values,

    invalid_tender_conditions,
    patch_tender,
    patch_tender_by_pq_bot_before_multiprofile,
    patch_tender_by_pq_bot_after_multiprofile,
    tender_owner_can_change_in_draft,
    tender_owner_cannot_change_in_draft,
    tender_period_update,
    required_field_deletion,
    tender_fields,
    lost_contract_for_active_award,
    create_tender_in_not_draft_status,
    patch_tender_status,
    patch_items_related_buyer_id,
    tender_criteria_values_type,
)
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    guarantee,
    get_tender,
    tender_not_found,
    dateModified_tender,
    patch_not_author,
    tender_items_float_quantity,
    tender_items_negative_quantity,
    patch_tender_jsonpatch,
    tender_funders,
    tender_with_main_procurement_category,
    create_tender_with_inn_before,
    tender_token_invalid,
    create_tender_with_required_unit,
    create_tender_with_earlier_non_required_unit,
    create_tender_config_test,
)


class TenderResourceTestMixin:
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_listing = snitch(listing)
    test_create_tender_draft = snitch(create_tender_draft)
    test_create_tender_draft_with_criteria = snitch(create_tender_draft_with_criteria)
    test_create_tender_draft_with_criteria_expected_values = snitch(create_tender_draft_with_criteria_expected_values)

    test_tender_owner_can_change_in_draft = snitch(tender_owner_can_change_in_draft)
    test_tender_period_update = snitch(tender_period_update)
    test_tender_owner_cannot_change_in_draft = snitch(tender_owner_cannot_change_in_draft)
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
    test_create_tender_config_test = snitch(create_tender_config_test)



@patch("openprocurement.tender.pricequotation.procedure.models.requirement.PQ_CRITERIA_ID_FROM",
       get_now() + timedelta(days=1))
@patch("openprocurement.tender.pricequotation.models.requirement.PQ_CRITERIA_ID_FROM", get_now() + timedelta(days=1))
class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin):
    docservice = True
    initial_data = test_tender_pq_data
    initial_auth = ("Basic", ("broker", ""))
    test_criteria = test_tender_pq_short_profile['criteria']
    test_criteria_1 = test_tender_pq_criteria_1

    Test_guarantee = snitch(guarantee)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_tender_fields = snitch(tender_fields)
    test_tender_items_float_quantity = snitch(tender_items_float_quantity)
    test_tender_items_negative_quantity = snitch(tender_items_negative_quantity)
    test_patch_tender_jsonpatch = snitch(patch_tender_jsonpatch)
    test_patch_tender = snitch(patch_tender)
    test_required_field_deletion = snitch(required_field_deletion)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_create_tender_with_inn_before = snitch(create_tender_with_inn_before)
    test_patch_tender_by_pq_bot_before_multiprofile = snitch(patch_tender_by_pq_bot_before_multiprofile)
    test_patch_tender_by_pq_bot_after_multiprofile = snitch(patch_tender_by_pq_bot_after_multiprofile)
    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_patch_tender_status = snitch(patch_tender_status)
    test_create_pricequotation_tender_with_earlier_non_required_unit = snitch(
        create_tender_with_earlier_non_required_unit
    )
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_tender_criteria_values_type = snitch(tender_criteria_values_type)


@patch("openprocurement.tender.pricequotation.procedure.models.requirement.PQ_CRITERIA_ID_FROM",
       get_now() - timedelta(days=1))
@patch("openprocurement.tender.pricequotation.models.requirement.PQ_CRITERIA_ID_FROM", get_now() - timedelta(days=1))
class MD5UidTenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin):
    docservice = True
    initial_data = test_tender_pq_data
    initial_auth = ("Basic", ("broker", ""))

    test_criteria_1 = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_1))
    test_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_short_profile['criteria']))


@patch("openprocurement.tender.pricequotation.procedure.models.requirement.PQ_CRITERIA_ID_FROM",
       get_now() + timedelta(days=1))
@patch("openprocurement.tender.pricequotation.models.requirement.PQ_CRITERIA_ID_FROM", get_now() + timedelta(days=1))
class TenderProcessTest(TenderContentWebTest):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_pq_data
    initial_status = 'active.tendering'
    need_tender = True
    docservice = True

    test_one_valid_bid_tender = snitch(one_valid_bid_tender)
    test_one_invalid_bid_tender = snitch(one_invalid_bid_tender)
    test_first_bid_tender = snitch(first_bid_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderProcessTest))
    suite.addTest(unittest.makeSuite(TenderResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
