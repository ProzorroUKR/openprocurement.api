# -*- coding: utf-8 -*-
import unittest

from openprocurement.agreement.cfaua.tests.agreement_blanks import (
    create_agreement,
    get_agreements_by_id,
    extract_credentials,
    agreement_patch_invalid,
    empty_listing,
    listing
)
from openprocurement.api.tests.base import snitch
import os
from openprocurement.agreement.cfaua.tests.base import TEST_AGREEMENT
from openprocurement.agreement.core.tests.base import BaseAgreementWebTest, BaseAgreementTest


class AgreementResources(BaseAgreementWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = TEST_AGREEMENT
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(AgreementResources, self).setUp()

    test_agreement_patch_invalid = snitch(agreement_patch_invalid)
    test_extract_credentials = snitch(extract_credentials)
    test_get_agreements_by_id = snitch(get_agreements_by_id)


class AgreementCreationTests(BaseAgreementWebTest):
    initial_data = TEST_AGREEMENT
    relative_to = os.path.dirname(__file__)

    def test_id(self):
        self.assertIsNotNone(self.agreement_id)
        self.assertIsNotNone(self.agreement_token)

    test_create_agreement = snitch(create_agreement)


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
    suite.addTest(unittest.makeSuite(AgreementCreationTests))
    suite.addTest(unittest.makeSuite(AgreementListingTests))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')