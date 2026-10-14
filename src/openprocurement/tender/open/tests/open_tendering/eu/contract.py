import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.open.tests.open_tendering.ua.contract_blanks import (
    patch_contract_value_multi_currency,
)
from openprocurement.tender.open.tests.below_threshold.base import (
    test_tender_below_author,
    test_tender_below_supplier,
)
from openprocurement.tender.open.tests.below_threshold.contract_blanks import (
    patch_tender_multi_contracts_cancelled,
    patch_tender_multi_contracts_cancelled_with_one_activated,
)
from openprocurement.tender.open.tests.open_tendering.eu.base import (
    BaseTenderContentWebTest,
    test_tender_open_tendering_eu_bids,
    test_tender_open_tendering_eu_multi_buyers_data,
)
from openprocurement.tender.open.tests.above_threshold_eu.contract_blanks import patch_tender_contract
from openprocurement.tender.open.tests.above_threshold_ua.contract_blanks import (
    patch_tender_contract_datesigned,
)


class TenderContractResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_tendering_eu_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_below_author

    def create_award(self):
        self.supplier_info = deepcopy(test_tender_below_supplier)
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [self.supplier_info],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "value": self.initial_bids[0].get("value") or self.initial_bids[0].get("lotValues")[0].get("value"),
                    "items": self.initial_data["items"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]
        self.app.authorization = ("Basic", ("broker", ""))
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"]["contracts"]]
        self.bid_token = self.initial_bids_tokens[award["bid_id"]]

    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned)
    test_patch_tender_contract = snitch(patch_tender_contract)
    # valueCurrencyEquality=False: the contract value/currency aren't limited by the award
    test_patch_contract_value_multi_currency = snitch(patch_contract_value_multi_currency)


class TenderContractMultiBuyersResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_tendering_eu_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_below_author
    initial_data = test_tender_open_tendering_eu_multi_buyers_data

    def setUp(self):
        super().setUp()
        TenderContractResourceTest.create_award(self)

    test_patch_tender_multi_contracts_cancelled = snitch(patch_tender_multi_contracts_cancelled)
    test_patch_tender_multi_contracts_cancelled_with_one_activated = snitch(
        patch_tender_multi_contracts_cancelled_with_one_activated
    )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractMultiBuyersResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
