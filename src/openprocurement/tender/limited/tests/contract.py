# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderContractResourceTestMixin,
    TenderContractDocumentResourceTestMixin,
)

from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_lots,
    test_tender_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
)
from openprocurement.tender.limited.tests.contract_blanks import (
    # TenderNegotiationQuickAccelerationTest
    create_tender_contract_negotiation_quick,
    # TenderNegotiationLot2ContractResourceTest
    sign_second_contract,
    create_two_contract,
    # TenderNegotiationLotContractResourceTest
    lot_items,
    lot_award_id_change_is_not_allowed,
    activate_contract_cancelled_lot,
    # TenderNegotiationContractResourceTest
    patch_tender_negotiation_contract,
    tender_negotiation_contract_signature_date,
    items,
    # TenderContractResourceTest
    create_tender_contract,
    patch_tender_contract,
    tender_contract_signature_date,
    award_id_change_is_not_allowed,
    create_tender_contract_document,
    patch_tender_contract_document,
    put_tender_contract_document,
)
from openprocurement.tender.belowthreshold.tests.contract_blanks import (
    patch_tender_contract_value_vat_not_included,
    patch_tender_contract_value,
)


class TenderContractResourceTest(BaseTenderContentWebTest, TenderContractResourceTestMixin):
    initial_status = "active"
    initial_data = test_tender_data
    initial_bids = None  # test_bids
    docservice = True
    
    def create_award(self):
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                }
            },
        )

        award = response.json["data"]
        self.award_id = award["id"]
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )

    def setUp(self):
        super(TenderContractResourceTest, self).setUp()
        self.create_award()

    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_tender_contract_signature_date = snitch(tender_contract_signature_date)
    test_award_id_change_is_not_allowed = snitch(award_id_change_is_not_allowed)


class TenderContractVATNotIncludedResourceTest(BaseTenderContentWebTest, TenderContractResourceTestMixin):
    initial_status = "active"
    initial_data = test_tender_data
    initial_bids = None

    def create_award(self):
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )

        self.award_id = response.json["data"]["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )

    def setUp(self):
        super(TenderContractVATNotIncludedResourceTest, self).setUp()
        self.create_award()

    test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)


class TenderNegotiationContractResourceTest(TenderContractResourceTest):
    initial_data = test_tender_negotiation_data
    stand_still_period_days = 10

    test_patch_tender_contract = snitch(patch_tender_negotiation_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_tender_contract_signature_date = snitch(tender_negotiation_contract_signature_date)
    test_items = snitch(items)


class TenderNegotiationContractVATNotIncludedResourceTest(TenderContractVATNotIncludedResourceTest):
    initial_data = test_tender_negotiation_data


class TenderNegotiationLotContractResourceTest(TenderNegotiationContractResourceTest):
    initial_data = test_tender_negotiation_data
    stand_still_period_days = 10

    def create_award(self):
        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": self.initial_data["items"]}},
        )

        # create lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        lot1 = response.json["data"]
        self.lot1 = lot1

        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": [{"relatedLot": lot1["id"]}]}},
        )
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": lot1["id"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )

    test_items = snitch(lot_items)
    test_award_id_change_is_not_allowed = snitch(lot_award_id_change_is_not_allowed)
    test_activate_contract_cancelled_lot = snitch(activate_contract_cancelled_lot)


class TenderNegotiationLot2ContractResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data
    stand_still_period_days = 10

    def setUp(self):
        super(TenderNegotiationLot2ContractResourceTest, self).setUp()
        self.create_award()

    def create_award(self):
        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": self.initial_data["items"] * 2}},
        )

        # create lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        lot1 = response.json["data"]
        self.lot1 = lot1

        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        lot2 = response.json["data"]
        self.lot2 = lot2

        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": [{"relatedLot": lot1["id"]}, {"relatedLot": lot2["id"]}]}},
        )

        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": lot1["id"],
                }
            },
        )

        award = response.json["data"]
        self.award1_id = award["id"]
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award1_id, self.tender_token),
            {"data": {"status": "active"}},
        )

        # Create another award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": lot2["id"],
                }
            },
        )

        award = response.json["data"]
        self.award2_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award2_id, self.tender_token),
            {"data": {"status": "active"}},
        )

    test_sign_second_contract = snitch(sign_second_contract)
    test_create_two_contract = snitch(create_two_contract)


class TenderNegotiationQuickContractResourceTest(TenderNegotiationContractResourceTest):
    initial_data = test_tender_negotiation_quick_data
    stand_still_period_days = 5


class TenderNegotiationQuickLotContractResourceTest(TenderNegotiationLotContractResourceTest):
    initial_data = test_tender_negotiation_quick_data
    stand_still_period_days = 5


class TenderNegotiationQuickAccelerationTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_quick_data
    stand_still_period_days = 5
    accelerator = "quick,accelerator=172800"  # 5 days=432000 sec; 432000/172800=2.5 sec
    time_sleep_in_sec = 3  # time which reduced

    def create_award(self):
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"suppliers": [test_organization], "status": "pending"}},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {
                "data": {
                    "status": "active",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                }
            },
        )

    def setUp(self):
        super(TenderNegotiationQuickAccelerationTest, self).setUp()
        if SANDBOX_MODE:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
                {"data": {"procurementMethodDetails": self.accelerator}},
            )
            self.assertEqual(response.status, "200 OK")
        self.create_award()

    test_create_tender_contract_negotiation_quick = snitch(create_tender_contract_negotiation_quick)


class TenderNegotiationQuickLotAccelerationTest(TenderNegotiationQuickAccelerationTest):
    initial_data = test_tender_negotiation_quick_data
    stand_still_period_days = 5
    accelerator = "quick,accelerator=172800"  # 5 days=432000 sec; 432000/172800=2.5 sec
    time_sleep_in_sec = 3  # time which reduced

    def create_award(self):
        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": self.initial_data["items"] * 2}},
        )

        # create lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        lot1 = response.json["data"]
        self.lot1 = lot1

        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": [{"relatedLot": lot1["id"]}]}},
        )
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": lot1["id"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )


class TenderNegotiationAccelerationTest(TenderNegotiationQuickAccelerationTest):
    stand_still_period_days = 10
    time_sleep_in_sec = 6


class TenderContractDocumentResourceTest(BaseTenderContentWebTest, TenderContractDocumentResourceTestMixin):
    initial_status = "active"
    initial_bids = None
    docservice = True

    def create_award(self):
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"suppliers": [test_organization], "status": "pending"}},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {
                "data": {
                    "status": "active",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                }
            },
        )

    def setUp(self):
        super(TenderContractDocumentResourceTest, self).setUp()
        self.create_award()
        response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
        self.contract_id = response.json["data"][0]["id"]

    test_create_tender_contract_document = snitch(create_tender_contract_document)
    test_patch_tender_contract_document = snitch(patch_tender_contract_document)
    test_put_tender_contract_document = snitch(put_tender_contract_document)
    test_create_contract_documents_by_render_bot = None
    test_create_contract_documents_by_render_bot_invalid = None
    test_create_contract_document_contract_data_by_owner = None
    test_create_contract_document_second_contract_data_by_owner_fail = None
    test_put_contract_document_contract_data_by_owner = None
    test_put_contract_document_contract_data_by_rbot = None


class TenderContractNegotiationDocumentResourceTest(TenderContractDocumentResourceTest):
    initial_data = test_tender_negotiation_data


class TenderContractNegotiationLotDocumentResourceTest(TenderContractDocumentResourceTest):
    initial_data = test_tender_negotiation_data

    def create_award(self):
        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": self.initial_data["items"] * 2}},
        )

        # create lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        lot1 = response.json["data"]
        self.lot1 = lot1

        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": [{"relatedLot": lot1["id"]}]}},
        )

        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": lot1["id"],
                }
            },
        )

        award = response.json["data"]
        self.award_id = award["id"]
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )


class TenderContractNegotiationQuickDocumentResourceTest(TenderContractNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderContractNegotiationQuickLotDocumentResourceTest(TenderContractNegotiationLotDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderContractDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
