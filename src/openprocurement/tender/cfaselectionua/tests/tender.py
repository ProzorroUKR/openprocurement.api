import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    create_tender_central,
    create_tender_central_invalid,
    create_tender_config_test,
    patch_tender_lots_none,
    tender_milestones_not_required,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    BaseTenderWebTest,
    test_tender_cfaselectionua_agreement,
    test_tender_cfaselectionua_agreement_features,
    test_tender_cfaselectionua_data,
    test_tender_cfaselectionua_lots,
)
from openprocurement.tender.cfaselectionua.tests.tender_blanks import (
    create_tender,
    create_tender_draft,
    create_tender_from_agreement_with_changes,
    create_tender_from_agreement_with_features,
    create_tender_from_agreement_with_features_0_3,
    create_tender_from_agreement_with_invalid_changes,
    create_tender_from_terminated_agreement,
    create_tender_generated,
    create_tender_invalid,
    create_tender_with_available_language,
    create_tender_with_value,
    dateModified_tender,
    edit_tender_in_active_enquiries,
    first_bid_tender,
    get_tender,
    invalid_tender_conditions,
    listing,
    listing_changes,
    listing_draft,
    lost_contract_for_active_award,
    one_invalid_bid_tender,
    one_valid_bid_tender,
    patch_not_author,
    patch_tender,
    patch_tender_bot,
    patch_tender_jsonpatch,
    patch_tender_to_draft_pending,
    tender_features_invalid,
    tender_fields,
    tender_funders,
    tender_not_found,
)
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.tender.core.tests.utils import set_tender_lots
from openprocurement.tender.open.tests.tender_blanks import create_tender_invalid_config

test_tender_cfaselectionua_data = deepcopy(test_tender_cfaselectionua_data)
set_tender_lots(test_tender_cfaselectionua_data, test_tender_cfaselectionua_lots)
test_tender_cfaselectionua_lots = deepcopy(test_tender_cfaselectionua_data["lots"])


class TenderResourceTestMixin:
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_listing = snitch(listing)
    test_create_tender_draft = snitch(create_tender_draft)
    test_create_tender = snitch(create_tender)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_create_tender_from_terminated_agreement = snitch(create_tender_from_terminated_agreement)
    test_create_tender_from_agreement_with_changes = snitch(create_tender_from_agreement_with_changes)
    test_create_tender_from_agreement_with_invalid_changes = snitch(create_tender_from_agreement_with_invalid_changes)
    test_create_tender_from_agreement_with_features = snitch(create_tender_from_agreement_with_features)
    test_create_tender_from_agreement_with_features_0_3 = snitch(create_tender_from_agreement_with_features_0_3)
    test_create_tender_with_value = snitch(create_tender_with_value)
    # test_tender_features = snitch(tender_features)
    test_get_tender = snitch(get_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_patch_not_author = snitch(patch_not_author)
    test_tender_funders = snitch(tender_funders)
    test_patch_tender_bot = snitch(patch_tender_bot)
    test_create_tender_with_available_language = snitch(create_tender_with_available_language)
    test_create_tender_config_test = snitch(create_tender_config_test)


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin):
    initial_data = test_tender_cfaselectionua_data
    primary_tender_status = "draft"
    initial_auth = ("Basic", ("broker", ""))
    initial_agreement = test_tender_cfaselectionua_agreement
    initial_agreement_with_features = test_tender_cfaselectionua_agreement_features
    test_lots_data = test_tender_cfaselectionua_lots
    initial_criteria = test_exclusion_criteria + test_language_criteria

    agreement_id = "11111111111111111111111111111111"

    # test_guarantee = snitch(guarantee)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_create_tender_generated = snitch(create_tender_generated)
    test_tender_fields = snitch(tender_fields)
    test_patch_tender_jsonpatch = snitch(patch_tender_jsonpatch)
    test_patch_tender = snitch(patch_tender)
    test_patch_tender_to_draft_pending = snitch(patch_tender_to_draft_pending)
    test_edit_tender_in_active_enquiries = snitch(edit_tender_in_active_enquiries)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_milestones_not_required = snitch(tender_milestones_not_required)


class TenderProcessTest(BaseTenderWebTest):
    initial_data = test_tender_cfaselectionua_data
    primary_tender_status = "draft"
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
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
