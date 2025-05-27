import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderEContractMultiBuyersResourceTestMixin,
    TenderEcontractResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.contract_blanks import (
    patch_contract_single_item_unit_value,
    patch_contract_single_item_unit_value_with_status,
    patch_tender_contract_value,
    patch_tender_contract_value_vat_not_included,
    patch_tender_multi_contracts,
    patch_tender_multi_contracts_cancelled,
    patch_tender_multi_contracts_cancelled_validate_amount,
    patch_tender_multi_contracts_cancelled_with_one_activated,
)
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_lots,
    test_tender_data_multi_buyers,
    test_tender_negotiation_config,
    test_tender_negotiation_data,
    test_tender_negotiation_data_2items,
    test_tender_negotiation_data_multi_buyers,
    test_tender_negotiation_quick_config,
    test_tender_negotiation_quick_data,
    test_tender_negotiation_quick_data_multi_buyers,
    test_tender_reporting_data,
)
from openprocurement.tender.limited.tests.contract_blanks import (  # EContract
    activate_contract_cancelled_lot,
    patch_tender_contract,
    patch_tender_negotiation_econtract,
    sign_second_contract,
    tender_contract_signature_date,
    tender_negotiation_contract_signature_date,
)


class CreateActiveAwardMixin:
    def create_award(self):
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {
                "data": {
                    "status": "active",
                    "qualified": True,
                }
            },
        )
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"].get("contracts", "")]
        self.bid_token = self.tender_token


class TenderContractResourceTest(BaseTenderContentWebTest, CreateActiveAwardMixin):
    initial_status = "active"
    initial_data = test_tender_reporting_data
    initial_bids = None  # test_bids

    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_tender_contract_signature_date = snitch(tender_contract_signature_date)
    test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)
    test_patch_contract_single_item_unit_value_with_status = snitch(patch_contract_single_item_unit_value_with_status)


class TenderContractVATNotIncludedResourceTest(BaseTenderContentWebTest):
    initial_status = "active"
    initial_data = test_tender_reporting_data
    initial_bids = None

    def create_award(self):
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )

        self.award_id = response.json["data"]["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"].get("contracts", "")]
        self.bid_token = self.tender_token

    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)


class TenderNegotiationContractResourceTest(TenderContractResourceTest):
    initial_data = test_tender_negotiation_data
    stand_still_period_days = 10
    initial_config = test_tender_negotiation_config

    test_patch_tender_contract = snitch(patch_tender_negotiation_econtract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_tender_contract_signature_date = snitch(tender_negotiation_contract_signature_date)


class TenderNegotiationContractVATNotIncludedResourceTest(TenderContractVATNotIncludedResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config


class TenderNegotiationLotMixin:
    def create_award(self):
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.lot1 = response.json["data"]["lots"][0]

        # Create award
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": self.lot1["id"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"].get("contracts", "")]
        self.bid_token = self.tender_token


class TenderNegotiationLotContractResourceTest(TenderNegotiationLotMixin, TenderNegotiationContractResourceTest):
    initial_status = "active"
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    stand_still_period_days = 10
    initial_lots = test_lots

    test_activate_contract_cancelled_lot = snitch(activate_contract_cancelled_lot)


class TenderNegotiationLot2ContractResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data_2items
    initial_config = test_tender_negotiation_config
    initial_lots = test_lots * 2
    stand_still_period_days = 10

    def setUp(self):
        super().setUp()
        self.create_award()

    def create_award(self):
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.lot1 = response.json["data"]["lots"][0]
        self.lot2 = response.json["data"]["lots"][1]

        # Create award
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": self.lot1["id"],
                }
            },
        )

        award = response.json["data"]
        self.award1_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award1_id}/documents")
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award1_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )

        # Create another award
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": self.lot2["id"],
                }
            },
        )

        award = response.json["data"]
        self.award2_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award2_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award2_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"].get("contracts", "")]
        self.bid_token = self.tender_token

    test_sign_second_contract = snitch(sign_second_contract)


class TenderNegotiationQuickContractResourceTest(TenderNegotiationContractResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
    stand_still_period_days = 5


class TenderNegotiationQuickLotContractResourceTest(
    TenderNegotiationLotContractResourceTest, TenderNegotiationLotMixin
):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
    stand_still_period_days = 5


class TenderContractMultiBuyersResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_data_multi_buyers
    stand_still_period_days = 10

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


class TenderNegotiationMultiBuyersContractResourceTest(TenderContractMultiBuyersResourceTest):
    initial_data = test_tender_negotiation_data_multi_buyers
    initial_config = test_tender_negotiation_config
    stand_still_period_days = 10


class TenderNegotiationQuickMultiBuyersContractResourceTest(TenderNegotiationMultiBuyersContractResourceTest):
    initial_data = test_tender_negotiation_quick_data_multi_buyers
    initial_config = test_tender_negotiation_quick_config
    stand_still_period_days = 10


class TenderReportingEContractResourceTest(
    BaseTenderContentWebTest, CreateActiveAwardMixin, TenderEcontractResourceTestMixin
):
    initial_status = "active"
    initial_data = test_tender_reporting_data
    initial_bids = None

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderNegotiationEContractResourceTest(TenderReportingEContractResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    stand_still_period_days = 10

    test_patch_tender_econtract = snitch(patch_tender_negotiation_econtract)


class TenderNegotiationQuickEContractResourceTest(TenderNegotiationEContractResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
    stand_still_period_days = 5


class TenderReportingEContractMultiBuyersResourceTest(
    BaseTenderContentWebTest,
    CreateActiveAwardMixin,
    TenderEContractMultiBuyersResourceTestMixin,
):
    initial_data = test_tender_data_multi_buyers
    stand_still_period_days = 10

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderNegotiationEContractMultiBuyersResourceTest(TenderReportingEContractMultiBuyersResourceTest):
    initial_data = test_tender_negotiation_data_multi_buyers
    initial_config = test_tender_negotiation_config


class TenderNegotiationQuickEContractMultiBuyersResourceTest(TenderReportingEContractMultiBuyersResourceTest):
    initial_data = test_tender_negotiation_quick_data_multi_buyers
    initial_config = test_tender_negotiation_quick_config


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
