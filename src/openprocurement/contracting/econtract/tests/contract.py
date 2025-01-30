import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.contracting.econtract.tests.base import (
    BaseEContractTest,
    BaseEContractWebTest,
    BaseEContractWebTestTwoItems,
)
from openprocurement.contracting.econtract.tests.contract_blanks import (
    cancel_tender_award,
    contract_activate,
    contract_administrator_change,
    contract_cancelled,
    contract_date_signed,
    contract_items_change,
    contract_status_change,
    contract_token_invalid,
    contract_update_add_remove_items,
    contract_wo_items_status_change,
    create_contract_transfer_token,
    create_contract_w_documents,
    empty_listing,
    generate_credentials,
    generate_credentials_invalid,
    get_contract,
    get_credentials,
    listing,
    listing_changes,
    not_found,
    patch_tender_contract,
    patch_tender_contract_amount_paid_zero,
    patch_tender_contract_identical,
    patch_tender_contract_milestones,
    patch_tender_contract_period,
    patch_tender_contract_readonly,
    patch_tender_contract_single_request,
    patch_tender_contract_value_amount,
    patch_tender_contract_value_vat_change,
    patch_tender_contract_without_value,
    patch_tender_contract_wo_amount_net,
    put_transaction_to_contract,
    simple_add_contract,
)
from openprocurement.contracting.econtract.tests.data import (
    test_contract_data,
    test_contract_data_wo_items,
    test_contract_data_wo_value_amount_net,
)


class ContractListingTests(BaseEContractTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_contract_data

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)


class ContractResourceTest(BaseEContractTest):
    initial_data = test_contract_data

    test_simple_add_contract = snitch(simple_add_contract)
    test_get_contract = snitch(get_contract)
    test_not_found = snitch(not_found)
    test_create_contract_transfer_token = snitch(create_contract_transfer_token)
    test_create_contract_w_documents = snitch(create_contract_w_documents)


class ContractResource4BrokersTest(BaseEContractWebTest):
    test_contract_token_invalid = snitch(contract_token_invalid)
    test_contract_date_signed = snitch(contract_date_signed)
    test_contract_status_change = snitch(contract_status_change)
    test_contract_cancelled = snitch(contract_cancelled)
    test_cancel_tender_award = snitch(cancel_tender_award)
    test_contract_items_change = snitch(contract_items_change)
    test_contract_activate = snitch(contract_activate)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_readonly = snitch(patch_tender_contract_readonly)
    test_get_credentials = snitch(get_credentials)
    test_generate_credentials_invalid = snitch(generate_credentials_invalid)
    test_put_transaction_to_contract = snitch(put_transaction_to_contract)


class ContractActiveResource4BrokersTest(BaseEContractWebTest):
    initial_status = "active"

    test_generate_credentials = snitch(generate_credentials)
    test_patch_tender_contract_identical = snitch(patch_tender_contract_identical)
    test_patch_tender_contract_value_vat_change = snitch(patch_tender_contract_value_vat_change)
    test_patch_tender_contract_single_request = snitch(patch_tender_contract_single_request)
    test_patch_tender_contract_value_amount = snitch(patch_tender_contract_value_amount)
    test_patch_tender_contract_without_value = snitch(patch_tender_contract_without_value)
    test_patch_tender_contract_amount_paid_zero = snitch(patch_tender_contract_amount_paid_zero)
    test_patch_tender_contract_period = snitch(patch_tender_contract_period)
    test_patch_tender_contract_milestones = snitch(patch_tender_contract_milestones)


class ContractResource4BrokersTestMultipleItems(BaseEContractWebTestTwoItems):
    test_contract_update_add_remove_items = snitch(contract_update_add_remove_items)


class ContractResource4AdministratorTest(BaseEContractWebTest):
    initial_auth = ("Basic", ("administrator", ""))

    test_contract_administrator_change = snitch(contract_administrator_change)


class ContractWOItemsResource4BrokersTest(BaseEContractWebTest):
    initial_data = test_contract_data_wo_items

    test_contract_wo_items_status_change = snitch(contract_wo_items_status_change)


class ContractWOAmountNetResource4BrokersTest(BaseEContractWebTest):
    initial_status = "active"
    initial_data = test_contract_data_wo_value_amount_net

    test_patch_tender_contract = snitch(patch_tender_contract_wo_amount_net)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractResource4BrokersTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractActiveResource4BrokersTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractResource4AdministratorTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractWOItemsResource4BrokersTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractWOAmountNetResource4BrokersTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
