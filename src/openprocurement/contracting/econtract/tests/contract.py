import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.contracting.core.tests.base import (
    BaseContractTest,
    BaseContractWebTestTwoItems,
)
from openprocurement.contracting.core.tests.contract_blanks import (
    cancel_tender_award,
    contract_administrator_change,
    contract_update_add_remove_items,
    create_contract_transfer_token,
    create_contract_w_documents,
    empty_listing,
    get_contract,
    listing,
    listing_changes,
    not_found,
    put_transaction_to_contract,
    simple_add_contract,
)
from openprocurement.contracting.econtract.tests.base import (
    BaseEContractContentWebTest,
    BaseEContractWebTest,
)
from openprocurement.contracting.econtract.tests.contract_blanks import (
    post_new_version_of_contract,
)
from openprocurement.contracting.econtract.tests.data import test_econtract_data


class ContractListingTests(BaseContractTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_econtract_data

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)


class ContractResourceTest(BaseContractTest):
    initial_data = test_econtract_data

    test_simple_add_contract = snitch(simple_add_contract)
    test_get_contract = snitch(get_contract)
    test_not_found = snitch(not_found)
    test_create_contract_transfer_token = snitch(create_contract_transfer_token)
    test_create_contract_w_documents = snitch(create_contract_w_documents)


class ContractResource4BrokersTest(BaseEContractContentWebTest):
    test_cancel_tender_award = snitch(cancel_tender_award)
    test_put_transaction_to_contract = snitch(put_transaction_to_contract)
    test_post_new_version_of_contract = snitch(post_new_version_of_contract)


class ContractActiveResource4BrokersTest(BaseEContractContentWebTest):
    initial_status = "active"

    # TODO: add these tests after amountPaid will be added on PATCH or via change
    # test_patch_tender_contract_identical = snitch(patch_tender_contract_identical)
    # test_patch_tender_contract_single_request = snitch(patch_tender_contract_single_request)
    # test_patch_tender_contract_without_value = snitch(patch_tender_contract_without_value)
    # test_patch_tender_contract_amount_paid_zero = snitch(patch_tender_contract_amount_paid_zero)


class ContractResource4BrokersTestMultipleItems(BaseContractWebTestTwoItems):
    test_contract_update_add_remove_items = snitch(contract_update_add_remove_items)


class ContractResource4AdministratorTest(BaseEContractWebTest):
    initial_auth = ("Basic", ("administrator", ""))

    test_contract_administrator_change = snitch(contract_administrator_change)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractResource4BrokersTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractActiveResource4BrokersTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractResource4AdministratorTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
