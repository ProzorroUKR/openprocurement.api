# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import (
    snitch
)

from openprocurement.contracting.api.tests.base import (
    BaseWebTest,
    BaseContractContentWebTest,
    test_contract_data
)
from openprocurement.contracting.api.tests.change_blanks import (
    # ContractNoItemsChangeTest
    no_items_contract_change,
    # ContractChangesResourceTest
    not_found,
    get_change,
    create_change_invalid,
    create_change,
    patch_change,
    change_date_signed,
    date_signed_on_change_creation,
    change_date_signed_very_old_contracts_data,
    date_signed_on_change_creation_for_very_old_contracts_data,
)


class ContractNoItemsChangeTest(BaseWebTest):
    initial_data = test_contract_data
    test_no_items_contract_change = snitch(no_items_contract_change)


class ContractChangesResourceTest(BaseContractContentWebTest):
    initial_auth = ('Basic', ('broker', ''))

    test_not_found = snitch(not_found)
    test_get_change = snitch(get_change)
    test_create_change_invalid = snitch(create_change_invalid)
    test_create_change = snitch(create_change)
    test_patch_change = snitch(patch_change)
    test_change_date_signed = snitch(change_date_signed)
    test_date_signed_on_change_creation = snitch(date_signed_on_change_creation)
    test_change_date_signed_very_old_contracts_data = snitch(change_date_signed_very_old_contracts_data)
    test_date_signed_on_change_creation_for_very_old_contracts_data  = snitch(date_signed_on_change_creation_for_very_old_contracts_data)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite())
    suite.addTest(unittest.makeSuite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
