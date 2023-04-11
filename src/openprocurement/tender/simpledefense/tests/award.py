# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from datetime import timedelta

import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_lots,
    test_tender_below_organization,
    test_tender_below_draft_complaint,
)
from openprocurement.tender.belowthreshold.tests.award import TenderAwardDocumentResourceTestMixin
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_award_invalid,
    get_tender_award,
    create_tender_award_complaint_invalid,
    not_found as complaint_docs_not_found,
    create_tender_award_complaint_document,
    put_tender_award_complaint_document,
    create_tender_lots_award_complaint_document,
    create_tender_lots_award_document,
    put_tender_lots_award_document,
    patch_tender_lots_award_document,
    patch_tender_lot_award_lots_none,
    create_tender_award_document_json_bulk,
)

from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.openua.tests.award_blanks import (
    create_tender_award,
    patch_tender_award,
    create_tender_lot_award,
    patch_tender_lot_award,
    create_tender_lots_award,
    patch_tender_lots_award,
    create_tender_award_complaint_not_active,
    create_tender_award_complaint,
    patch_tender_award_complaint,
    review_tender_award_complaint,
    review_tender_award_stopping_complaint,
    create_tender_lot_award_complaint,
    patch_tender_lot_award_complaint,
    create_tender_lots_award_complaint,
    patch_tender_award_complaint_document,
    put_tender_lots_award_complaint_document,
    patch_tender_lots_award_complaint_document,
    create_tender_award_no_scale_invalid,
    create_tender_award_with_scale_not_required,
    create_tender_award_no_scale,
    bot_patch_tender_award_complaint,
    bot_patch_tender_award_complaint_forbidden,
)
from openprocurement.tender.simpledefense.tests.base import (
    test_tender_simpledefense_bids,
    BaseSimpleDefContentWebTest,
)

from openprocurement.tender.openuadefense.tests.award_blanks import (
    check_tender_award_complaint_period_dates_before_new,
    check_tender_award_complaint_period_dates_after_new,
    check_tender_award_complaint_period_dates_new,
    patch_tender_award_active_before_new,
    patch_tender_award_active_after_new,
    patch_tender_award_active_new,
    patch_tender_award_unsuccessful_before_new,
    patch_tender_award_unsuccessful_after_new,
    patch_tender_award_unsuccessful_new,
    patch_tender_lot_award_unsuccessful_before_new,
    patch_tender_lot_award_unsuccessful_after_new,
    patch_tender_lot_award_unsuccessful_new,
    create_tender_award_claim,
    create_tender_award_claim_denied,
    review_tender_award_claim,
    get_tender_award_complaint,
    get_tender_award_complaints,
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    patch_tender_lots_award_complaint,
)


class TenderAwardResourceTest(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_simpledefense_bids

    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_check_tender_award_complaint_period_dates_before_new = snitch(check_tender_award_complaint_period_dates_before_new)
    test_check_tender_award_complaint_period_dates_after_new = snitch(check_tender_award_complaint_period_dates_after_new)
    test_check_tender_award_complaint_period_dates_new = snitch(check_tender_award_complaint_period_dates_new)
    test_patch_tender_award_active_before_new = snitch(patch_tender_award_active_before_new)
    test_patch_tender_award_active_after_new = snitch(patch_tender_award_active_after_new)
    test_patch_tender_award_active_new = snitch(patch_tender_award_active_new)
    test_patch_tender_award_unsuccessful_before_new = snitch(patch_tender_award_unsuccessful_before_new)
    test_patch_tender_award_unsuccessful_after_new = snitch(patch_tender_award_unsuccessful_after_new)
    test_patch_tender_award_unsuccessful_new = snitch(patch_tender_award_unsuccessful_new)
    test_get_tender_award = snitch(get_tender_award)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)


class TenderAwardResourceScaleTest(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"

    def setUp(self):
        patcher = mock.patch("openprocurement.api.models.ORGANIZATION_SCALE_FROM", get_now() + timedelta(days=1))
        patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch("openprocurement.tender.core.procedure.models.organization.ORGANIZATION_SCALE_FROM",
                             get_now() + timedelta(days=1))
        patcher.start()
        self.addCleanup(patcher.stop)

        test_bid = deepcopy(test_tender_simpledefense_bids[0])
        test_bid["tenderers"][0].pop("scale")
        self.initial_bids = [test_bid]
        super(TenderAwardResourceScaleTest, self).setUp()

        self.app.authorization = ("Basic", ("token", ""))

    test_create_tender_award_with_scale_not_required = snitch(create_tender_award_with_scale_not_required)
    test_create_tender_award_with_no_scale = snitch(create_tender_award_no_scale)


class TenderLotAwardResourceTest(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_simpledefense_bids

    test_create_tender_award = snitch(create_tender_lot_award)
    test_patch_tender_award = snitch(patch_tender_lot_award)
    test_patch_tender_award_unsuccessful_before_new = snitch(patch_tender_lot_award_unsuccessful_before_new)
    test_patch_tender_award_unsuccessful_after_new = snitch(patch_tender_lot_award_unsuccessful_after_new)
    test_patch_tender_award_unsuccessful_new = snitch(patch_tender_lot_award_unsuccessful_new)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class Tender2LotAwardResourceTest(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_tender_below_lots
    initial_bids = test_tender_simpledefense_bids

    test_create_tender_award = snitch(create_tender_lots_award)
    test_patch_tender_award = snitch(patch_tender_lots_award)


class TenderAwardPendingResourceTestCase(BaseSimpleDefContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_simpledefense_bids
    docservice = True

    def setUp(self):
        super(TenderAwardPendingResourceTestCase, self).setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {"data": {
                    "suppliers": [test_tender_below_organization],
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
    test_create_tender_award_claim_denied = snitch(create_tender_award_claim_denied)
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
    initial_lots = test_tender_below_lots

    test_create_tender_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest):
    initial_lots = 2 * test_tender_below_lots

    test_create_tender_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderAwardComplaintDocumentResourceTest(TenderAwardActiveResourceTestCase):

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()

        # Create complaint for award
        bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_not_found = snitch(complaint_docs_not_found)
    test_create_tender_award_complaint_document = snitch(create_tender_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(TenderAwardActiveResourceTestCase):
    initial_lots = 2 * test_tender_below_lots

    def setUp(self):
        super(Tender2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": test_tender_below_draft_complaint},
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
    initial_lots = 2 * test_tender_below_lots

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
