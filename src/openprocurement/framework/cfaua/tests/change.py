import os
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.framework.cfaua.tests.base import (
    BaseAgreementContentWebTest,
    BaseAgreementTest,
)
from openprocurement.framework.cfaua.tests.change_blanks import (
    activate_change_after_1_cancelled,
    change_date_signed,
    change_date_signed_very_old_agreements_data,
    create_change,
    create_change_invalid,
    create_change_item_price_variation_modifications_boundaries,
    date_signed_on_change_creation,
    date_signed_on_change_creation_for_very_old_agreements_data,
    get_change,
    multi_change,
    no_items_agreement_change,
    not_found,
    patch_change,
)
from openprocurement.framework.cfaua.tests.data import test_agreement_data


class AgreementNoItemsChangeTest(BaseAgreementTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_agreement_data
    test_no_items_agreement_change = snitch(no_items_agreement_change)


class AgreementChangesResourceTest(BaseAgreementContentWebTest):
    test_not_found = snitch(not_found)
    test_get_change = snitch(get_change)
    test_create_change_invalid = snitch(create_change_invalid)
    test_create_change = snitch(create_change)
    test_create_change_item_price_variation_modifications_boundaries = snitch(
        create_change_item_price_variation_modifications_boundaries
    )
    test_patch_change = snitch(patch_change)
    test_multi_change = snitch(multi_change)
    test_change_date_signed = snitch(change_date_signed)
    test_date_signed_on_change_creation = snitch(date_signed_on_change_creation)
    test_change_date_signed_very_old_agreements_data = snitch(change_date_signed_very_old_agreements_data)
    test_date_signed_on_change_creation_for_very_old_agreements_data = snitch(
        date_signed_on_change_creation_for_very_old_agreements_data
    )
    test_activate_change_after_1_cancelled = snitch(activate_change_after_1_cancelled)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(AgreementNoItemsChangeTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(AgreementChangesResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
