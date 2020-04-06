# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_award_no_scale_invalid,
    create_tender_award_with_scale_not_required,
    create_tender_award_no_scale,
    patch_tender_lot_award_lots_none,
)
from openprocurement.tender.belowthreshold.tests.base import test_organization, test_author, test_draft_claim
from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardDocumentResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
)
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_tender_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
    test_lots,
    test_tender_negotiation_data_2items,
    test_tender_negotiation_quick_data_2items,
)
from openprocurement.tender.limited.tests.award_blanks import (
    # TenderAwardDocumentResourceTest
    create_tender_award_document_invalid,
    # TenderNegotiationAwardComplaintDocumentResourceTest
    patch_tender_award_complaint_document,
    # Tender2LotNegotiationAwardComplaintResourceTest
    two_awards_on_one_lot,
    change_lotID_from_unsuccessful_award,
    change_lotID_from_active_award,
    change_lotID_from_cancelled_award,
    # Tender2LotNegotiationAwardComplaintResourceTest
    cancelled_2lot_award_with_complaint,
    cancelled_active_award_with_complaint,
    cancelled_unsuccessful_award_with_complaint,
    # TenderLotNegotiationAwardComplaintResourceTest
    create_tender_lot_award_complaints,
    cancelled_lot_award_with_complaint,
    # TenderNegotiationAwardComplaintResourceTest
    create_tender_award_complaint_invalid,
    create_tender_negotiation_award_complaints,
    patch_tender_award_complaint,
    bot_patch_tender_award_complaint,
    bot_patch_tender_award_complaint_forbidden,
    review_tender_award_complaint,
    review_tender_award_stopping_complaint,
    get_tender_award_complaint,
    get_tender_award_complaints,
    cancelled_award_with_complaint,
    # TenderNegotiationLotAwardResourceTest
    create_award_with_lot,
    create_tender_award_with_lot,
    canceling_created_lot_award_and_create_new_one,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    get_tender_lot_award,
    two_lot_two_awards,
    cancel_award,
    create_award_on_cancel_lot,
    patch_award_on_cancel_lot,
    # TenderNegotiationAwardResourceTest
    patch_tender_award_Administrator_change,
    patch_active_not_qualified,
    create_two_awards_on_one_lot,
    # TenderAwardComplaintResourceTest
    create_tender_award_complaints,
    # TenderAwardResourceTest
    create_tender_award_invalid,
    create_tender_award,
    canceling_created_award_and_create_new_one,
    patch_tender_award,
    patch_tender_award_unsuccessful,
    get_tender_award,
    activate_contract_with_cancelled_award,
    check_tender_award_complaint_period_dates,
)


class TenderAwardResourceTest(BaseTenderContentWebTest):
    initial_status = "active"
    initial_data = test_tender_data
    test_tender_data_local = test_tender_data
    initial_bids = None

    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award = snitch(create_tender_award)
    test_canceling_created_award_and_create_new_one = snitch(canceling_created_award_and_create_new_one)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_get_tender_award = snitch(get_tender_award)
    test_activate_contract_with_cancelled_award = snitch(activate_contract_with_cancelled_award)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)
    test_create_tender_award_with_scale_not_required = snitch(create_tender_award_with_scale_not_required)
    test_create_tender_award_with_no_scale = snitch(create_tender_award_no_scale)


class TenderAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_status = "active"
    initial_data = test_tender_data
    initial_bids = None

    test_create_tender_award_complaints = snitch(create_tender_award_complaints)


class TenderNegotiationAwardResourceTest(TenderAwardResourceTest):
    initial_data = test_tender_negotiation_data

    test_lots_data = test_lots  # TODO: change attribute identifier

    test_check_tender_award_complaint_period_dates = snitch(check_tender_award_complaint_period_dates)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)
    test_patch_active_not_qualified = snitch(patch_active_not_qualified)
    test_create_two_awards_on_one_lot = snitch(create_two_awards_on_one_lot)


class TenderNegotiationLotAwardResourceTest(TenderAwardResourceTest):
    initial_data = test_tender_negotiation_data
    test_tender_negotiation_data_local = test_tender_negotiation_data
    test_tender_data_local = test_tender_data
    test_lots_data = test_lots  # TODO: change attribute identifier

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


class TenderNegotiation2LotAwardResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data
    initial_lots = 2 * test_lots

    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class TenderNegotiationQuickAwardResourceTest(TenderNegotiationAwardResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderNegotiationAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data

    def create_award(self):
        # Create award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path, {"data": {"suppliers": [test_organization], "qualified": True, "status": "pending"}}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

    def setUp(self):
        super(TenderNegotiationAwardComplaintResourceTest, self).setUp()
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


class TenderLotNegotiationAwardComplaintResourceTest(TenderNegotiationAwardComplaintResourceTest):
    test_create_tender_award_complaints = snitch(create_tender_lot_award_complaints)

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
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": [{"relatedLot": self.lot["id"]}]}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["items"][0]["relatedLot"], self.lot["id"])

        # create award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path,
            {
                "data": {
                    "suppliers": [test_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.lot["id"],
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]

    test_cancelled_award_with_complaint = snitch(cancelled_lot_award_with_complaint)


class Tender2LotNegotiationAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data_2items

    def setUp(self):
        super(Tender2LotNegotiationAwardComplaintResourceTest, self).setUp()
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
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": [{"relatedLot": self.first_lot["id"]}, {"relatedLot": self.second_lot["id"]}]}},
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
                    "suppliers": [test_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.first_lot["id"],
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
                    "suppliers": [test_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.second_lot["id"],
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


class Tender2LotNegotiationAwardComplaint2ResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data_2items

    def setUp(self):
        super(Tender2LotNegotiationAwardComplaint2ResourceTest, self).setUp()
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
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"items": [{"relatedLot": self.first_lot["id"]}, {"relatedLot": self.second_lot["id"]}]}},
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
                    "suppliers": [test_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.first_lot["id"],
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
                    "suppliers": [test_organization],
                    "qualified": True,
                    "status": "pending",
                    "lotID": self.second_lot["id"],
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


class TenderNegotiationQuickAwardComplaintResourceTest(TenderNegotiationAwardComplaintResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderLotNegotiationQuickAwardComplaintResourceTest(TenderLotNegotiationAwardComplaintResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderNegotiationAwardComplaintDocumentResourceTest(
    BaseTenderContentWebTest, TenderAwardComplaintDocumentResourceTestMixin
):
    initial_data = test_tender_negotiation_data

    def setUp(self):
        super(TenderNegotiationAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
        response = self.app.post_json(
            request_path, {"data": {"suppliers": [test_organization], "qualified": True, "status": "pending"}}
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.award_id = award["id"]
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints".format(self.tender_id, self.award_id),
            {"data": test_draft_claim},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class TenderNegotiationQuickAwardComplaintDocumentResourceTest(TenderNegotiationAwardComplaintDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderAwardDocumentResourceTest(BaseTenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active"
    initial_data = test_tender_data
    initial_bids = None

    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"suppliers": [test_organization], "qualified": True, "status": "pending"}},
        )
        award = response.json["data"]
        self.award_id = award["id"]

    test_create_tender_award_document_invalid = snitch(create_tender_award_document_invalid)
    test_patch_not_author = lambda x: 1  # disable edr bot test for now
    test_create_award_document_bot = lambda x: 1  # disable edr bot test for now


class TenderAwardNegotiationDocumentResourceTest(TenderAwardDocumentResourceTest):
    initial_data = test_tender_negotiation_data


class TenderAwardNegotiationQuickDocumentResourceTest(TenderAwardNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


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
            {"data": {"suppliers": [test_organization], "qualified": True, "status": "pending", "lotID": lot["id"]}},
        )
        award = response.json["data"]
        self.award_id = award["id"]


class TenderLotAwardNegotiationQuickDocumentResourceTest(TenderLotAwardNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
