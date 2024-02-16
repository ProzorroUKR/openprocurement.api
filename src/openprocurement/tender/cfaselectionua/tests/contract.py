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
    create_tender_contract_document_by_others,
    create_tender_contract_document_by_supplier,
    lot2_create_tender_contract_document_by_others,
    lot2_create_tender_contract_document_by_supplier,
    lot2_patch_tender_contract_document_by_supplier,
    lot2_put_tender_contract_document_by_supplier,
    patch_tender_contract_document_by_supplier,
    patch_tender_contract_status_by_others,
    patch_tender_contract_status_by_owner,
    patch_tender_contract_status_by_supplier,
    patch_tender_contract_value,
    patch_tender_contract_value_vat_not_included,
    patch_tender_multi_contracts,
    patch_tender_multi_contracts_cancelled,
    patch_tender_multi_contracts_cancelled_validate_amount,
    patch_tender_multi_contracts_cancelled_with_one_activated,
    put_tender_contract_document_by_others,
    put_tender_contract_document_by_supplier,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_tender_cfaselectionua_bids,
    test_tender_cfaselectionua_lots,
    test_tender_cfaselectionua_multi_buyers_data,
    test_tender_cfaselectionua_organization,
)
from openprocurement.tender.cfaselectionua.tests.contract_blanks import (  # TenderContractResourceTest; Tender2LotContractResourceTest; TenderContractDocumentResourceTest; Tender2LotContractDocumentResourceTest
    create_tender_contract,
    create_tender_contract_document,
    create_tender_contract_in_complete_status,
    create_tender_contract_invalid,
    get_tender_contract,
    get_tender_contracts,
    lot2_create_tender_contract_document,
    lot2_patch_tender_contract,
    lot2_patch_tender_contract_document,
    lot2_put_tender_contract_document,
    not_found,
    patch_contract_multi_items_unit_value,
    patch_contract_single_item_unit_value,
    patch_tender_contract,
    patch_tender_contract_document,
    put_tender_contract_document,
)


class TenderContractResourceTestMixin:
    test_create_tender_contract_invalid = snitch(create_tender_contract_invalid)
    test_get_tender_contract = snitch(get_tender_contract)
    test_get_tender_contracts = snitch(get_tender_contracts)


class TenderContractDocumentResourceTestMixin:
    test_not_found = snitch(not_found)
    test_create_tender_contract_document = snitch(create_tender_contract_document)
    test_put_tender_contract_document = snitch(put_tender_contract_document)
    test_patch_tender_contract_document = snitch(patch_tender_contract_document)


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
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active"}},
        )

        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"]["contracts"]]
        self.bid_token = self.initial_bids_tokens[award["bid_id"]]


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractResourceTest(TenderContentWebTest, TenderContractResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots

    test_create_tender_contract = snitch(create_tender_contract)
    test_create_tender_contract_in_complete_status = snitch(create_tender_contract_in_complete_status)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)
    test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)
    test_patch_contract_multi_items_unit_value = snitch(patch_contract_multi_items_unit_value)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractVATNotIncludedResourceTest(TenderContentWebTest, TenderContractResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots

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
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)


@unittest.skip("Skip multi-lots tests")
@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class Tender2LotContractResourceTest(TenderContentWebTest, CreateActiveAwardMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = 2 * test_tender_cfaselectionua_lots

    def setUp(self):
        super().setUp()
        # Create award
        self.create_award()

    test_lot2_patch_tender_contract = snitch(lot2_patch_tender_contract)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractDocumentResourceTest(TenderContentWebTest, TenderContractDocumentResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots
    docservice = True

    test_create_tender_contract_document_by_supplier = snitch(create_tender_contract_document_by_supplier)
    test_create_tender_contract_document_by_others = snitch(create_tender_contract_document_by_others)
    test_put_tender_contract_document_by_supplier = snitch(put_tender_contract_document_by_supplier)
    test_put_tender_contract_document_by_others = snitch(put_tender_contract_document_by_others)
    test_patch_tender_contract_document_by_supplier = snitch(patch_tender_contract_document_by_supplier)


@unittest.skip("Skip multi-lots tests")
@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class Tender2LotContractDocumentResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = 2 * test_tender_cfaselectionua_lots

    def setUp(self):
        super().setUp()
        # Create award
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
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]

        self.app.authorization = auth
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )
        # Create contract for award

        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/contracts".format(self.tender_id),
            {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
        )
        contract = response.json["data"]
        self.contract_id = contract["id"]
        self.app.authorization = auth

    lot2_create_tender_contract_document = snitch(lot2_create_tender_contract_document)
    lot2_put_tender_contract_document = snitch(lot2_put_tender_contract_document)
    lot2_patch_tender_contract_document = snitch(lot2_patch_tender_contract_document)
    test_lot2_create_tender_contract_document_by_supplier = snitch(lot2_create_tender_contract_document_by_supplier)
    test_lot2_create_tender_contract_document_by_others = snitch(lot2_create_tender_contract_document_by_others)
    test_lot2_put_tender_contract_document_by_supplier = snitch(lot2_put_tender_contract_document_by_supplier)
    test_lot2_patch_tender_contract_document_by_supplier = snitch(lot2_patch_tender_contract_document_by_supplier)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
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
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )
        # check contracts are buyer related
        response = self.app.get(f"/tenders/{self.tender_id}")
        for c in response.json["data"]["contracts"]:
            self.assertIn("buyerID", c)

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
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


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
class TenderEContractResourceTest(TenderContentWebTest, CreateActiveAwardMixin, TenderEcontractResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
    def setUp(self):
        super().setUp()
        self.create_award()


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
class TenderEContractMultiBuyersResourceTest(
    TenderContentWebTest,
    CreateActiveAwardMixin,
    TenderEContractMultiBuyersResourceTestMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots
    initial_data = test_tender_cfaselectionua_multi_buyers_data

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
    def setUp(self):
        super().setUp()
        self.create_award()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractVATNotIncludedResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEContractMultiBuyersResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
