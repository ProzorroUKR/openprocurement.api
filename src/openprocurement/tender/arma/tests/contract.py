import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.arma.tests.base import (
    BaseTenderContentWebTest,
    test_tender_arma_bids,
    test_tender_arma_lots,
)
from openprocurement.tender.arma.tests.contract_blanks import (
    patch_tender_contract,
    patch_tender_contract_datesigned,
    patch_tender_contract_value,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_supplier,
)


class TenderContractResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_arma_bids
    initial_lots = test_tender_arma_lots
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
                    "lotID": self.initial_lots[0]["id"],
                    "value": {"amountPercentage": 50},
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
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
