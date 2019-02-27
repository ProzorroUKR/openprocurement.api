# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.agreement.cfaua.tests.agreement_blanks import (
    # TestTenderAgreement
    create_agreement,
    create_agreement_with_documents,
    create_agreement_with_features,
    patch_agreement_features_invalid,
    # AgreementResources
    get_agreements_by_id,
    extract_credentials,
    agreement_patch_invalid,
    # AgreementListingTests
    empty_listing,
    listing,
    agreement_preview,
    agreement_change_item_price_variation_preview,
    agreement_change_party_withdrawal_cancelled_preview,
    agreement_change_party_withdrawal_preview,
    agreement_change_tax_rate_preview,
    agreement_change_third_party_preview,
    agreement_changes_patch_from_agreements,
    create_agreement_with_two_active_contracts
)
from openprocurement.api.tests.base import snitch
import os
from openprocurement.agreement.cfaua.tests.base import (
    TEST_AGREEMENT, TEST_FEATURES, TEST_CHANGE
)
from openprocurement.agreement.core.tests.base import BaseAgreementWebTest, BaseAgreementTest


class AgreementResources(BaseAgreementWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = TEST_AGREEMENT
    initial_change = TEST_CHANGE
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(AgreementResources, self).setUp()

    test_agreement_patch_invalid = snitch(agreement_patch_invalid)
    test_extract_credentials = snitch(extract_credentials)
    test_get_agreements_by_id = snitch(get_agreements_by_id)
    test_agreement_preview = snitch(agreement_preview)
    test_agreement_change_item_price_variation_preview = snitch(agreement_change_item_price_variation_preview)
    test_agreement_change_party_withdrawal_cancelled_preview = \
        snitch(agreement_change_party_withdrawal_cancelled_preview)
    test_agreement_change_party_withdrawal_preview = snitch(agreement_change_party_withdrawal_preview)
    test_agreement_change_tax_rate_preview = snitch(agreement_change_tax_rate_preview)
    test_agreement_change_third_party_preview = snitch(agreement_change_third_party_preview)
    test_agreement_changes_patch_from_agreements = snitch(agreement_changes_patch_from_agreements)


class TestTenderAgreement(BaseAgreementTest):
    features = TEST_FEATURES
    initial_auth = ('Basic', ('agreements', ''))
    initial_data = deepcopy(TEST_AGREEMENT)
    relative_to = os.path.dirname(__file__)

    test_create_agreement = snitch(create_agreement)
    test_create_agreement_with_documents = snitch(create_agreement_with_documents)
    test_create_agreement_with_features = snitch(create_agreement_with_features)
    test_patch_agreement_features_invalid = snitch(patch_agreement_features_invalid)
    test_create_agreement_with_two_active_contracts = snitch(create_agreement_with_two_active_contracts)


class AgreementListingTests(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super(AgreementListingTests, self).setUp()
        self.initial_data = TEST_AGREEMENT

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AgreementResources))
    suite.addTest(unittest.makeSuite(TestTenderAgreement))
    suite.addTest(unittest.makeSuite(AgreementListingTests))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')