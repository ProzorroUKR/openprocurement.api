# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from datetime import timedelta

import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now

from openprocurement.tender.belowthreshold.tests.base import test_lots, test_organization, test_draft_complaint

from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardResourceTestMixin,
    TenderAwardComplaintResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
    Tender2LotAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    # TenderLotAwardComplaintResourceTest
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    # Tender2LotAwardComplaintDocumentResourceTest
    create_tender_lots_award_complaint_document,
    # TenderLotAwardResourceTest
    patch_tender_lot_award_lots_none,
)

from openprocurement.tender.openua.tests.base import test_bids, BaseTenderUAContentWebTest
from openprocurement.tender.openua.tests.award_blanks import (
    # TenderAwardResourceTest
    create_tender_award,
    patch_tender_award,
    check_tender_award_complaint_period_dates,
    patch_tender_award_active,
    patch_tender_award_unsuccessful,
    create_tender_award_no_scale_invalid,
    # TenderAwardResourceScaleTest
    create_tender_award_with_scale_not_required,
    create_tender_award_no_scale,
    # TenderLotAwardResourceTest
    create_tender_lot_award,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    # Tender2LotAwardResourceTest
    create_tender_lots_award,
    patch_tender_lots_award,
    # TenderAwardComplaintResourceTest
    create_tender_award_claim,
    create_tender_award_complaint_not_active,
    create_tender_award_complaint_after_2020_04_19,
    create_tender_award_complaint,
    patch_tender_award_complaint,
    review_tender_award_complaint,
    review_tender_award_claim,
    review_tender_award_stopping_complaint,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_award_complaint,
    patch_tender_lot_award_complaint,
    # Tender2LotAwardComplaintResourceTest
    create_tender_lots_award_complaint,
    patch_tender_lots_award_complaint,
    # TenderAwardComplaintDocumentResourceTest
    patch_tender_award_complaint_document,
    # Tender2LotAwardComplaintDocumentResourceTest
    put_tender_lots_award_complaint_document,
    patch_tender_lots_award_complaint_document,
    tender_award_complaint_period,
    bot_patch_tender_award_complaint,
    bot_patch_tender_award_complaint_forbidden,
)


class TenderUAAwardComplaintResourceTestMixin(object):
    test_create_tender_award_claim = snitch(create_tender_award_claim)
    test_create_tender_award_complaint_not_active = snitch(create_tender_award_complaint_not_active)
    test_create_tender_award_complaint_after_2020_04_19 = snitch(create_tender_award_complaint_after_2020_04_19)
    test_create_tender_award_complaint = snitch(create_tender_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_award_complaint)
    test_review_tender_award_complaint = snitch(review_tender_award_complaint)
    test_review_tender_award_claim = snitch(review_tender_award_claim)
    test_review_tender_award_stopping_complaint = snitch(review_tender_award_stopping_complaint)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)
    test_bot_patch_tender_award_complaint = snitch(bot_patch_tender_award_complaint)
    test_bot_patch_tender_award_complaint_forbidden = snitch(bot_patch_tender_award_complaint_forbidden)


class TenderAwardResourceTest(BaseTenderUAContentWebTest, TenderAwardResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids

    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_tender_award_complaint_period = snitch(tender_award_complaint_period)


class TenderAwardResourceScaleTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"

    def setUp(self):
        patcher = mock.patch("openprocurement.api.models.ORGANIZATION_SCALE_FROM", get_now() + timedelta(days=1))
        patcher.start()
        self.addCleanup(patcher.stop)
        test_bid = deepcopy(test_bids[0])
        test_bid["tenderers"][0].pop("scale")
        self.initial_bids = [test_bid]
        super(TenderAwardResourceScaleTest, self).setUp()
        self.app.authorization = ("Basic", ("token", ""))

    test_create_tender_award_with_scale_not_required = snitch(create_tender_award_with_scale_not_required)
    test_create_tender_award_with_no_scale = snitch(create_tender_award_no_scale)


class TenderLotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_lot_award = snitch(create_tender_lot_award)
    test_patch_tender_lot_award = snitch(patch_tender_lot_award)
    test_patch_tender_lot_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class Tender2LotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_tender_lots_award = snitch(create_tender_lots_award)
    test_patch_tender_lots_award = snitch(patch_tender_lots_award)


class TenderAwardComplaintResourceTest(
    BaseTenderUAContentWebTest, TenderAwardComplaintResourceTestMixin, TenderUAAwardComplaintResourceTestMixin
):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {"suppliers": [test_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.app.authorization = auth
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class TenderLotAwardComplaintResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_lots
    initial_bids = test_bids

    def setUp(self):
        super(TenderLotAwardComplaintResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": bid["lotValues"][0]["relatedLot"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = auth

    test_create_tender_lot_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_lot_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_lot_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_lot_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest):
    initial_lots = 2 * test_lots

    test_create_tender_lots_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_lots_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderAwardComplaintDocumentResourceTest(
    BaseTenderUAContentWebTest, TenderAwardComplaintDocumentResourceTestMixin
):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {"suppliers": [test_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.app.authorization = auth

        # Create complaint for award
        bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": bid["lotValues"][0]["relatedLot"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.app.authorization = auth
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_lots_award_document = snitch(create_tender_lots_award_complaint_document)
    test_put_tender_lots_award_complaint_document = snitch(put_tender_lots_award_complaint_document)
    test_patch_tender_lots_award_complaint_document = snitch(patch_tender_lots_award_complaint_document)


class TenderAwardDocumentResourceTest(BaseTenderUAContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {"suppliers": [test_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = auth


class Tender2LotAwardDocumentResourceTest(BaseTenderUAContentWebTest, Tender2LotAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": bid["lotValues"][0]["relatedLot"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = auth


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tender2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
