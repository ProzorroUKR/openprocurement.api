# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.contracting.api.tests.base import BaseContractContentWebTest, BaseContractTest
from openprocurement.contracting.api.tests.data import test_contract_data
from openprocurement.contracting.api.tests.change_blanks import (
    no_items_contract_change,
    not_found,
    get_change,
    create_change_invalid,
    create_change,
    patch_change,
    change_date_signed,
    date_signed_on_change_creation,
    change_date_signed_very_old_contracts_data,
    date_signed_on_change_creation_for_very_old_contracts_data,
    patch_change_after_contract_is_already_terminated,
)


class ContractNoItemsChangeTest(BaseContractTest):
    initial_data = test_contract_data
    test_no_items_contract_change = snitch(no_items_contract_change)


class ContractChangesResourceTest(BaseContractContentWebTest):

    test_not_found = snitch(not_found)
    test_get_change = snitch(get_change)
    test_create_change_invalid = snitch(create_change_invalid)
    test_create_change = snitch(create_change)
    test_patch_change = snitch(patch_change)
    test_change_date_signed = snitch(change_date_signed)
    test_date_signed_on_change_creation = snitch(date_signed_on_change_creation)
    test_change_date_signed_very_old_contracts_data = snitch(change_date_signed_very_old_contracts_data)
    test_date_signed_on_change_creation_for_very_old_contracts_data = snitch(
        date_signed_on_change_creation_for_very_old_contracts_data
    )
    test_patch_change_after_contract_is_already_terminated = snitch(patch_change_after_contract_is_already_terminated)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractNoItemsChangeTest))
    suite.addTest(unittest.makeSuite(ContractChangesResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
