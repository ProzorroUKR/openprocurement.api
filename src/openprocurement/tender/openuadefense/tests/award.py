# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from datetime import timedelta

import mock
from iso8601 import parse_date
from parameterized import parameterized

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now

from openprocurement.tender.belowthreshold.tests.base import test_lots, test_organization, test_draft_complaint
from openprocurement.tender.belowthreshold.tests.award import TenderAwardDocumentResourceTestMixin
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    # TenderAwardResourceTest
    create_tender_award_invalid,
    get_tender_award,
    patch_tender_award_Administrator_change,
    check_tender_award_complaint_period_dates,
    # TenderAwardComplaintResourceTest
    create_tender_award_complaint_invalid,
    get_tender_award_complaint,
    get_tender_award_complaints,
    # TenderLotAwardComplaintResourceTest
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    # TenderAwardComplaintDocumentResourceTest
    not_found as complaint_docs_not_found,
    create_tender_award_complaint_document,
    put_tender_award_complaint_document,
    # Tender2LotAwardComplaintDocumentResourceTest
    create_tender_lots_award_complaint_document,
    # Tender2LotAwardDocumentResourceTest
    create_tender_lots_award_document,
    put_tender_lots_award_document,
    patch_tender_lots_award_document,
    # TenderLotAwardResourceTest
    patch_tender_lot_award_lots_none,
)

from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.openua.tests.award_blanks import (
    # TenderAwardResourceTest
    create_tender_award,
    patch_tender_award,
    patch_tender_award_active,
    patch_tender_award_unsuccessful,
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
    create_tender_award_no_scale_invalid,
    create_tender_award_with_scale_not_required,
    create_tender_award_no_scale,
    bot_patch_tender_award_complaint,
    bot_patch_tender_award_complaint_forbidden,
)
from openprocurement.tender.openuadefense.tests.award_blanks import tender_award_complaint_period

from openprocurement.tender.openuadefense.tests.base import BaseTenderUAContentWebTest, BaseTenderUAWebTest


class TenderAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids

    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_check_tender_award_complaint_period_dates = snitch(check_tender_award_complaint_period_dates)
    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_get_tender_award = snitch(get_tender_award)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)


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


class TenderAwardResourceComplaintPeriodTest(BaseTenderUAWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids

    @parameterized.expand(
        [
            [
                "working_day",
                "2019-09-16T12:00:00+03:00",  # Tender created on working date
                "2019-10-01T00:00:00+03:00",  # NORMALIZED_COMPLAINT_PERIOD_FROM in future
                "2019-10-01T00:00:00+03:00",  # WORKING_DATE_ALLOW_MIDNIGHT_FROM in future
                "2019-09-20T12:00:00+03:00",  # Award period end date
                "2019-09-16T12:04:00+03:00",  # Award period end date sandbox mode
            ],
            [
                "working_day",
                "2019-09-16T12:00:00+03:00",  # Tender created on working date
                "2019-08-01T00:00:00+03:00",  # NORMALIZED_COMPLAINT_PERIOD_FROM in future
                "2019-10-01T00:00:00+03:00",  # WORKING_DATE_ALLOW_MIDNIGHT_FROM in future
                "2019-09-23T00:00:00+03:00",  # Award period end date on last working (but after weekend)
                "2019-09-16T12:04:00+03:00",  # Award period end date sandbox mode
            ],
            [
                "working_day",
                "2019-09-16T12:00:00+03:00",  # Tender created on working date
                "2019-08-01T00:00:00+03:00",  # NORMALIZED_COMPLAINT_PERIOD_FROM in future
                "2019-08-01T00:00:00+03:00",  # WORKING_DATE_ALLOW_MIDNIGHT_FROM in future
                "2019-09-21T00:00:00+03:00",  # Award period end date on last working
                "2019-09-16T12:04:00+03:00",  # Award period end date sandbox mode
            ],
            [
                "non_working_day",
                "2019-09-15T12:00:00+03:00",  # Tender created on weekend
                "2019-10-01T00:00:00+03:00",  # NORMALIZED_COMPLAINT_PERIOD_FROM in future
                "2019-10-01T00:00:00+03:00",  # WORKING_DATE_ALLOW_MIDNIGHT_FROM in future
                "2019-09-20T00:00:00+03:00",  # Award period end date on last working (but after weekend)
                "2019-09-15T12:04:00+03:00",  # Award period end date sandbox mode
            ],
            [
                "non_working_day",
                "2019-09-15T12:00:00+03:00",  # Tender created on weekend
                "2019-08-01T00:00:00+03:00",  # NORMALIZED_COMPLAINT_PERIOD_FROM in future
                "2019-10-01T00:00:00+03:00",  # WORKING_DATE_ALLOW_MIDNIGHT_FROM in future
                "2019-09-20T00:00:00+03:00",  # Award period end date on last working (but after weekend)
                "2019-09-15T12:04:00+03:00",  # Award period end date sandbox mode
            ],
            [
                "non_working_day",
                "2019-09-15T12:00:00+03:00",  # Tender created on weekend
                "2019-08-01T00:00:00+03:00",  # NORMALIZED_COMPLAINT_PERIOD_FROM in future
                "2019-08-01T00:00:00+03:00",  # WORKING_DATE_ALLOW_MIDNIGHT_FROM in future
                "2019-09-20T00:00:00+03:00",  # Award period end date on last working
                "2019-09-15T12:04:00+03:00",  # Award period end date sandbox mode
            ],
        ]
    )
    def test_tender_award_complaint_period(
        self, name, date_str, mock_normalized_date_str, mock_midnight_date_str, expected_date_str, expected_sb_date_str
    ):
        tender_award_complaint_period(
            self,
            parse_date(date_str),
            parse_date(mock_normalized_date_str),
            parse_date(mock_midnight_date_str),
            parse_date(expected_date_str),
            parse_date(expected_sb_date_str),
        )


class TenderLotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_tender_award = snitch(create_tender_lot_award)
    test_patch_tender_award = snitch(patch_tender_lot_award)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class Tender2LotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_tender_award = snitch(create_tender_lots_award)
    test_patch_tender_award = snitch(patch_tender_lots_award)


class TenderAwardComplaintResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintResourceTest, self).setUp()
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
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

    test_create_tender_award_complaint_invalid = snitch(create_tender_award_complaint_invalid)
    test_create_tender_award_claim = snitch(create_tender_award_claim)
    test_create_tender_award_complaint_not_active = snitch(create_tender_award_complaint_not_active)
    test_create_tender_award_complaint = snitch(create_tender_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_award_complaint)
    test_review_tender_award_complaint = snitch(review_tender_award_complaint)
    test_review_tender_award_stopping_complaint = snitch(review_tender_award_stopping_complaint)
    test_review_tender_award_claim = snitch(review_tender_award_claim)
    test_get_tender_award_complaint = snitch(get_tender_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_award_complaints)
    test_bot_patch_tender_award_complaint = snitch(bot_patch_tender_award_complaint)
    test_bot_patch_tender_award_complaint_forbidden = snitch(bot_patch_tender_award_complaint_forbidden)


class TenderLotAwardComplaintResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_lots
    initial_bids = test_bids

    def setUp(self):
        super(TenderLotAwardComplaintResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
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

    test_create_tender_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest):
    initial_lots = 2 * test_lots

    test_create_tender_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderAwardComplaintDocumentResourceTest(BaseTenderUAContentWebTest):
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

    test_not_found = snitch(complaint_docs_not_found)
    test_create_tender_award_complaint_document = snitch(create_tender_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_award_complaint_document)
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

    test_create_tender_award_complaint_document = snitch(create_tender_lots_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_lots_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_lots_award_complaint_document)


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


class Tender2LotAwardDocumentResourceTest(BaseTenderUAContentWebTest):
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

    test_create_tender_award_document = snitch(create_tender_lots_award_document)
    test_put_tender_award_document = snitch(put_tender_lots_award_document)
    test_patch_tender_award_document = snitch(patch_tender_lots_award_document)


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
