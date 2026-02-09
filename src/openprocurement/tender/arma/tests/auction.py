import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.arma.tests.auction_blanks import (
    get_tender_auction,
    post_tender_auction,
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
)
from openprocurement.tender.arma.tests.base import (
    BaseTenderContentWebTest,
    test_tender_arma_bids,
    test_tender_arma_lots,
)
from openprocurement.tender.belowthreshold.tests.auction import (
    TenderAuctionResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier
from openprocurement.tender.esco.tests.auction_blanks import patch_tender_auction


class TenderAuctionResourceTest(BaseTenderContentWebTest, TenderAuctionResourceTestMixin):
    # initial_data = tender_data
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_tender_arma_bids
    initial_lots = test_lots_data = test_tender_arma_lots

    def setUp(self):
        super().setUp()
        # switch to active.pre-qualification
        self.time_shift("active.pre-qualification")
        response = self.check_chronograph()
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
        for qualific in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualific["id"], self.tender_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")
        # # switch to active.pre-qualification.stand-still

    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)
    test_patch_tender_auction = snitch(patch_tender_auction)


class TenderSameValueAuctionResourceTest(BaseTenderContentWebTest):
    initial_status = "active.auction"
    tenderer_info = deepcopy(test_tender_below_supplier)
    initial_bids = test_bids_data = [test_tender_arma_bids[0] for i in range(3)]
    initial_lots = test_tender_arma_lots

    @patch(
        "openprocurement.tender.core.procedure.state.tender_details.EVALUATION_REPORTS_DOC_REQUIRED_FROM",
        get_now() + timedelta(days=1),
    )
    def setUp(self):
        super().setUp()
        auth = self.app.authorization
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
        self.app.authorization = auth

        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        for qualific in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualific["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status("active.auction", {"status": "active.pre-qualification.stand-still"})
        response = self.check_chronograph()
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.auction")
        self.app.authorization = auth

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSameValueAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
