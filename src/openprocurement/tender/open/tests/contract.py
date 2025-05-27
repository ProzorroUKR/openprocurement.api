import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_lots,
    test_tender_below_supplier,
)
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderEContractMultiBuyersResourceTestMixin,
    TenderEcontractResourceTestMixin,
)
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
from openprocurement.tender.open.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_open_bids,
    test_tender_open_multi_buyers_data,
)
from openprocurement.tender.open.tests.contract_blanks import (
    patch_tender_contract,
    patch_tender_contract_datesigned,
)


class CreateActiveAwardMixin:
    def create_award(self):
        authorization = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "lotID": self.initial_lots[0]["id"],
                    "value": self.initial_bids[0]["lotValues"][0]["value"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]
        self.app.authorization = authorization
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )

        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"]["contracts"]]
        self.bid_token = self.initial_bids_tokens[award["bid_id"]]

        return response.json["data"]


class TenderContractResourceTest(BaseTenderUAContentWebTest, CreateActiveAwardMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_bids
    initial_lots = test_tender_below_lots

    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)
    test_patch_contract_single_item_unit_value_with_status = snitch(patch_contract_single_item_unit_value_with_status)
    test_patch_contract_multi_items_unit_value = snitch(patch_contract_multi_items_unit_value)


class TenderContractVATNotIncludedResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_bids
    initial_lots = test_tender_below_lots

    def create_award(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards",
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "lotID": self.initial_lots[0]["id"],
                    "value": {
                        "amount": self.initial_bids[0]["lotValues"][0]["value"]["amount"],
                        "currency": self.initial_bids[0]["lotValues"][0]["value"]["currency"],
                        "valueAddedTaxIncluded": False,
                    },
                }
            },
        )
        self.app.authorization = auth
        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )

        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"]["contracts"]]
        self.bid_token = self.initial_bids_tokens[award["bid_id"]]

    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)


class TenderContractMultiBuyersResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_bids
    initial_lots = test_tender_below_lots
    initial_data = test_tender_open_multi_buyers_data

    def setUp(self):
        super().setUp()
        TenderContractResourceTest.create_award(self)

    test_patch_tender_multi_contracts = snitch(patch_tender_multi_contracts)
    test_patch_tender_multi_contracts_cancelled = snitch(patch_tender_multi_contracts_cancelled)
    test_patch_tender_multi_contracts_cancelled_with_one_activated = snitch(
        patch_tender_multi_contracts_cancelled_with_one_activated
    )
    test_patch_tender_multi_contracts_cancelled_validate_amount = snitch(
        patch_tender_multi_contracts_cancelled_validate_amount
    )


class TenderEContractResourceTest(
    BaseTenderUAContentWebTest,
    CreateActiveAwardMixin,
    TenderEcontractResourceTestMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_bids
    initial_lots = test_tender_below_lots

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderEContractMultiBuyersResourceTest(
    BaseTenderUAContentWebTest,
    CreateActiveAwardMixin,
    TenderEContractMultiBuyersResourceTestMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_bids
    initial_lots = test_tender_below_lots
    initial_data = test_tender_open_multi_buyers_data

    def setUp(self):
        super().setUp()
        self.create_award()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractMultiBuyersResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEContractMultiBuyersResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
