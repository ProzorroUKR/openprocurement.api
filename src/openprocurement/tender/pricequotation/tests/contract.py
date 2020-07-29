# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_bids,
    )
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderContractResourceTestMixin,
    TenderContractDocumentResourceTestMixin
    )
from openprocurement.tender.belowthreshold.tests.contract_blanks import (
    create_tender_contract,
    create_tender_contract_in_complete_status,
    patch_tender_contract_value,
    patch_tender_contract_status_by_owner,
    patch_tender_contract_status_by_supplier,
    patch_tender_contract_status_by_others,
    create_tender_contract_document_by_supplier,
    create_tender_contract_document_by_others,
    put_tender_contract_document_by_supplier,
    put_tender_contract_document_by_others,
    patch_tender_contract_document_by_supplier,
    )
from openprocurement.tender.pricequotation.tests.contract_blanks import (
    patch_tender_contract,
    patch_tender_contract_value_vat_not_included,
    )


class TenderContractResourceTest(TenderContentWebTest,
                                 TenderContractResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_bids

    def setUp(self):
        super(TenderContractResourceTest, self).setUp()
        self.award_id = self.award_ids[-1]
        resp = self.app.get(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
            )
        award = resp.json["data"]
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]
        self.award_items = award["items"]
        self.award_date = award["date"]

    test_create_tender_contract = snitch(create_tender_contract)
    test_create_tender_contract_in_complete_status = snitch(
        create_tender_contract_in_complete_status
    )
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)


class TenderContractVATNotIncludedResourceTest(TenderContentWebTest,
                                               TenderContractResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_bids

    def setUp(self):
        super(TenderContractVATNotIncludedResourceTest, self).setUp()
        self.award_id = self.award_ids[-1]
        resp = self.app.get(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
            )
        award = resp.json["data"]
        self.award_value = award["value"]
        self.award_suppliers = award["suppliers"]
        self.award_items = award["items"]

    test_patch_tender_contract_value_vat_not_included = snitch(
        patch_tender_contract_value_vat_not_included
    )
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)


class TenderContractDocumentResourceTest(TenderContentWebTest,
                                         TenderContractDocumentResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_bids
    docservice = True

    def setUp(self):
        super(TenderContractDocumentResourceTest, self).setUp()

    test_create_tender_contract_document_by_supplier = snitch(create_tender_contract_document_by_supplier)
    test_create_tender_contract_document_by_others = snitch(create_tender_contract_document_by_others)
    test_put_tender_contract_document_by_supplier = snitch(put_tender_contract_document_by_supplier)
    test_put_tender_contract_document_by_others = snitch(put_tender_contract_document_by_others)
    test_patch_tender_contract_document_by_supplier = snitch(patch_tender_contract_document_by_supplier)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderContractDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
