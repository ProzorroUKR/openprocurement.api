import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderEContractMultiBuyersResourceTestMixin,
    TenderEcontractResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.contract_blanks import (
    create_tender_contract,
    patch_tender_contract_value,
    patch_tender_contract_value_vat_not_included,
    patch_tender_multi_contracts,
    patch_tender_multi_contracts_cancelled,
    patch_tender_multi_contracts_cancelled_validate_amount,
    patch_tender_multi_contracts_cancelled_with_one_activated,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_tender_cfaselectionua_bids,
    test_tender_cfaselectionua_lots,
    test_tender_cfaselectionua_multi_buyers_data,
    test_tender_cfaselectionua_organization,
)
from openprocurement.tender.cfaselectionua.tests.contract_blanks import (  # TenderContractResourceTest; Tender2LotContractResourceTest; TenderContractDocumentResourceTest; Tender2LotContractDocumentResourceTest
    lot2_patch_tender_contract,
    patch_contract_single_item_unit_value,
    patch_tender_contract,
)


class CreateActiveAwardMixin:
    def create_award(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards",
            {
                "data": {
                    "suppliers": [test_tender_cfaselectionua_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "lotID": self.initial_lots[0]["id"],
                    "value": {"amount": 500, "currency": "UAH", "valueAddedTaxIncluded": True},
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = auth
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active"}},
        )

        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"]["contracts"]]
        self.bid_token = self.initial_bids_tokens[award["bid_id"]]


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderContractResourceTest(TenderContentWebTest, TenderEcontractResourceTestMixin):
    def setUp(self):
        super().setUp()
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"]["contracts"]]

    initial_status = "active.awarded"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots

    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)


class TenderContractVATNotIncludedResourceTest(TenderContentWebTest, CreateActiveAwardMixin):
    initial_status = "active.awarded"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots

    def setUp(self):
        super().setUp()
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"]["contracts"]]

    def update_vat_fields(self, items):
        for item in items:
            if "lotValues" in item:
                for lot_value in item["lotValues"]:
                    lot_value["value"]["valueAddedTaxIncluded"] = False
            else:
                item["value"]["valueAddedTaxIncluded"] = False

    def generate_bids(self, status, start_end="start"):
        self.initial_bids = deepcopy(self.initial_bids)
        self.update_vat_fields(self.initial_bids)
        super().generate_bids(status, start_end)

    def calculate_agreement_contracts_value_amount(self, agreement, items):
        super().calculate_agreement_contracts_value_amount(agreement, items)
        self.update_vat_fields(agreement["contracts"])

    test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)


@unittest.skip("Skip multi-lots tests")
class Tender2LotContractResourceTest(TenderContentWebTest, CreateActiveAwardMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = 2 * test_tender_cfaselectionua_lots

    def setUp(self):
        super().setUp()
        # Create award
        self.create_award()

    test_lot2_patch_tender_contract = snitch(lot2_patch_tender_contract)


class TenderContractMultiBuyersResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots
    initial_data = test_tender_cfaselectionua_multi_buyers_data

    def create_award(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_cfaselectionua_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "lotID": self.initial_lots[0]["id"],
                    "value": {"amount": 500, "currency": "UAH", "valueAddedTaxIncluded": True},
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]
        self.app.authorization = auth
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )
        # check contracts are buyer related
        response = self.app.get(f"/tenders/{self.tender_id}/contracts")
        self.contracts_ids = [c["id"] for c in response.json["data"]]

    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_multi_contracts = snitch(patch_tender_multi_contracts)
    test_patch_tender_multi_contracts_cancelled = snitch(patch_tender_multi_contracts_cancelled)
    test_patch_tender_multi_contracts_cancelled_with_one_activated = snitch(
        patch_tender_multi_contracts_cancelled_with_one_activated
    )
    test_patch_tender_multi_contracts_cancelled_validate_amount = snitch(
        patch_tender_multi_contracts_cancelled_validate_amount
    )


class TenderEContractResourceTest(TenderContentWebTest, CreateActiveAwardMixin, TenderEcontractResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderEContractMultiBuyersResourceTest(
    TenderContentWebTest,
    CreateActiveAwardMixin,
    TenderEContractMultiBuyersResourceTestMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots
    initial_data = test_tender_cfaselectionua_multi_buyers_data

    def setUp(self):
        super().setUp()
        self.create_award()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractVATNotIncludedResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEContractMultiBuyersResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
