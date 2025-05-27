import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier
from openprocurement.tender.belowthreshold.tests.contract_blanks import (
    patch_contract_multi_items_unit_value,
    patch_contract_single_item_unit_value,
    patch_contract_single_item_unit_value_with_status,
    patch_tender_contract_value,
    patch_tender_contract_value_vat_not_included,
    patch_tender_multi_contracts,
    patch_tender_multi_contracts_cancelled,
    patch_tender_multi_contracts_cancelled_validate_amount,
    patch_tender_multi_contracts_cancelled_with_one_activated,
)
from openprocurement.tender.openua.tests.contract_blanks import patch_tender_contract
from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest,
    test_tender_simpledefense_bids,
    test_tender_simpledefense_multi_buyers_data,
)


class TenderContractResourceTest(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_simpledefense_bids

    def create_award(self, value_vat_included=True):
        authorization = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "value": {
                        "amount": self.initial_data["value"]["amount"],
                        "currency": self.initial_data["value"]["currency"],
                        "valueAddedTaxIncluded": value_vat_included,
                    },
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]
        self.app.authorization = authorization
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True}},
        )
        response = self.app.get(f"/tenders/{self.tender_id}/contracts")
        self.contracts_ids = [i["id"] for i in response.json["data"]]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]

    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)
    test_patch_contract_single_item_unit_value_with_status = snitch(patch_contract_single_item_unit_value_with_status)
    test_patch_contract_multi_items_unit_value = snitch(patch_contract_multi_items_unit_value)


class TenderContractVATNotIncludedResourceTest(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_simpledefense_bids

    def setUp(self):
        super().setUp()
        TenderContractResourceTest.create_award(self, value_vat_included=False)

    test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)


class TenderContractMultiBuyersResourceTest(BaseSimpleDefContentWebTest):
    initial_data = test_tender_simpledefense_multi_buyers_data
    initial_status = "active.qualification"
    initial_bids = test_tender_simpledefense_bids

    def setUp(self):
        super().setUp()
        TenderContractResourceTest.create_award(self, value_vat_included=True)

    test_patch_tender_multi_contracts = snitch(patch_tender_multi_contracts)
    test_patch_tender_multi_contracts_cancelled = snitch(patch_tender_multi_contracts_cancelled)
    test_patch_tender_multi_contracts_cancelled_with_one_activated = snitch(
        patch_tender_multi_contracts_cancelled_with_one_activated
    )
    test_patch_tender_multi_contracts_cancelled_validate_amount = snitch(
        patch_tender_multi_contracts_cancelled_validate_amount
    )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractVATNotIncludedResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
