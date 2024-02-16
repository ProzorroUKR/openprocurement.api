import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.framework.dps.tests.base import (
    BaseApiWebTest,
    BaseFrameworkWebTest,
    test_framework_dps_data,
)
from openprocurement.framework.dps.tests.framework_blanks import (
    accreditation_level,
    complete_status,
    create_framework_config_restricted,
    create_framework_config_test,
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
    patch_framework_active,
    patch_framework_draft,
    patch_framework_draft_to_active,
    patch_framework_draft_to_active_invalid,
    periods_deletion,
    simple_add_framework,
    unsuccessful_status,
)


class FrameworkTest(BaseApiWebTest):
    initial_data = test_framework_dps_data

    test_simple_add_framework = snitch(simple_add_framework)


class FrameworkResourceTest(BaseFrameworkWebTest):
    initial_data = test_framework_dps_data
    initial_auth = ("Basic", ("broker", ""))

    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_listing = snitch(listing)
    test_create_framework_draft = snitch(create_framework_draft)
    test_create_framework_config_test = snitch(create_framework_config_test)
    test_create_framework_config_restricted = snitch(create_framework_config_restricted)
    test_accreditation_level = snitch(accreditation_level)
    test_create_framework_draft_invalid = snitch(create_framework_draft_invalid)
    test_create_framework_draft_invalid_kind = snitch(create_framework_draft_invalid_kind)
    test_create_framework_draft_url_validation = snitch(create_framework_draft_url_validation)
    test_patch_framework_draft = snitch(patch_framework_draft)
    test_patch_framework_draft_to_active = snitch(patch_framework_draft_to_active)
    test_patch_framework_draft_to_active_invalid = snitch(patch_framework_draft_to_active_invalid)
    test_patch_framework_active = snitch(patch_framework_active)
    test_get_framework = snitch(get_framework)
    test_unsuccessful_status = snitch(unsuccessful_status)
    test_complete_status = snitch(complete_status)

    test_date_framework = snitch(date_framework)
    test_dateModified_framework = snitch(dateModified_framework)
    test_periods_deletion = snitch(periods_deletion)
    test_framework_not_found = snitch(framework_not_found)
    test_framework_token_invalid = snitch(framework_token_invalid)
    test_framework_fields = snitch(framework_fields)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(FrameworkTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(FrameworkResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
