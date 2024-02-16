import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.framework.cfaua.tests.agreement_blanks import (
    agreement_change_item_price_variation_preview,
    agreement_change_party_withdrawal_cancelled_preview,
    agreement_change_party_withdrawal_preview,
    agreement_change_tax_rate_preview,
    agreement_change_third_party_preview,
    agreement_changes_patch_from_agreements,
    agreement_patch_invalid,
    agreement_preview,
    agreement_token_invalid,
    create_agreement,
    create_agreement_with_documents,
    create_agreement_with_features,
    create_agreement_with_two_active_contracts,
    empty_listing,
    generate_credentials,
    generate_credentials_invalid,
    get_agreements_by_id,
    listing,
    skip_address_validation,
)
from openprocurement.framework.cfaua.tests.base import (
    BaseAgreementContentWebTest,
    BaseAgreementTest,
)
from openprocurement.framework.cfaua.tests.data import (
    TEST_AGREEMENT,
    TEST_CHANGE,
    TEST_FEATURES,
)


class AgreementListingTests(BaseAgreementTest):
    initial_data = TEST_AGREEMENT

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)


class AgreementResourceTest(BaseAgreementTest):
    features = TEST_FEATURES
    initial_data = deepcopy(TEST_AGREEMENT)

    test_create_agreement = snitch(create_agreement)
    test_create_agreement_with_documents = snitch(create_agreement_with_documents)
    test_create_agreement_with_features = snitch(create_agreement_with_features)
    test_create_agreement_with_two_active_contracts = snitch(create_agreement_with_two_active_contracts)
    test_skip_address_validation = snitch(skip_address_validation)


class AgreementResourceTest4BrokerTest(BaseAgreementContentWebTest):
    initial_change = TEST_CHANGE

    test_agreement_token_invalid = snitch(agreement_token_invalid)
    test_agreement_patch_invalid = snitch(agreement_patch_invalid)
    test_generate_credentials = snitch(generate_credentials)
    test_generate_credentials_invalid = snitch(generate_credentials_invalid)
    test_get_agreements_by_id = snitch(get_agreements_by_id)
    test_agreement_preview = snitch(agreement_preview)
    test_agreement_change_item_price_variation_preview = snitch(agreement_change_item_price_variation_preview)
    test_agreement_change_party_withdrawal_cancelled_preview = snitch(
        agreement_change_party_withdrawal_cancelled_preview
    )
    test_agreement_change_party_withdrawal_preview = snitch(agreement_change_party_withdrawal_preview)
    test_agreement_change_tax_rate_preview = snitch(agreement_change_tax_rate_preview)
    test_agreement_change_third_party_preview = snitch(agreement_change_third_party_preview)
    test_agreement_changes_patch_from_agreements = snitch(agreement_changes_patch_from_agreements)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(AgreementResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(AgreementResourceTest4BrokerTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(AgreementListingTests))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
