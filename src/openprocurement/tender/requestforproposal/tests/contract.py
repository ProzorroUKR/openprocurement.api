import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.contract_blanks import (  # TenderContractResourceTest; Tender2LotContractResourceTest; TenderContractDocumentResourceTest; Tender2LotContractDocumentResourceTest; Econtract
    cancelling_award_contract_sync,
    create_tender_contract,
    patch_contract_multi_items_unit_value,
    patch_contract_single_item_unit_value,
    patch_contract_single_item_unit_value_round,
    patch_contract_single_item_unit_value_with_status,
    patch_multiple_contracts_in_contracting,
    patch_tender_contract,
    patch_tender_contract_rationale_simple,
    patch_tender_contract_value,
    patch_tender_contract_value_vat_not_included,
    patch_tender_multi_contracts,
    patch_tender_multi_contracts_cancelled,
    patch_tender_multi_contracts_cancelled_validate_amount,
    patch_tender_multi_contracts_cancelled_with_one_activated,
)
from openprocurement.tender.requestforproposal.tests.base import (
    TenderContentWebTest,
    test_tender_rfp_bids,
    test_tender_rfp_config,
    test_tender_rfp_data_no_auction,
    test_tender_rfp_lots,
    test_tender_rfp_multi_buyers_data,
    test_tender_rfp_supplier,
)
from openprocurement.tender.requestforproposal.tests.contract_blanks import (
    patch_econtract_multi_currency,
)


class TenderEcontractResourceTestMixin:
    # test_create_econtract = snitch(create_econtract)
    test_cancelling_award_contract_sync = snitch(cancelling_award_contract_sync)

    def activate_contract(self, contract_id, status=200):
        # prepare contract for activating
        doc = self.mongodb.tenders.get(self.tender_id)
        for i in doc.get("awards", []):
            if 'complaintPeriod' in i:
                i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
        self.mongodb.tenders.save(doc)

        response = self.app.put_json(
            f"/contracts/{contract_id}/buyer/signer_info?acc_token={self.tender_token}",
            {
                "data": {
                    "name": "Test Testovich",
                    "telephone": "+380950000000",
                    "email": "example@email.com",
                    "iban": "1" * 15,
                    "authorizedBy": "документ який дозволяє",
                    "position": "статус",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        response = self.app.put_json(
            f"/contracts/{contract_id}/suppliers/signer_info?acc_token={self.bid_token}",
            {
                "data": {
                    "name": "Test Testovich",
                    "telephone": "+380950000000",
                    "email": "example@email.com",
                    "iban": "1" * 15,
                    "authorizedBy": "документ який дозволяє",
                    "position": "статус",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        response = self.app.patch_json(
            f"/contracts/{contract_id}?acc_token={self.tender_token}",
            {
                "data": {
                    "status": "active",
                    "contractNumber": "123",
                    "period": {
                        "startDate": "2023-03-18T18:47:47.155143+02:00",
                        "endDate": "2023-05-18T18:47:47.155143+02:00",
                    },
                }
            },
            status=status,
        )
        return response


class TenderEContractMultiBuyersResourceTestMixin:
    test_patch_multiple_contracts_in_contracting = snitch(patch_multiple_contracts_in_contracting)


class CreateActiveAwardMixin:
    def create_award(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards",
            {
                "data": {
                    "suppliers": [test_tender_rfp_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "value": self.initial_data["value"],
                }
            },
        )
        self.app.authorization = auth
        award = response.json["data"]
        self.award_id = award["id"]
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]

        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )

        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"].get("contracts", "")]
        self.bid_token = self.initial_bids_tokens[award["bid_id"]]


class TenderContractResourceTest(TenderContentWebTest, CreateActiveAwardMixin, TenderEcontractResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_rfp_bids

    def setUp(self):
        super().setUp()
        self.create_award()

    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_rationale_simple = snitch(patch_tender_contract_rationale_simple)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)
    test_patch_contract_single_item_unit_value_with_status = snitch(patch_contract_single_item_unit_value_with_status)
    test_patch_contract_single_item_unit_value_round = snitch(patch_contract_single_item_unit_value_round)
    test_patch_contract_multi_items_unit_value = snitch(patch_contract_multi_items_unit_value)


class TenderContractVATNotIncludedResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_rfp_bids

    def create_award(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards",
            {
                "data": {
                    "suppliers": [test_tender_rfp_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "items": self.initial_data["items"],
                    "value": {
                        "amount": self.initial_data["value"]["amount"],
                        "currency": self.initial_data["value"]["currency"],
                        "valueAddedTaxIncluded": False,
                    },
                }
            },
        )
        self.app.authorization = auth
        self.award_id = response.json["data"]["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"].get("contracts", "")]

    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)


class TenderContractMultiBuyersResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_rfp_bids
    initial_data = test_tender_rfp_multi_buyers_data

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


class TenderLotContractMultiBuyersResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_data = test_tender_rfp_multi_buyers_data
    initial_bids = test_tender_rfp_bids
    initial_lots = test_tender_rfp_lots

    def setUp(self):
        super().setUp()
        # Create award

        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards",
            {
                "data": {
                    "suppliers": [test_tender_rfp_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "lotID": self.initial_lots[0]["id"],
                    "value": self.initial_data["value"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = auth
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )
        self.bid_token = self.initial_bids_tokens[award["bid_id"]]

    test_patch_lot_tender_multi_contracts = snitch(patch_tender_multi_contracts)


class TenderEContractResourceTest(
    TenderContentWebTest,
    CreateActiveAwardMixin,
    TenderEcontractResourceTestMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_rfp_bids
    config = deepcopy(test_tender_rfp_config)
    config.update(
        {
            "hasAuction": False,
            "hasAwardingOrder": False,
            "hasValueRestriction": False,
            "valueCurrencyEquality": False,
        }
    )
    initial_config = config
    initial_data = test_tender_rfp_data_no_auction
    tender_for_funders = True

    test_patch_econtract_multi_currency = snitch(patch_econtract_multi_currency)

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderEContractMultiBuyersResourceTest(
    TenderContentWebTest,
    CreateActiveAwardMixin,
    TenderEContractMultiBuyersResourceTestMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_rfp_bids
    initial_data = test_tender_rfp_multi_buyers_data

    def setUp(self):
        super().setUp()
        self.create_award()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractVATNotIncludedResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractMultiBuyersResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotContractMultiBuyersResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEContractResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
