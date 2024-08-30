import unittest
from copy import deepcopy

# from openprocurement.tender.belowthreshold.tests.contract_blanks import (
#     create_tender_contract,
#     patch_contract_multi_items_unit_value,
#     patch_contract_single_item_unit_value,
#     patch_contract_single_item_unit_value_with_status,
#     patch_tender_contract_value,
#     patch_tender_multi_contracts,
#     patch_tender_multi_contracts_cancelled,
#     patch_tender_multi_contracts_cancelled_validate_amount,
#     patch_tender_multi_contracts_cancelled_with_one_activated,
# )
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_tender_pq_bids,
    test_tender_pq_data,
    test_tender_pq_multi_buyers_data,
)

# from openprocurement.api.tests.base import snitch


# from datetime import timedelta
# from unittest.mock import patch


# from openprocurement.tender.pricequotation.tests.contract_blanks import (
#     patch_tender_contract,
#     patch_tender_contract_value_vat_not_included,
# )

multi_item_tender_data = deepcopy(test_tender_pq_data)
multi_item_tender_data["items"] *= 3


# @patch(
#     "openprocurement.tender.pricequotation.procedure.models.requirement.PQ_CRITERIA_ID_FROM",
#     get_now() + timedelta(days=1),
# )
class TenderContractResourceTest(TenderContentWebTest):
    initial_status = "active.awarded"
    initial_data = multi_item_tender_data
    initial_bids = test_tender_pq_bids

    def get_award(self):
        self.award_id = self.award_ids[-1]
        resp = self.app.get(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
        )
        award = resp.json["data"]
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]
        self.award_date = award["date"]

    def setUp(self):
        super().setUp()
        self.get_award()

    # test_create_tender_contract = snitch(create_tender_contract)
    # test_patch_tender_contract = snitch(patch_tender_contract)
    # test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    # test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)
    # test_patch_contract_single_item_unit_value_with_status = snitch(patch_contract_single_item_unit_value_with_status)
    # test_patch_contract_multi_items_unit_value = snitch(patch_contract_multi_items_unit_value)


# @patch(
#     "openprocurement.tender.pricequotation.procedure.models.requirement.PQ_CRITERIA_ID_FROM",
#     get_now() + timedelta(days=1),
# )
class TenderContractVATNotIncludedResourceTest(TenderContentWebTest):
    initial_status = "active.awarded"
    initial_bids = test_tender_pq_bids

    def setUp(self):
        super().setUp()
        TenderContractResourceTest.get_award(self)

    # test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)


# @patch(
#     "openprocurement.tender.pricequotation.procedure.models.requirement.PQ_CRITERIA_ID_FROM",
#     get_now() + timedelta(days=1),
# )
class TenderContractMultiBuyersResourceTest(TenderContentWebTest):
    initial_data = test_tender_pq_multi_buyers_data
    initial_status = "active.qualification"
    initial_bids = test_tender_pq_bids

    def setUp(self):
        super().setUp()
        TenderContractResourceTest.get_award(self)
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"]["contracts"]]

    # test_patch_tender_multi_contracts = snitch(patch_tender_multi_contracts)
    # test_patch_tender_multi_contracts_cancelled = snitch(patch_tender_multi_contracts_cancelled)
    # test_patch_tender_multi_contracts_cancelled_with_one_activated = snitch(
    #     patch_tender_multi_contracts_cancelled_with_one_activated
    # )
    # test_patch_tender_multi_contracts_cancelled_validate_amount = snitch(
    #     patch_tender_multi_contracts_cancelled_validate_amount
    # )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractMultiBuyersResourceTest))

    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
