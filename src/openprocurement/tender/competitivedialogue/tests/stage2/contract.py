import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderContractDocumentResourceTestMixin,
    TenderContractResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.contract_blanks import (  # TenderStage2EU(UA)ContractResourceTest
    create_tender_contract,
    create_tender_contract_document_by_others,
    create_tender_contract_document_by_supplier,
    patch_contract_multi_items_unit_value,
    patch_contract_single_item_unit_value,
    patch_contract_single_item_unit_value_with_status,
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
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cd_author,
    test_tender_cd_tenderer,
    test_tender_cdeu_stage2_data,
    test_tender_cdeu_stage2_multi_buyers_data,
    test_tender_cdua_stage2_multi_buyers_data,
    test_tender_openeu_bids,
)
from openprocurement.tender.openeu.tests.contract_blanks import contract_termination
from openprocurement.tender.openeu.tests.contract_blanks import (
    patch_tender_contract as patch_tender_contract_eu,  # TenderStage2EUContractResourceTest
)
from openprocurement.tender.openua.tests.contract_blanks import (  # TenderStage2EU(UA)ContractResourceTest; TenderStage2UAContractResourceTest,
    patch_tender_contract,
    patch_tender_contract_datesigned,
)

test_tender_bids = deepcopy(test_tender_openeu_bids[:2])
for test_bid in test_tender_bids:
    test_bid["tenderers"] = [test_tender_cd_tenderer]


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderStage2EUContractResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderContractResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_below_lots
    author_data = test_tender_cd_author

    def create_award(self):
        self.supplier_info = deepcopy(test_tender_cd_tenderer)
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [self.supplier_info],
                    "status": "pending",
                    "bid_id": self.bids[0]["id"],
                    "value": self.initial_data["value"],
                    "items": self.initial_data["items"],
                    "lotID": self.initial_lots[0]["id"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authotization = ("Basic", ("broker", ""))
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]
        self.award_items = award["items"]
        self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
        self.app.patch_json(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super().setUp()
        self.create_award()

    test_contract_termination = snitch(contract_termination)
    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned)
    test_patch_tender_contract = snitch(patch_tender_contract_eu)
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderStage2EUContractDocumentResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderContractDocumentResourceTestMixin
):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_below_lots
    docservice = True

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super().setUp()
        # Create award
        supplier_info = deepcopy(test_tender_cd_tenderer)
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [supplier_info],
                    "status": "pending",
                    "bid_id": self.bids[0]["id"],
                    "lotID": self.initial_lots[0]["id"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create contract for award
        response = self.app.post_json(
            "/tenders/{}/contracts".format(self.tender_id),
            {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
        )
        contract = response.json["data"]
        self.contract_id = contract["id"]
        self.app.authorization = ("Basic", ("broker", ""))

    test_create_tender_contract_document_by_supplier = snitch(create_tender_contract_document_by_supplier)
    test_create_tender_contract_document_by_others = snitch(create_tender_contract_document_by_others)
    test_put_tender_contract_document_by_supplier = snitch(put_tender_contract_document_by_supplier)
    test_put_tender_contract_document_by_others = snitch(put_tender_contract_document_by_others)
    test_patch_tender_contract_document_by_supplier = snitch(patch_tender_contract_document_by_supplier)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderStage2UAContractResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = test_tender_below_lots

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def create_award(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_cd_tenderer],
                    "status": "pending",
                    "bid_id": self.bids[0]["id"],
                    "value": self.initial_data["value"],
                    "items": self.initial_data["items"],
                    "lotID": self.initial_lots[0]["id"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = auth
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]
        self.award_items = award["items"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )

    def setUp(self):
        super().setUp()
        self.create_award()

    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)
    test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)
    test_patch_contract_single_item_unit_value_with_status = snitch(patch_contract_single_item_unit_value_with_status)
    test_patch_contract_multi_items_unit_value = snitch(patch_contract_multi_items_unit_value)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractVATNotIncludedResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = test_tender_below_lots

    def create_award(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_cd_tenderer],
                    "status": "pending",
                    "bid_id": self.bids[0]["id"],
                    "value": {
                        "amount": self.initial_data["value"]["amount"],
                        "currency": self.initial_data["value"]["currency"],
                        "valueAddedTaxIncluded": False,
                    },
                    "lotID": self.initial_lots[0]["id"],
                }
            },
        )
        self.app.authorization = auth
        self.award_id = response.json["data"]["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super().setUp()
        self.create_award()

    test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderStage2UAContractDocumentResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest, TenderContractDocumentResourceTestMixin
):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = test_tender_below_lots
    docservice = True

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super().setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_cd_tenderer],
                    "status": "pending",
                    "bid_id": self.bids[0]["id"],
                    "lotID": self.initial_lots[0]["id"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create contract for award
        response = self.app.post_json(
            "/tenders/{}/contracts".format(self.tender_id),
            {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
        )
        contract = response.json["data"]
        self.contract_id = contract["id"]
        self.app.authorization = auth

    test_create_tender_contract_document_by_supplier = snitch(create_tender_contract_document_by_supplier)
    test_create_tender_contract_document_by_others = snitch(create_tender_contract_document_by_others)
    test_put_tender_contract_document_by_supplier = snitch(put_tender_contract_document_by_supplier)
    test_put_tender_contract_document_by_others = snitch(put_tender_contract_document_by_others)
    test_patch_tender_contract_document_by_supplier = snitch(patch_tender_contract_document_by_supplier)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderStage2EUContractUnitValueResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = test_tender_below_lots

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super().setUp()
        auth = self.app.authorization
        TenderStage2EUContractResourceTest.create_award(self)
        self.app.authorization = auth

    test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)
    test_patch_contract_multi_items_unit_value = snitch(patch_contract_multi_items_unit_value)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractEUStage2MultiBuyersResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_data = test_tender_cdeu_stage2_multi_buyers_data
    initial_lots = test_tender_below_lots

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super().setUp()
        TenderStage2EUContractResourceTest.create_award(self)

    test_patch_tender_multi_contracts = snitch(patch_tender_multi_contracts)
    test_patch_tender_multi_contracts_cancelled = snitch(patch_tender_multi_contracts_cancelled)
    test_patch_tender_multi_contracts_cancelled_with_one_activated = snitch(
        patch_tender_multi_contracts_cancelled_with_one_activated
    )
    test_patch_tender_multi_contracts_cancelled_validate_amount = snitch(
        patch_tender_multi_contracts_cancelled_validate_amount
    )


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractUAStage2MultiBuyersResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_data = test_tender_cdua_stage2_multi_buyers_data
    initial_lots = test_tender_below_lots

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super().setUp()
        TenderStage2UAContractResourceTest.create_award(self)

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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUContractDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UAContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UAContractDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractVATNotIncludedResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractEUStage2MultiBuyersResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractUAStage2MultiBuyersResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
