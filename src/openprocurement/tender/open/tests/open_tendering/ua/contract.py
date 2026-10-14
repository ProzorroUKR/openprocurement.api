import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.open.tests.open_tendering.ua.contract_blanks import (
    patch_contract_value_multi_currency,
)
from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_supplier
from openprocurement.tender.open.tests.below_threshold.contract_blanks import (
    patch_tender_multi_contracts_cancelled,
    patch_tender_multi_contracts_cancelled_with_one_activated,
)
from openprocurement.tender.open.tests.open_tendering.ua.base import (
    BaseTenderOpenTenderingUAContentWebTest,
    test_tender_open_tendering_ua_bids,
    test_tender_open_tendering_ua_multi_buyers_data,
)
from openprocurement.tender.open.tests.above_threshold_ua.contract_blanks import (
    patch_tender_contract,
    patch_tender_contract_datesigned,
)


class TenderContractResourceTest(BaseTenderOpenTenderingUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_tendering_ua_bids

    def create_award(self):
        authorization = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards",
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "value": self.initial_bids[0].get("value") or self.initial_bids[0].get("lotValues")[0].get("value"),
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
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"].get("contracts", "")]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]

    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned)
    test_patch_tender_contract = snitch(patch_tender_contract)
    # valueCurrencyEquality=False: the contract value/currency aren't limited by the award
    test_patch_contract_value_multi_currency = snitch(patch_contract_value_multi_currency)


class TenderContractVATNotIncludedResourceTest(BaseTenderOpenTenderingUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_tendering_ua_bids

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
                    "value": {
                        "amount": self.initial_bids[0]["value"]["amount"],
                        "currency": self.initial_bids[0]["value"]["currency"],
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
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"].get("contracts", "")]

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderContractMultiBuyersResourceTest(BaseTenderOpenTenderingUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_tendering_ua_bids
    initial_data = test_tender_open_tendering_ua_multi_buyers_data

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
