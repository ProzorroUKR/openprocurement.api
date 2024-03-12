import unittest
from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from esculator import escp, npv

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderContractDocumentResourceTestMixin,
    TenderContractResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.contract_blanks import (
    create_tender_contract_document_by_others,
    create_tender_contract_document_by_supplier,
    patch_tender_contract_document_by_supplier,
    patch_tender_contract_status_by_others,
    patch_tender_contract_status_by_owner,
    patch_tender_contract_status_by_supplier,
    put_tender_contract_document_by_others,
    put_tender_contract_document_by_supplier,
)
from openprocurement.tender.esco.procedure.utils import to_decimal
from openprocurement.tender.esco.tests.base import (
    NBU_DISCOUNT_RATE,
    BaseESCOContentWebTest,
    test_tender_esco_bids,
)
from openprocurement.tender.esco.tests.contract_blanks import (  # TenderContractResourceTest; EContract
    patch_econtract,
    patch_tender_contract,
)
from openprocurement.tender.openeu.tests.base import test_tender_openeu_data
from openprocurement.tender.openeu.tests.contract_blanks import (  # TenderContractResourceTest
    contract_termination,
)
from openprocurement.tender.openua.tests.contract_blanks import (
    create_tender_contract,
    patch_tender_contract_datesigned,
)

amount_precision = 2

contract_amount_performance = to_decimal(
    npv(
        test_tender_esco_bids[0]["value"]["contractDuration"]["years"],
        test_tender_esco_bids[0]["value"]["contractDuration"]["days"],
        test_tender_esco_bids[0]["value"]["yearlyPaymentsPercentage"],
        test_tender_esco_bids[0]["value"]["annualCostsReduction"],
        get_now(),
        NBU_DISCOUNT_RATE,
    )
).quantize(Decimal(f"1E-{amount_precision}"))

contract_amount = to_decimal(
    escp(
        test_tender_esco_bids[0]["value"]["contractDuration"]["years"],
        test_tender_esco_bids[0]["value"]["contractDuration"]["days"],
        test_tender_esco_bids[0]["value"]["yearlyPaymentsPercentage"],
        test_tender_esco_bids[0]["value"]["annualCostsReduction"],
        get_now(),
    )
).quantize(Decimal(f"1E-{amount_precision}"))


class CreateAwardMixin:
    def create_award(self):
        self.supplier_info = deepcopy(test_tender_below_organization)
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [self.supplier_info],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "value": self.initial_bids[0]["value"],
                    "items": test_tender_openeu_data["items"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )

        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contracts_ids = [i["id"] for i in response.json["data"].get("contracts", "")]
        self.bid_token = self.initial_bids_tokens[award["bid_id"]]


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractResourceTest(BaseESCOContentWebTest, CreateAwardMixin, TenderContractResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_esco_bids
    author_data = test_tender_below_author
    initial_auth = ("Basic", ("broker", ""))
    expected_contract_amountPerformance = contract_amount_performance
    expected_contract_amount = contract_amount

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super().setUp()
        self.create_award()

    test_contract_termination = snitch(contract_termination)
    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_status_by_owner = snitch(patch_tender_contract_status_by_owner)
    test_patch_tender_contract_status_by_others = snitch(patch_tender_contract_status_by_others)
    test_patch_tender_contract_status_by_supplier = snitch(patch_tender_contract_status_by_supplier)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractDocumentResourceTest(BaseESCOContentWebTest, TenderContractDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_esco_bids
    initial_auth = ("Basic", ("broker", ""))
    docservice = True

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super().setUp()
        # Create award
        supplier_info = deepcopy(test_tender_below_organization)
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {"suppliers": [supplier_info], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        response = self.app.patch_json(
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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderContractDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
