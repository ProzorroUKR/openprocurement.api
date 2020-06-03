# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
import dateutil

from datetime import timedelta

import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now

from openprocurement.tender.belowthreshold.tests.base import test_organization, test_draft_complaint
from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardComplaintResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
    Tender2LotAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    # TenderLotAwardComplaintResourceTest
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    # TenderLotAwardResourceTestMixin
    patch_tender_lot_award_lots_none,
)

from openprocurement.tender.openua.tests.award import TenderUAAwardComplaintResourceTestMixin
from openprocurement.tender.openua.tests.award_blanks import (
    # Tender2LotAwardComplaintResourceTest
    create_tender_lots_award_complaint,
    patch_tender_lots_award_complaint,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_award_complaint,
    patch_tender_lot_award_complaint,
    # TenderAwardResourceTest
    create_tender_award_no_scale_invalid,
    # TenderAwardResourceScaleTest
    create_tender_award_with_scale_not_required,
    create_tender_award_no_scale,
)

from openprocurement.tender.openeu.tests.award_blanks import (
    # Tender2LotAwardComplaintDocumentResourceTest
    patch_tender_award_complaint_document,
    # TenderAwardComplaintDocumentResourceTest
    create_tender_2lot_award_complaint_document,
    put_tender_2lot_award_complaint_document,
    patch_tender_2lot_award_complaint_document,
    # Tender2LotAwardResourceTest
    create_tender_2lot_award,
    patch_tender_2lot_award,
    # TenderLotAwardResourceTest
    create_tender_lot_award,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    # TenderAwardResourceTest
    create_tender_award_invalid,
    create_tender_award,
    get_tender_award,
    patch_tender_award,
    patch_tender_award_active,
    patch_tender_award_unsuccessful,
    patch_tender_award_Administrator_change,
    check_tender_award_complaint_period_dates

)
from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest, test_bids, test_lots


class TenderAwardResourceTestMixin(object):
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_get_tender_award = snitch(get_tender_award)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)


class TenderAwardResourceTest(BaseTenderContentWebTest, TenderAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_bids
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amount = test_bids[0]["value"]["amount"]

    def setUp(self):
        super(TenderAwardResourceTest, self).setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))

    test_check_tender_award_complaint_period_dates = snitch(check_tender_award_complaint_period_dates)


class TenderAwardResourceScaleTest(BaseTenderContentWebTest):
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


class TenderLotAwardResourceTestMixin(object):

    test_create_tender_award = snitch(create_tender_lot_award)
    test_patch_tender_award = snitch(patch_tender_lot_award)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class TenderLotAwardResourceTest(BaseTenderContentWebTest, TenderLotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_bids
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amount = test_bids[0]["value"]["amount"]

    def setUp(self):
        super(TenderLotAwardResourceTest, self).setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))


class Tender2LotAwardResourceTestMixin(object):

    test_create_tender_award = snitch(create_tender_2lot_award)
    test_patch_tender_award = snitch(patch_tender_2lot_award)


class Tender2LotAwardResourceTest(BaseTenderContentWebTest, Tender2LotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_lots = 2 * test_lots
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(Tender2LotAwardResourceTest, self).setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.app.authorization = ("Basic", ("broker", ""))


class TenderAwardComplaintResourceTest(
    BaseTenderContentWebTest, TenderAwardComplaintResourceTestMixin, TenderUAAwardComplaintResourceTestMixin
):
    # initial_data = tender_data
    initial_status = "active.tendering"
    initial_bids = test_bids
    initial_lots = 2 * test_lots
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderAwardComplaintResourceTest, self).setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class TenderLotAwardComplaintResourceTestMixin(object):

    test_create_tender_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_lot_award_complaints)


class TenderLotAwardComplaintResourceTest(BaseTenderContentWebTest, TenderLotAwardComplaintResourceTestMixin):
    # initial_data = tender_data
    initial_status = "active.tendering"
    initial_lots = test_lots
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderLotAwardComplaintResourceTest, self).setUp()

        self.prepare_award()

        # Create award
        self.app.authorization = ("Basic", ("token", ""))
        bid = self.initial_bids[0]
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
        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class Tender2LotAwardComplaintResourceTestMixin(object):

    test_create_tender_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lots_award_complaint)


class Tender2LotAwardComplaintResourceTest(
    TenderLotAwardComplaintResourceTest, Tender2LotAwardComplaintResourceTestMixin
):
    initial_lots = 2 * test_lots


class TenderAwardComplaintDocumentResourceTest(BaseTenderContentWebTest, TenderAwardComplaintDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {"suppliers": [test_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints".format(self.tender_id, self.award_id),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
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
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints".format(self.tender_id, self.award_id),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_award_complaint_document = snitch(create_tender_2lot_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_2lot_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_2lot_award_complaint_document)


class TenderAwardDocumentResourceTest(BaseTenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {"suppliers": [test_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        )
        award = response.json["data"]
        self.award_id = award["id"]


class Tender2LotAwardDocumentResourceTest(BaseTenderContentWebTest, Tender2LotAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
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
