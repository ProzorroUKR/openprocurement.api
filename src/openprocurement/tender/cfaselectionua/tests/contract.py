# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_bids,
    test_lots,
    test_organization,
)
from openprocurement.tender.cfaselectionua.tests.contract_blanks import (
    # TenderContractResourceTest
    create_tender_contract_invalid,
    create_tender_contract,
    create_tender_contract_in_complete_status,
    patch_tender_contract,
    get_tender_contract,
    get_tender_contracts,
    # Tender2LotContractResourceTest
    lot2_patch_tender_contract,
    # TenderContractDocumentResourceTest
    not_found,
    create_tender_contract_document,
    put_tender_contract_document,
    patch_tender_contract_document,
    # Tender2LotContractDocumentResourceTest
    lot2_create_tender_contract_document,
    lot2_put_tender_contract_document,
    lot2_patch_tender_contract_document,
)
from openprocurement.tender.belowthreshold.tests.contract_blanks import (
    patch_tender_contract_value_vat_not_included,
    patch_tender_contract_value,
    patch_tender_contract_status_by_owner,
    patch_tender_contract_status_by_others,
    patch_tender_contract_status_by_supplier,
    create_tender_contract_document_by_supplier,
    create_tender_contract_document_by_others,
    put_tender_contract_document_by_supplier,
    put_tender_contract_document_by_others,
    patch_tender_contract_document_by_supplier,
    lot2_create_tender_contract_document_by_supplier,
    lot2_create_tender_contract_document_by_others,
    lot2_put_tender_contract_document_by_supplier,
    lot2_patch_tender_contract_document_by_supplier,
)


class TenderContractResourceTestMixin(object):
    test_create_tender_contract_invalid = snitch(create_tender_contract_invalid)
    test_get_tender_contract = snitch(get_tender_contract)
    test_get_tender_contracts = snitch(get_tender_contracts)


class TenderContractDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_tender_contract_document = snitch(create_tender_contract_document)
    test_put_tender_contract_document = snitch(put_tender_contract_document)
    test_patch_tender_contract_document = snitch(patch_tender_contract_document)


class TenderContractResourceTest(TenderContentWebTest, TenderContractResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_bids
    initial_lots = test_lots

    test_create_tender_contract = snitch(create_tender_contract)
    test_create_tender_contract_in_complete_status = snitch(create_tender_contract_in_complete_status)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)


class TenderContractVATNotIncludedResourceTest(TenderContentWebTest, TenderContractResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_bids
    initial_lots = test_lots

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
        super(TenderContractVATNotIncludedResourceTest, self).generate_bids(status, start_end)

    def calculate_agreement_contracts_value_amount(self, agreement, items):
        super(TenderContractVATNotIncludedResourceTest, self).calculate_agreement_contracts_value_amount(
            agreement, items
        )
        self.update_vat_fields(agreement["contracts"])

    test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)


@unittest.skip("Skip multi-lots tests")
class Tender2LotContractResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotContractResourceTest, self).setUp()
        # Create award

        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_organization],
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

    test_lot2_patch_tender_contract = snitch(lot2_patch_tender_contract)


class TenderContractDocumentResourceTest(TenderContentWebTest, TenderContractDocumentResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_bids
    initial_lots = test_lots
    docservice = True
    
    test_create_tender_contract_document_by_supplier = snitch(create_tender_contract_document_by_supplier)
    test_create_tender_contract_document_by_others = snitch(create_tender_contract_document_by_others)
    test_put_tender_contract_document_by_supplier = snitch(put_tender_contract_document_by_supplier)
    test_put_tender_contract_document_by_others = snitch(put_tender_contract_document_by_others)
    test_patch_tender_contract_document_by_supplier = snitch(patch_tender_contract_document_by_supplier)

@unittest.skip("Skip multi-lots tests")
class Tender2LotContractDocumentResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotContractDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))

        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_organization],
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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderContractDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderContractVATNotIncludedResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
