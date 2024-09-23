import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardComplaintDocumentResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_award_document_json_bulk,
    create_tender_award_no_scale_invalid,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
    test_tender_below_organization,
)
from openprocurement.tender.limited.tests.award_blanks import (  # TenderAwardDocumentResourceTest; TenderNegotiationAwardComplaintDocumentResourceTest; Tender2LotNegotiationAwardComplaintResourceTest; TenderLotNegotiationAwardComplaintResourceTest; TenderNegotiationAwardComplaintResourceTest; TenderNegotiationLotAwardResourceTest; TenderNegotiationAwardResourceTest; TenderAwardComplaintResourceTest; TenderAwardResourceTest
    activate_contract_with_cancelled_award,
    bot_patch_tender_award_complaint,
    bot_patch_tender_award_complaint_forbidden,
    cancel_award,
    canceling_created_award_and_create_new_one,
    canceling_created_lot_award_and_create_new_one,
    cancelled_2lot_award_with_complaint,
    cancelled_active_award_with_complaint,
    cancelled_award_with_complaint,
    cancelled_lot_award_with_complaint,
    cancelled_unsuccessful_award_with_complaint,
    change_lotID_from_active_award,
    change_lotID_from_cancelled_award,
    change_lotID_from_unsuccessful_award,
    check_tender_award_complaint_period_dates,
    create_award_on_cancel_lot,
    create_award_with_lot,
    create_tender_award,
    create_tender_award_complaint_invalid,
    create_tender_award_complaints,
    create_tender_award_document_invalid,
    create_tender_award_invalid,
    create_tender_award_with_lot,
    create_tender_lot_award_complaints,
    create_tender_negotiation_award_complaints,
    create_two_awards_on_one_lot,
    get_tender_award,
    get_tender_award_complaint,
    get_tender_award_complaints,
    get_tender_lot_award,
    patch_active_not_qualified,
    patch_award_on_cancel_lot,
    patch_tender_award,
    patch_tender_award_complaint,
    patch_tender_award_complaint_document,
    patch_tender_award_unsuccessful,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    prolongation_award_is_forbidden,
    review_tender_award_complaint,
    review_tender_award_stopping_complaint,
    two_awards_on_one_lot,
    two_lot_two_awards,
)
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_lots,
    test_tender_negotiation_config,
    test_tender_negotiation_data,
    test_tender_negotiation_data_2items,
    test_tender_negotiation_quick_config,
    test_tender_negotiation_quick_data,
    test_tender_negotiation_quick_data_2items,
    test_tender_reporting_data,
)
from openprocurement.tender.limited.tests.utils import get_award_data


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderAwardResourceTest(BaseTenderContentWebTest):
    initial_status = "active"
    initial_data = test_tender_reporting_data
    test_tender_data_local = test_tender_reporting_data
    initial_bids = None

    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award = snitch(create_tender_award)
    test_canceling_created_award_and_create_new_one = snitch(canceling_created_award_and_create_new_one)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_get_tender_award = snitch(get_tender_award)
    test_activate_contract_with_cancelled_award = snitch(activate_contract_with_cancelled_award)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)
    test_prolongation_award_is_forbidden = snitch(prolongation_award_is_forbidden)


class TenderAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_status = "active"
    initial_data = test_tender_reporting_data
    initial_bids = None

    test_create_tender_award_complaints = snitch(create_tender_award_complaints)


class TenderNegotiationAwardResourceTest(TenderAwardResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config

    initial_lots = test_lots

    test_check_tender_award_complaint_period_dates = snitch(check_tender_award_complaint_period_dates)
    test_patch_active_not_qualified = snitch(patch_active_not_qualified)
    test_create_two_awards_on_one_lot = snitch(create_two_awards_on_one_lot)


class TenderNegotiationLotAwardResourceTest(TenderAwardResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    test_tender_negotiation_data_local = test_tender_negotiation_data
    test_tender_data_local = test_tender_reporting_data
    initial_lots = test_lots

    test_create_award_with_lot = snitch(create_award_with_lot)
    test_create_tender_award_with_lot = snitch(create_tender_award_with_lot)
    test_canceling_created_award_and_create_new_one = snitch(canceling_created_lot_award_and_create_new_one)
    test_patch_tender_award = snitch(patch_tender_lot_award)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_get_tender_award = snitch(get_tender_lot_award)
    test_two_lot_two_awards = snitch(two_lot_two_awards)
    test_cancel_award = snitch(cancel_award)
    test_create_award_on_cancel_lot = snitch(create_award_on_cancel_lot)
    test_patch_award_on_cancel_lot = snitch(patch_award_on_cancel_lot)


class TenderNegotiationQuickAwardResourceTest(TenderNegotiationAwardResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderNegotiationAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    initial_lots = test_lots

    def create_award(self):
        # Create award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path,
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "status": "pending",
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                    "lotID": self.initial_lots[0]["id"],
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

    def setUp(self):
        super().setUp()
        self.create_award()

    test_create_tender_award_complaint_invalid = snitch(create_tender_award_complaint_invalid)
    test_create_tender_award_complaints = snitch(create_tender_negotiation_award_complaints)
    test_patch_tender_award_complaint = snitch(patch_tender_award_complaint)
    test_review_tender_award_complaint = snitch(review_tender_award_complaint)
    test_review_tender_award_stopping_complaint = snitch(review_tender_award_stopping_complaint)
    test_get_tender_award_complaint = snitch(get_tender_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_award_complaints)
    test_cancelled_award_with_complaint = snitch(cancelled_award_with_complaint)
    test_bot_patch_tender_award_complaint = snitch(bot_patch_tender_award_complaint)
    test_bot_patch_tender_award_complaint_forbidden = snitch(bot_patch_tender_award_complaint_forbidden)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderLotNegotiationAwardComplaintResourceTest(TenderNegotiationAwardComplaintResourceTest):
    def create_award(self):
        # create lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.lot = response.json["data"]
        self.lot_id = self.lot["id"]

        # set items to lot

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = self.lot_id

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": items}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["items"][0]["relatedLot"], self.lot["id"])

        # create award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path,
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.lot["id"],
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

    test_create_tender_award_complaints = snitch(create_tender_lot_award_complaints)
    test_cancelled_award_with_complaint = snitch(cancelled_lot_award_with_complaint)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class Tender2LotNegotiationAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data_2items
    initial_config = test_tender_negotiation_config
    initial_lots = test_lots

    def setUp(self):
        super().setUp()
        self.create_award()

    def create_award(self):
        # create lots
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.first_lot = response.json["data"]

        self.assertEqual(response.content_type, "application/json")
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )
        self.assertEqual(response.status, "201 Created")
        self.second_lot = response.json["data"]

        # set items to lot

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = self.first_lot["id"]
        items[1]["relatedLot"] = self.second_lot["id"]

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": items}},
        )

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["items"][0]["relatedLot"], self.first_lot["id"])
        self.assertEqual(response.json["data"]["items"][1]["relatedLot"], self.second_lot["id"])

        # create first award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path,
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.first_lot["id"],
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.first_award = response.json["data"]
        self.award_id = self.first_award["id"]

        # create second award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path,
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.second_lot["id"],
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.second_award = response.json["data"]
        self.second_award_id = self.second_award["id"]

    test_cancelled_award_with_complaint = snitch(cancelled_2lot_award_with_complaint)
    test_cancelled_active_award_with_complaint = snitch(cancelled_active_award_with_complaint)
    test_cancelled_unsuccessful_award_with_complaint = snitch(cancelled_unsuccessful_award_with_complaint)


class Tender2LotNegotiationQuickAwardComplaintResourceTest(Tender2LotNegotiationAwardComplaintResourceTest):
    initial_data = test_tender_negotiation_quick_data_2items
    initial_config = test_tender_negotiation_quick_config
    initial_lots = test_lots


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class Tender2LotNegotiationAwardComplaint2ResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data_2items
    initial_config = test_tender_negotiation_config
    initial_lots = test_lots

    def setUp(self):
        super().setUp()
        self.create_award()

    def create_award(self):
        # create lots
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.first_lot = response.json["data"]

        self.assertEqual(response.content_type, "application/json")
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )
        self.assertEqual(response.status, "201 Created")
        self.second_lot = response.json["data"]

        # set items to lot

        response = self.app.get("/tenders/{}".format(self.tender_id))
        tender = response.json["data"]
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = self.first_lot["id"]
        items[1]["relatedLot"] = self.second_lot["id"]

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": items}},
        )

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["items"][0]["relatedLot"], self.first_lot["id"])
        self.assertEqual(response.json["data"]["items"][1]["relatedLot"], self.second_lot["id"])

        # create first award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path,
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.first_lot["id"],
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.first_award = response.json["data"]
        self.award_id = self.first_award["id"]

        # create second award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path,
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.second_lot["id"],
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.second_award = response.json["data"]
        self.second_award_id = self.second_award["id"]

    test_two_awards_on_one_lot = snitch(two_awards_on_one_lot)
    test_change_lotID_from_unsuccessful_award = snitch(change_lotID_from_unsuccessful_award)
    test_change_lotID_from_active_award = snitch(change_lotID_from_active_award)
    test_change_lotID_from_cancelled_award = snitch(change_lotID_from_cancelled_award)


class Tender2LotNegotiationQuickAwardComplaint2ResourceTest(Tender2LotNegotiationAwardComplaint2ResourceTest):
    initial_data = test_tender_negotiation_quick_data_2items
    initial_config = test_tender_negotiation_quick_config


class TenderNegotiationQuickAwardComplaintResourceTest(TenderNegotiationAwardComplaintResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


class TenderLotNegotiationQuickAwardComplaintResourceTest(TenderLotNegotiationAwardComplaintResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


class TenderNegotiationAwardComplaintDocumentResourceTest(
    BaseTenderContentWebTest, TenderAwardComplaintDocumentResourceTestMixin
):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config

    def setUp(self):
        super().setUp()
        # Create award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path,
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "status": "pending",
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints".format(self.tender_id, self.award_id),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class TenderNegotiationQuickAwardComplaintDocumentResourceTest(TenderNegotiationAwardComplaintDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


class TenderAwardDocumentResourceTest(BaseTenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active"
    initial_data = test_tender_reporting_data
    initial_bids = None

    def setUp(self):
        super().setUp()
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": get_award_data(self)},
        )
        award = response.json["data"]
        self.award_id = award["id"]

    test_create_tender_award_document_invalid = snitch(create_tender_award_document_invalid)
    test_patch_not_author = lambda x: 1  # disable edr bot test for now
    test_create_award_document_bot = lambda x: 1  # disable edr bot test for now

    test_create_tender_award_document_json_bulk = snitch(create_tender_award_document_json_bulk)


class TenderAwardNegotiationDocumentResourceTest(TenderAwardDocumentResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    initial_lots = test_lots


class TenderAwardNegotiationQuickDocumentResourceTest(TenderAwardNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
    initial_lots = test_lots


class TenderLotAwardNegotiationDocumentResourceTest(TenderAwardNegotiationDocumentResourceTest):
    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        # Create lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": test_lots[0]}
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        lot = response.json["data"]
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": lot["id"],
                    "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]


class TenderLotAwardNegotiationQuickDocumentResourceTest(TenderLotAwardNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
