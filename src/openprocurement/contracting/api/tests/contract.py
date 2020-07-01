# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.contracting.api.tests.base import BaseContractWebTest, BaseContractTest
from openprocurement.contracting.api.tests.data import (
    test_contract_data,
    test_contract_data_wo_items,
    test_contract_data_wo_value_amount_net,
)
from openprocurement.contracting.api.tests.contract_blanks import (
    empty_listing,
    listing,
    listing_changes,
    get_contract,
    not_found,
    create_contract_invalid,
    create_contract_generated,
    create_contract,
    create_contract_transfer_token,
    simple_add_contract,
    create_contract_w_documents,
    contract_administrator_change,
    contract_token_invalid,
    contract_status_change,
    contract_items_change,
    patch_tender_contract,
    patch_tender_contract_identical,
    patch_tender_contract_readonly,
    patch_tender_contract_amount,
    patch_tender_contract_amount_paid_zero,
    patch_tender_contract_before_vat,
    patch_tender_contract_readonly_before_vat,
    patch_tender_contract_before_vat_single_request,
    get_credentials,
    generate_credentials,
    generate_credentials_invalid,
    contract_wo_items_status_change,
    patch_tender_contract_wo_amount_net,
    patch_tender_without_value,
    skip_address_validation,
    put_transaction_to_contract,
)


class ContractListingTests(BaseContractTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_contract_data
    docservice = True

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)


class ContractResourceTest(BaseContractTest):
    initial_data = test_contract_data
    docservice = True
    initial_auth = ("Basic", ("contracting", ""))

    test_simple_add_contract = snitch(simple_add_contract)
    test_get_contract = snitch(get_contract)
    test_not_found = snitch(not_found)
    test_create_contract_invalid = snitch(create_contract_invalid)
    test_create_contract_generated = snitch(create_contract_generated)
    test_create_contract = snitch(create_contract)
    test_create_contract_transfer_token = snitch(create_contract_transfer_token)
    test_create_contract_w_documents = snitch(create_contract_w_documents)
    test_skip_address_validation = snitch(skip_address_validation)


class ContractResource4BrokersTest(BaseContractWebTest):
    test_contract_token_invalid = snitch(contract_token_invalid)
    test_contract_status_change = snitch(contract_status_change)
    test_contract_items_change = snitch(contract_items_change)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_identical = snitch(patch_tender_contract_identical)
    test_patch_tender_contract_readonly = snitch(patch_tender_contract_readonly)
    test_patch_tender_contract_readonly_before_vat = snitch(patch_tender_contract_readonly_before_vat)
    test_patch_tender_without_value = snitch(patch_tender_without_value)
    test_patch_tender_contract_amount = snitch(patch_tender_contract_amount)
    test_patch_tender_contract_amount_paid_zero = snitch(patch_tender_contract_amount_paid_zero)
    test_patch_tender_contract_before_vat = snitch(patch_tender_contract_before_vat)
    test_patch_tender_contract_before_vat_single_request = snitch(patch_tender_contract_before_vat_single_request)
    test_get_credentials = snitch(get_credentials)
    test_generate_credentials = snitch(generate_credentials)
    test_generate_credentials_invalid = snitch(generate_credentials_invalid)
    test_put_transaction_to_contract = snitch(put_transaction_to_contract)


class ContractResource4AdministratorTest(BaseContractWebTest):
    initial_auth = ("Basic", ("administrator", ""))

    test_contract_administrator_change = snitch(contract_administrator_change)


class ContractWOItemsResource4BrokersTest(BaseContractWebTest):
    initial_data = test_contract_data_wo_items

    test_contract_wo_items_status_change = snitch(contract_wo_items_status_change)


class ContractWOAmountNetResource4BrokersTest(BaseContractWebTest):
    initial_data = test_contract_data_wo_value_amount_net

    test_patch_tender_contract = snitch(patch_tender_contract_wo_amount_net)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractResourceTest))
    suite.addTest(unittest.makeSuite(ContractResource4BrokersTest))
    suite.addTest(unittest.makeSuite(ContractResource4AdministratorTest))
    suite.addTest(unittest.makeSuite(ContractWOItemsResource4BrokersTest))
    suite.addTest(unittest.makeSuite(ContractWOAmountNetResource4BrokersTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
