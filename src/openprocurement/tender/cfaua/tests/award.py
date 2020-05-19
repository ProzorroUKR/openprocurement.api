# -*- coding: utf-8 -*-
import unittest

from copy import deepcopy
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_draft_complaint
from openprocurement.tender.cfaua.constants import MIN_BIDS_NUMBER

from openprocurement.tender.belowthreshold.tests.award_blanks import (
    # TenderLotAwardComplaintResourceTest
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    create_tender_award_complaint_invalid,
    not_found,
    create_tender_award_complaint_document,
    put_tender_award_complaint_document,
    # TenderAwardDocumentResourceTest
    not_found_award_document,
    create_tender_award_document,
    put_tender_award_document,
    patch_tender_award_document,
    create_award_document_bot,
    patch_not_author,
    # TenderLotAwardResourceTest
    patch_tender_lot_award_lots_none,
    create_tender_award_contract_data_document,
)

from openprocurement.tender.openua.tests.award_blanks import (
    patch_tender_award_complaint,
    patch_tender_lot_award_complaint,
    review_tender_award_stopping_complaint,
)

from openprocurement.tender.openeu.tests.award_blanks import (
    # TenderAwardResourceTest
    create_tender_award_invalid,
    get_tender_award,
    patch_tender_award_Administrator_change,
)
from openprocurement.tender.cfaua.tests.base import BaseTenderContentWebTest, test_bids, test_lots
from openprocurement.tender.cfaua.tests.award_blanks import (
    # TenderAwardComplaintResourceTest
    create_tender_award_claim,
    create_tender_award_complaint,
    create_tender_award_complaint_not_active,
    get_tender_award_complaint,
    get_tender_award_complaints,
    patch_tender_award,
    patch_tender_award_active,
    review_tender_award_complaint,
    review_tender_award_claim,
    patch_tender_award_unsuccessful,
    bot_patch_tender_award_complaint,
    bot_patch_tender_award_complaint_forbidden,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_award_complaint,

    # TenderAwardComplaintDocumentResourceTest
    patch_tender_award_complaint_document,
    patch_tender_award_in_qualification_st_st,
    award_complaint_document_in_active_qualification,
)

no_lot_logic = True


class TenderAwardResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amount = test_bids[0]["value"]["amount"]

    def setUp(self):
        super(TenderAwardResourceTest, self).setUp()
        # Get awards
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.awards_ids = [award["id"] for award in response.json["data"]]
        self.award_id = self.awards_ids[0]  # for compability with belowthreshonl and openeu tests
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))

    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_get_tender_award = snitch(get_tender_award)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)
    test_patch_tender_award_in_qualification_st_st = snitch(patch_tender_award_in_qualification_st_st)


class TenderAwardBidsOverMaxAwardsResourceTest(TenderAwardResourceTest):
    """Testing awards with bids over max awards"""

    initial_bids = test_bids + deepcopy(test_bids)  # double testbids
    min_bids_number = MIN_BIDS_NUMBER * 2


class TenderLotAwardResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amount = test_bids[0]["value"]["amount"]

    def setUp(self):
        super(TenderLotAwardResourceTest, self).setUp()
        # Get awards
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.awards_ids = [award["id"] for award in response.json["data"]]
        self.award_id = self.awards_ids[0]  # for compability with belowthreshonl and openeu tests
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))

    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_get_tender_award = snitch(get_tender_award)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class TenderAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderAwardComplaintResourceTest, self).setUp()
        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]

    test_create_tender_award_claim = snitch(create_tender_award_claim)
    test_get_tender_award_complaints = snitch(get_tender_award_complaints)
    test_review_tender_award_claim = snitch(review_tender_award_claim)
    test_review_tender_award_complaint = snitch(review_tender_award_complaint)
    test_create_tender_award_complaint = snitch(create_tender_award_complaint)
    test_create_tender_award_complaint_not_active = snitch(create_tender_award_complaint_not_active)
    test_get_tender_award_complaint = snitch(get_tender_award_complaint)
    test_bot_patch_tender_award_complaint = snitch(bot_patch_tender_award_complaint)
    test_bot_patch_tender_award_complaint_forbidden = snitch(bot_patch_tender_award_complaint_forbidden)

    # TenderAwardComplaintResourceTestMixin
    test_create_tender_award_complaint_invalid = snitch(create_tender_award_complaint_invalid)


class TenderLotAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification.stand-still"
    initial_lots = test_lots
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderLotAwardComplaintResourceTest, self).setUp()
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.awards_ids = [award["id"] for award in response.json["data"]]
        self.award_id = self.awards_ids[0]


    test_create_tender_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_lot_award_complaints)


class TenderAwardComplaintExtendedResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderAwardComplaintExtendedResourceTest, self).setUp()
        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.set_status("active.qualification.stand-still")

    test_patch_tender_award_complaint = snitch(patch_tender_award_complaint)
    test_review_tender_award_stopping_complaint = snitch(review_tender_award_stopping_complaint)


class TenderAwardComplaintDocumentResourceTest(BaseTenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = test_lots

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.award_bid_id = response.json["data"][0]["bid_id"]

        self.set_status("active.qualification.stand-still")
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(
                self.tender_id, self.award_id, self.initial_bids_tokens[self.award_bid_id]
            ),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)
    test_not_found = snitch(not_found)
    test_create_tender_award_complaint_document = snitch(create_tender_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_award_complaint_document)
    test_award_complaint_document_in_active_qualification = snitch(award_complaint_document_in_active_qualification)


class TenderAwardDocumentResourceTest(BaseTenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = test_lots

    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]

    test_not_found_award_document = snitch(not_found_award_document)
    test_create_tender_award_document = snitch(create_tender_award_document)
    test_put_tender_award_document = snitch(put_tender_award_document)
    test_patch_tender_award_document = snitch(patch_tender_award_document)
    test_create_award_document_bot = snitch(create_award_document_bot)
    test_patch_not_author = snitch(patch_not_author)
    test_create_tender_award_contract_data_document = snitch(create_tender_award_contract_data_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardBidsOverMaxAwardsResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintExtendedResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
