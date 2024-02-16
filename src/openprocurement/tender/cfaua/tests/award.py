import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.award_blanks import (  # TenderLotAwardComplaintResourceTest; TenderAwardDocumentResourceTest; TenderAwardDocumentWithDSResourceTest
    create_award_document_bot,
    create_tender_award_complaint_document,
    create_tender_award_complaint_invalid,
    create_tender_award_document,
    create_tender_award_document_json_bulk,
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    not_found,
    not_found_award_document,
    patch_not_author,
    patch_tender_award_document,
    put_tender_award_complaint_document,
    put_tender_award_document,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
)
from openprocurement.tender.cfaua.constants import MIN_BIDS_NUMBER
from openprocurement.tender.cfaua.tests.award_blanks import (
    award_complaint_document_in_active_qualification,
    bot_patch_tender_award_complaint,
    bot_patch_tender_award_complaint_forbidden,
    create_tender_award_claim,
    create_tender_award_complaint,
    create_tender_award_complaint_not_active,
    create_tender_lot_award_complaint,
    get_tender_award_complaint,
    get_tender_award_complaints,
    patch_tender_award,
    patch_tender_award_active,
    patch_tender_award_complaint_document,
    patch_tender_award_in_qualification_st_st,
    patch_tender_award_unsuccessful,
    patch_tender_lot_award_lots_none,
    review_tender_award_claim,
    review_tender_award_complaint,
)
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_cfaua_bids,
    test_tender_cfaua_lots,
)
from openprocurement.tender.openeu.tests.award_blanks import (  # TenderAwardResourceTest
    create_tender_award_invalid,
    get_tender_award,
)
from openprocurement.tender.openua.tests.award_blanks import (
    patch_tender_award_complaint,
    patch_tender_lot_award_complaint,
    review_tender_award_stopping_complaint,
)


class TenderAwardResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amount = test_tender_cfaua_bids[0]["value"]["amount"]
    docservice = True

    def setUp(self):
        super().setUp()
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
    test_patch_tender_award_in_qualification_st_st = snitch(patch_tender_award_in_qualification_st_st)


class TenderAwardBidsOverMaxAwardsResourceTest(TenderAwardResourceTest):
    """Testing awards with bids over max awards"""

    initial_bids = test_tender_cfaua_bids + deepcopy(test_tender_cfaua_bids)  # double testbids
    min_bids_number = MIN_BIDS_NUMBER * 2


class TenderLotAwardResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaua_bids
    initial_lots = test_tender_cfaua_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amount = test_tender_cfaua_bids[0]["value"]["amount"]
    docservice = True

    def setUp(self):
        super().setUp()
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
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class TenderAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))
    docservice = True

    def setUp(self):
        super().setUp()
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
    initial_lots = test_tender_cfaua_lots
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))
    docservice = True

    def setUp(self):
        super().setUp()
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
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))
    docservice = True

    def setUp(self):
        super().setUp()
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
    initial_bids = test_tender_cfaua_bids
    initial_lots = test_tender_cfaua_lots
    docservice = True

    def setUp(self):
        super().setUp()
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.award_bid_id = response.json["data"][0]["bid_id"]

        self.set_status("active.qualification.stand-still")
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(
                self.tender_id, self.award_id, self.initial_bids_tokens[self.award_bid_id]
            ),
            {"data": test_tender_below_draft_complaint},
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
    initial_bids = test_tender_cfaua_bids
    initial_lots = test_tender_cfaua_lots
    docservice = True

    def setUp(self):
        super().setUp()
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]

    test_not_found_award_document = snitch(not_found_award_document)
    test_create_tender_award_document = snitch(create_tender_award_document)
    test_put_tender_award_document = snitch(put_tender_award_document)
    test_patch_tender_award_document = snitch(patch_tender_award_document)
    test_create_award_document_bot = snitch(create_award_document_bot)
    test_patch_not_author = snitch(patch_not_author)


class TenderAwardDocumentWithDSResourceTest(TenderAwardDocumentResourceTest):
    docservice = True
    test_create_tender_award_document_json_bulk = snitch(create_tender_award_document_json_bulk)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardBidsOverMaxAwardsResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintExtendedResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
