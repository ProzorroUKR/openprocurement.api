# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.contracting.api.tests.base import (
    test_contract_data,
    test_contract_data_wo_items,
    test_contract_data_wo_value_amount_net,
    BaseWebTest,
    BaseContractWebTest,
    documents,
)
from openprocurement.contracting.api.tests.contract_blanks import (
    # ContractTest
    simple_add_contract,
    # ContractResourceTest
    empty_listing,
    listing,
    listing_changes,
    get_contract,
    not_found,
    create_contract_invalid,
    create_contract_generated,
    create_contract,
    # ContractWDocumentsWithDSResourceTest
    create_contract_w_documents,
    # ContractResource4BrokersTest
    contract_status_change,
    contract_items_change,
    patch_tender_contract,
    # ContractResource4AdministratorTest
    contract_administrator_change,
    # ContractCredentialsTest
    get_credentials,
    generate_credentials,
    # ContractWOItemsResource4BrokersTest
    contract_wo_items_status_change,
    patch_tender_contract_wo_amount_net
)


class ContractTest(BaseWebTest):
    initial_data = test_contract_data

    test_simple_add_contract = snitch(simple_add_contract)


class ContractResourceTest(BaseWebTest):
    """ contract resource test """
    initial_data = test_contract_data

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_get_contract = snitch(get_contract)
    test_not_found = snitch(not_found)
    test_create_contract_invalid = snitch(create_contract_invalid)
    test_create_contract_generated = snitch(create_contract_generated)
    test_create_contract = snitch(create_contract)


class ContractWDocumentsWithDSResourceTest(BaseWebTest):
    docservice = True
    initial_data = deepcopy(test_contract_data)
    documents = deepcopy(documents)
    initial_data['documents'] = documents

    test_create_contract_w_documents = snitch(create_contract_w_documents)


class ContractResource4BrokersTest(BaseContractWebTest):
    """ contract resource test """
    initial_auth = ('Basic', ('broker', ''))

    test_contract_status_change = snitch(contract_status_change)
    test_contract_items_change = snitch(contract_items_change)
    test_patch_tender_contract = snitch(patch_tender_contract)


class ContractResource4AdministratorTest(BaseContractWebTest):
    """ contract resource test """
    initial_auth = ('Basic', ('administrator', ''))

    test_contract_administrator_change = snitch(contract_administrator_change)


class ContractCredentialsTest(BaseContractWebTest):
    """ Contract credentials tests """

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_contract_data

    test_get_credentials = snitch(get_credentials)
    test_generate_credentials = snitch(generate_credentials)


class ContractWOItemsResource4BrokersTest(BaseContractWebTest):
    initial_data = test_contract_data_wo_items
    initial_auth = ('Basic', ('broker', ''))

    test_contract_wo_items_status_change = snitch(contract_wo_items_status_change)


class ContractWOAmountNetResource4BrokersTest(BaseContractWebTest):
    """ contract resource test """
    initial_data = test_contract_data_wo_value_amount_net
    initial_auth = ('Basic', ('broker', ''))

    test_patch_tender_contract = snitch(patch_tender_contract_wo_amount_net)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractTest))
    suite.addTest(unittest.makeSuite(ContractResourceTest))
    suite.addTest(unittest.makeSuite(ContractWDocumentsWithDSResourceTest))
    suite.addTest(unittest.makeSuite(ContractResource4BrokersTest))
    suite.addTest(unittest.makeSuite(ContractResource4AdministratorTest))
    suite.addTest(unittest.makeSuite(ContractCredentialsTest))
    suite.addTest(unittest.makeSuite(ContractWOItemsResource4BrokersTest))
    suite.addTest(unittest.makeSuite(ContractWOAmountNetResource4BrokersTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
