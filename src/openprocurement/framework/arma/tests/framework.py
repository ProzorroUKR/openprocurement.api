import unittest

from openprocurement.api.constants import KIND_FRAMEWORK_TYPE_MAPPING
from openprocurement.api.tests.base import snitch
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.arma.tests.base import (
    BaseApiWebTest,
    BaseFrameworkWebTest,
    test_framework_arma_data,
)
from openprocurement.framework.arma.tests.framework_blanks import (
    arma_change_period_recalculation,
    arma_period_calculation,
    arma_successful_status_without_submissions,
    arma_validate_procurement_entity_kind,
)
from openprocurement.framework.dps.tests.framework_blanks import (
    accreditation_level,
    additional_classifications_deletion,
    complete_status,
    create_framework_draft,
    create_framework_draft_invalid,
    create_framework_draft_invalid_kind,
    create_framework_draft_url_validation,
    date_framework,
    dateModified_framework,
    framework_fields,
    framework_not_found,
    framework_token_invalid,
    get_framework,
    listing,
    listing_changes,
    listing_draft,
    modify_framework_period,
    patch_framework_active,
    patch_framework_draft,
    patch_framework_draft_to_active,
    patch_framework_draft_to_active_invalid,
    periods_deletion,
    simple_add_framework,
    validate_procurement_entity_kind_patch,
)


class FrameworkTest(BaseApiWebTest):
    initial_data = test_framework_arma_data

    test_simple_add_framework = snitch(simple_add_framework)


class FrameworkResourceTest(BaseFrameworkWebTest):
    initial_data = test_framework_arma_data
    initial_auth = ("Basic", ("broker", ""))
    allowed_proc_entity_kinds = KIND_FRAMEWORK_TYPE_MAPPING[ARMA_TYPE]

    min_submissions_number = 0
    min_submissions_number_days = 0
    min_submissions_number_working_days = False
    min_qualification_duration = 365

    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_listing = snitch(listing)
    test_create_framework_draft = snitch(create_framework_draft)
    test_accreditation_level = snitch(accreditation_level)
    test_create_framework_draft_invalid = snitch(create_framework_draft_invalid)
    test_create_framework_draft_invalid_kind = snitch(create_framework_draft_invalid_kind)
    test_create_framework_draft_url_validation = snitch(create_framework_draft_url_validation)
    test_patch_framework_draft = snitch(patch_framework_draft)
    test_patch_framework_draft_to_active = snitch(patch_framework_draft_to_active)
    test_patch_framework_draft_to_active_invalid = snitch(patch_framework_draft_to_active_invalid)
    test_patch_framework_active = snitch(patch_framework_active)
    test_get_framework = snitch(get_framework)
    test_complete_status = snitch(complete_status)

    test_date_framework = snitch(date_framework)
    test_dateModified_framework = snitch(dateModified_framework)
    test_periods_deletion = snitch(periods_deletion)
    test_additional_classifications_deletion = snitch(additional_classifications_deletion)
    test_framework_not_found = snitch(framework_not_found)
    test_framework_token_invalid = snitch(framework_token_invalid)
    test_framework_fields = snitch(framework_fields)
    test_modify_framework_period = snitch(modify_framework_period)
    test_validate_procurement_entity_kind = snitch(arma_validate_procurement_entity_kind)
    test_validate_procurement_entity_kind_patch = snitch(validate_procurement_entity_kind_patch)

    test_arma_period_calculation = snitch(arma_period_calculation)
    test_arma_change_period_recalculation = snitch(arma_change_period_recalculation)
    test_arma_successful_status_without_submissions = snitch(arma_successful_status_without_submissions)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(FrameworkTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(FrameworkResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
