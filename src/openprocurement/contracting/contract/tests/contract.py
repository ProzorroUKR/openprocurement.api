import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.contracting.contract.tests.base import BaseContractContentWebTest
from openprocurement.contracting.core.tests.base import (
    BaseContractTest,
    BaseContractWebTest,
)
from openprocurement.contracting.core.tests.contract_blanks import (
    cancel_tender_award,
    contract_activate,
    contract_administrator_change,
    contract_cancelled,
    contract_date_signed,
    contract_items_change,
    contract_status_change,
    contract_token_invalid,
    contract_update_add_remove_items,
    contract_validate_signer_info,
    contract_wo_items_status_change,
    create_contract_transfer_token,
    empty_listing,
    get_contract,
    listing,
    listing_changes,
    not_found,
    patch_tender_contract,
    patch_tender_contract_amount_paid_zero,
    patch_tender_contract_identical,
    patch_tender_contract_period,
    patch_tender_contract_readonly,
    patch_tender_contract_single_request,
    patch_tender_contract_value_amount,
    patch_tender_contract_value_vat_change,
    patch_tender_contract_without_value,
    patch_tender_contract_wo_amount_net,
    put_transaction_to_contract,
)
from openprocurement.contracting.core.tests.data import (
    test_contract_data,
    test_contract_data_second_item,
)


class ContractListingTests(BaseContractTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_contract_data = test_contract_data

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)


class ContractResourceTest(BaseContractContentWebTest):
    test_get_contract = snitch(get_contract)
    test_not_found = snitch(not_found)
    test_create_contract_transfer_token = snitch(create_contract_transfer_token)


class ContractResource4BrokersTest(BaseContractContentWebTest):
    test_contract_token_invalid = snitch(contract_token_invalid)
    test_contract_date_signed = snitch(contract_date_signed)
    test_contract_status_change = snitch(contract_status_change)
    test_contract_cancelled = snitch(contract_cancelled)
    test_cancel_tender_award = snitch(cancel_tender_award)
    test_contract_items_change = snitch(contract_items_change)
    test_contract_activate = snitch(contract_activate)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_readonly = snitch(patch_tender_contract_readonly)
    test_put_transaction_to_contract = snitch(put_transaction_to_contract)


class ContractActiveResource4BrokersTest(BaseContractContentWebTest):
    initial_contract_status = "active"

    test_patch_tender_contract_identical = snitch(patch_tender_contract_identical)
    test_patch_tender_contract_value_vat_change = snitch(patch_tender_contract_value_vat_change)
    test_patch_tender_contract_single_request = snitch(patch_tender_contract_single_request)
    test_patch_tender_contract_value_amount = snitch(patch_tender_contract_value_amount)
    test_patch_tender_contract_without_value = snitch(patch_tender_contract_without_value)
    test_patch_tender_contract_amount_paid_zero = snitch(patch_tender_contract_amount_paid_zero)
    test_patch_tender_contract_period = snitch(patch_tender_contract_period)


class ContractResource4BrokersTestMultipleItems(BaseContractContentWebTest):
    def setUp(self):
        super().setUp()
        contract_doc = self.mongodb.contracts.get(self.contract_id)
        contract_doc['items'].append(test_contract_data_second_item)
        self.mongodb.contracts.save(contract_doc)

    test_contract_update_add_remove_items = snitch(contract_update_add_remove_items)


class ContractResource4AdministratorTest(BaseContractWebTest):
    test_contract_administrator_change = snitch(contract_administrator_change)


class ContractWOItemsResource4BrokersTest(BaseContractContentWebTest):
    def setUp(self):
        super().setUp()
        contract_doc = self.mongodb.contracts.get(self.contract_id)
        del contract_doc['items']
        self.mongodb.contracts.save(contract_doc)

    test_contract_wo_items_status_change = snitch(contract_wo_items_status_change)
    test_contract_validate_signer_info = snitch(contract_validate_signer_info)


class ContractWOAmountNetResource4BrokersTest(BaseContractContentWebTest):
    initial_contract_status = "active"

    def setUp(self):
        super().setUp()
        contract_doc = self.mongodb.contracts.get(self.contract_id)
        del contract_doc['value']['amountNet']
        self.mongodb.contracts.save(contract_doc)

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
