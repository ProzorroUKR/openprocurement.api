import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.contracting.econtract.tests.base import BaseEContractContentWebTest
from openprocurement.contracting.econtract.tests.change_blanks import (
    activation_of_change,
    cancellation_of_change,
    change_contract_period,
    change_contract_value_amount,
    change_contract_value_vat_change,
    change_contract_wo_amount_net,
    change_documents,
    change_for_pending_contract_forbidden,
    change_tender_contract_items_change,
    contract_token_invalid,
    create_change,
    create_change_invalid,
    get_change,
    not_found,
    patch_change,
)


class ContractChangesMixin:
    initial_status = "active"

    def activate_change(self, change_id):
        contract_sign_data = {
            "documentType": "contractSignature",
            "title": "sign.p7s",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/pkcs7-signature",
        }
        self.app.post_json(
            f"/contracts/{self.contract_id}/changes/{change_id}/documents?acc_token={self.contract_token}",
            {"data": contract_sign_data},
        )
        # add signature for supplier
        self.app.post_json(
            f"/contracts/{self.contract_id}/changes/{change_id}/documents?acc_token={self.bid_token}",
            {"data": contract_sign_data},
        )


class ContractChangesResourceTest(ContractChangesMixin, BaseEContractContentWebTest):

    test_not_found = snitch(not_found)
    test_get_change = snitch(get_change)
    test_create_change_invalid = snitch(create_change_invalid)
    test_create_change = snitch(create_change)
    test_patch_change = snitch(patch_change)
    # test_patch_change_after_contract_is_already_terminated = snitch(patch_change_after_contract_is_already_terminated)
    test_activation_of_change = snitch(activation_of_change)
    test_cancellation_of_change = snitch(cancellation_of_change)
    test_change_for_pending_contract_forbidden = snitch(change_for_pending_contract_forbidden)
    test_contract_token_invalid = snitch(contract_token_invalid)
    test_change_documents = snitch(change_documents)


class ContractChangesModificationsResourceTest(ContractChangesMixin, BaseEContractContentWebTest):
    test_change_tender_contract_wo_amount_net = snitch(change_contract_wo_amount_net)
    test_change_tender_contract_value_amount = snitch(change_contract_value_amount)
    test_change_tender_contract_value_vat_change = snitch(change_contract_value_vat_change)
    test_change_tender_contract_period = snitch(change_contract_period)
    test_change_tender_contract_items_change = snitch(change_tender_contract_items_change)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractChangesResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ContractChangesModificationsResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
