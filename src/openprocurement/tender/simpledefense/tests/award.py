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
    # TenderAwardDocumentWithDSResourceTest
    create_tender_award_document_json_bulk,
)

from openprocurement.tender.core.tests.base import change_auth
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

from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest,
    BaseSimpleDefWebTest,
    test_bids,
)


class TenderAwardResourceTest(BaseSimpleDefContentWebTest):
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


class TenderAwardResourceScaleTest(BaseSimpleDefContentWebTest):
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


class TenderLotAwardResourceTest(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_tender_award = snitch(create_tender_lot_award)
    test_patch_tender_award = snitch(patch_tender_lot_award)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class Tender2LotAwardResourceTest(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_tender_award = snitch(create_tender_lots_award)
    test_patch_tender_award = snitch(patch_tender_lots_award)


class TenderAwardPendingResourceTestCase(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardPendingResourceTestCase, self).setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {"data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "lotID": self.initial_bids[0]["lotValues"][0]["relatedLot"] if self.initial_lots else None,
                }},
            )
        award = response.json["data"]
        self.award_id = award["id"]


class TenderAwardActiveResourceTestCase(TenderAwardPendingResourceTestCase):
    def setUp(self):
        super(TenderAwardActiveResourceTestCase, self).setUp()
        with change_auth(self.app, ("Basic", ("token", ""))):
            self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class TenderAwardComplaintResourceTest(TenderAwardActiveResourceTestCase):

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


class TenderLotAwardComplaintResourceTest(TenderAwardActiveResourceTestCase):
    initial_lots = test_lots

    test_create_tender_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest):
    initial_lots = 2 * test_lots

    test_create_tender_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderAwardComplaintDocumentResourceTest(TenderAwardActiveResourceTestCase):

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()

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


class Tender2LotAwardComplaintDocumentResourceTest(TenderAwardActiveResourceTestCase):
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_award_complaint_document = snitch(create_tender_lots_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_lots_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_lots_award_complaint_document)


class TenderAwardDocumentResourceTest(TenderAwardPendingResourceTestCase, TenderAwardDocumentResourceTestMixin):
    pass


class Tender2LotAwardDocumentResourceTest(TenderAwardPendingResourceTestCase):
    initial_lots = 2 * test_lots

    test_create_tender_award_document = snitch(create_tender_lots_award_document)
    test_put_tender_award_document = snitch(put_tender_lots_award_document)
    test_patch_tender_award_document = snitch(patch_tender_lots_award_document)


class TenderAwardDocumentWithDSResourceTest(TenderAwardDocumentResourceTest):
    docservice = True

    test_create_tender_award_document_json_bulk = snitch(create_tender_award_document_json_bulk)


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
