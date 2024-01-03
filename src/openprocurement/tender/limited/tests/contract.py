# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch
from datetime import timedelta
from copy import deepcopy

from openprocurement.api.utils import get_now
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderContractResourceTestMixin,
    TenderContractDocumentResourceTestMixin,
    TenderEcontractResourceTestMixin,
    TenderEContractMultiBuyersResourceTestMixin,
)

from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_lots,
    test_tender_reporting_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
    test_tender_data_multi_buyers,
    test_tender_negotiation_data_multi_buyers,
    test_tender_negotiation_quick_data_multi_buyers,
    test_tender_negotiation_data_2items,
    test_tender_negotiation_config,
    test_tender_negotiation_quick_config,
)
from openprocurement.tender.limited.tests.contract_blanks import (
    create_tender_contract_negotiation_quick,
    sign_second_contract,
    create_two_contract,
    lot_items,
    lot_award_id_change_is_not_allowed,
    activate_contract_cancelled_lot,
    patch_tender_negotiation_contract,
    tender_negotiation_contract_signature_date,
    items,
    create_tender_contract,
    patch_tender_contract,
    tender_contract_signature_date,
    award_id_change_is_not_allowed,
    create_tender_contract_document,
    patch_tender_contract_document,
    put_tender_contract_document,
    # EContract
    patch_tender_negotiation_econtract
)
from openprocurement.tender.belowthreshold.tests.contract_blanks import (
    patch_tender_contract_value_vat_not_included,
    patch_tender_contract_value,
    patch_contract_single_item_unit_value,
    patch_contract_single_item_unit_value_with_status,
    patch_tender_multi_contracts,
    patch_tender_multi_contracts_cancelled,
    patch_tender_multi_contracts_cancelled_with_one_activated,
    patch_tender_multi_contracts_cancelled_validate_amount,
)


class CreateActiveAwardMixin:
    def create_award(self):
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"suppliers": [test_tender_below_organization], "status": "pending",
                      "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True}}},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
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


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractResourceTest(BaseTenderContentWebTest, CreateActiveAwardMixin, TenderContractResourceTestMixin):
    initial_status = "active"
    initial_data = test_tender_reporting_data
    initial_bids = None  # test_bids

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super(TenderContractResourceTest, self).setUp()
        self.create_award()

    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract = snitch(patch_tender_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_tender_contract_signature_date = snitch(tender_contract_signature_date)
    test_award_id_change_is_not_allowed = snitch(award_id_change_is_not_allowed)
    test_patch_contract_single_item_unit_value = snitch(patch_contract_single_item_unit_value)
    test_patch_contract_single_item_unit_value_with_status = snitch(
        patch_contract_single_item_unit_value_with_status
    )


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractVATNotIncludedResourceTest(BaseTenderContentWebTest, TenderContractResourceTestMixin):
    initial_status = "active"
    initial_data = test_tender_reporting_data
    initial_bids = None

    def create_award(self):
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
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

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super(TenderContractVATNotIncludedResourceTest, self).setUp()
        self.create_award()

    test_patch_tender_contract_value_vat_not_included = snitch(patch_tender_contract_value_vat_not_included)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationContractResourceTest(TenderContractResourceTest):
    initial_data = test_tender_negotiation_data
    stand_still_period_days = 10
    initial_config = test_tender_negotiation_config

    test_patch_tender_contract = snitch(patch_tender_negotiation_contract)
    test_patch_tender_contract_value = snitch(patch_tender_contract_value)
    test_tender_contract_signature_date = snitch(tender_negotiation_contract_signature_date)
    test_items = snitch(items)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationContractVATNotIncludedResourceTest(TenderContractVATNotIncludedResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config


class TenderNegotiationLotMixin:
    def create_award(self):
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.lot1 = response.json["data"]["lots"][0]

        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": self.lot1["id"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationLotContractResourceTest(TenderNegotiationLotMixin, TenderNegotiationContractResourceTest):
    initial_status = "active"
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    stand_still_period_days = 10
    initial_lots = test_lots

    test_items = snitch(lot_items)
    test_award_id_change_is_not_allowed = snitch(lot_award_id_change_is_not_allowed)
    test_activate_contract_cancelled_lot = snitch(activate_contract_cancelled_lot)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationLot2ContractResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data_2items
    initial_config = test_tender_negotiation_config
    initial_lots = test_lots * 2
    stand_still_period_days = 10

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super(TenderNegotiationLot2ContractResourceTest, self).setUp()
        self.create_award()

    def create_award(self):
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.lot1 = response.json["data"]["lots"][0]
        self.lot2 = response.json["data"]["lots"][1]

        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": self.lot1["id"],
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
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "qualified": True,
                    "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                    "lotID": self.lot2["id"],
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


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationQuickContractResourceTest(TenderNegotiationContractResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
    stand_still_period_days = 5


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationQuickLotContractResourceTest(TenderNegotiationLotContractResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
    stand_still_period_days = 5


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationQuickAccelerationTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
    stand_still_period_days = 5
    accelerator = "quick,accelerator=172800"  # 5 days=432000 sec; 432000/172800=2.5 sec
    time_sleep_in_sec = 3  # time which reduced
    initial_lots = test_lots

    def create_award(self):
        response = self.app.get(f"/tenders/{self.tender_id}")
        tender_lots = response.json["data"]["lots"]
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {
                "lotID": tender_lots[0]["id"],
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True}
            }},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {
                "data": {
                    "status": "active",
                    "qualified": True,
                }
            },
        )

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
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


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationQuickLotAccelerationTest(TenderNegotiationQuickAccelerationTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
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

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = self.lot1["id"]
        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": items}},
        )
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
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


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationAccelerationTest(TenderNegotiationQuickAccelerationTest):
    stand_still_period_days = 10
    time_sleep_in_sec = 6


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractDocumentResourceTest(
    BaseTenderContentWebTest,
    CreateActiveAwardMixin,
    TenderContractDocumentResourceTestMixin,
):
    initial_status = "active"
    initial_bids = None
    docservice = True

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super(TenderContractDocumentResourceTest, self).setUp()
        self.create_award()
        response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
        self.contract_id = response.json["data"][0]["id"]

    test_create_tender_contract_document = snitch(create_tender_contract_document)
    test_patch_tender_contract_document = snitch(patch_tender_contract_document)
    test_put_tender_contract_document = snitch(put_tender_contract_document)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractNegotiationDocumentResourceTest(TenderContractDocumentResourceTest, TenderNegotiationLotMixin):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractNegotiationLotDocumentResourceTest(TenderContractDocumentResourceTest, TenderNegotiationLotMixin):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    initial_lots = test_lots

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

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = self.lot1["id"]
        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": items}},
        )

        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
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


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractNegotiationQuickDocumentResourceTest(TenderContractNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractNegotiationQuickLotDocumentResourceTest(TenderContractNegotiationLotDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderContractMultiBuyersResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_data_multi_buyers
    stand_still_period_days = 10

    @patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
    def setUp(self):
        super(TenderContractMultiBuyersResourceTest, self).setUp()
        TenderContractResourceTest.create_award(self)

    test_patch_tender_multi_contracts = snitch(patch_tender_multi_contracts)
    test_patch_tender_multi_contracts_cancelled = snitch(patch_tender_multi_contracts_cancelled)
    test_patch_tender_multi_contracts_cancelled_with_one_activated = snitch(
        patch_tender_multi_contracts_cancelled_with_one_activated
    )
    test_patch_tender_multi_contracts_cancelled_validate_amount = snitch(
        patch_tender_multi_contracts_cancelled_validate_amount
    )


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationMultiBuyersContractResourceTest(TenderContractMultiBuyersResourceTest):
    initial_data = test_tender_negotiation_data_multi_buyers
    initial_config = test_tender_negotiation_config
    stand_still_period_days = 10


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() + timedelta(days=1))
class TenderNegotiationQuickMultiBuyersContractResourceTest(TenderNegotiationMultiBuyersContractResourceTest):
    initial_data = test_tender_negotiation_quick_data_multi_buyers
    initial_config = test_tender_negotiation_quick_config
    stand_still_period_days = 10


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
class TenderReportingEContractResourceTest(
    BaseTenderContentWebTest,
    CreateActiveAwardMixin,
    TenderEcontractResourceTestMixin
):
    initial_status = "active"
    initial_data = test_tender_reporting_data
    initial_bids = None

    def setUp(self):
        super().setUp()
        self.create_award()


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
class TenderNegotiationEContractResourceTest(TenderReportingEContractResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    stand_still_period_days = 10

    test_patch_tender_econtract = snitch(patch_tender_negotiation_econtract)


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
class TenderNegotiationQuickEContractResourceTest(TenderNegotiationEContractResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
    stand_still_period_days = 5


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
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


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
class TenderNegotiationEContractMultiBuyersResourceTest(
    TenderReportingEContractMultiBuyersResourceTest
):
    initial_data = test_tender_negotiation_data_multi_buyers
    initial_config = test_tender_negotiation_config


@patch("openprocurement.tender.core.procedure.utils.NEW_CONTRACTING_FROM", get_now() - timedelta(days=1))
class TenderNegotiationEContractMultiBuyersResourceTest(
    TenderReportingEContractMultiBuyersResourceTest
):
    initial_data = test_tender_negotiation_quick_data_multi_buyers
    initial_config = test_tender_negotiation_quick_config


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderContractDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
