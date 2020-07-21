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

    test_create_tender_contract = snitch(create_tender_contract)
    test_create_tender_contract_in_complete_status = snitch(
        create_tender_contract_in_complete_status
    )
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)


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


class TenderContractDocumentResourceTest(TenderContentWebTest,
                                         TenderContractDocumentResourceTestMixin):
    initial_status = "active.awarded"
    initial_bids = test_bids

    def setUp(self):
        super(TenderContractDocumentResourceTest, self).setUp()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderContractDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
