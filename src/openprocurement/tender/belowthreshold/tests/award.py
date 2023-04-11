import unittest
import mock

from copy import deepcopy
from datetime import timedelta

from openprocurement.api.tests.base import snitch, change_auth
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.adapters import TenderBelowThersholdConfigurator
from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_bids,
    test_tender_below_lots,
    test_tender_below_organization,
    test_tender_below_draft_claim,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_award_invalid,
    create_tender_award_no_scale_invalid,
    create_tender_award,
    patch_tender_award,
    check_tender_award_complaint_period_dates,
    patch_tender_award_unsuccessful,
    get_tender_award,
    check_tender_award,
    create_tender_lot_award,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    patch_tender_lot_award_lots_none,
    create_tender_lots_award,
    patch_tender_lots_award,
    create_tender_award_complaint_invalid,
    create_tender_award_complaint,
    patch_tender_award_complaint,
    review_tender_award_complaint,
    get_tender_award_complaint,
    get_tender_award_complaints,
    create_tender_lot_award_complaint,
    patch_tender_lot_award_complaint,
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    create_tender_lots_award_complaint,
    patch_tender_lots_award_complaint,
    not_found,
    create_tender_award_complaint_document,
    put_tender_award_complaint_document,
    patch_tender_award_complaint_document,
    create_tender_lots_award_complaint_document,
    put_tender_lots_award_complaint_document,
    patch_tender_lots_award_complaint_document,
    not_found_award_document,
    create_tender_award_document,
    create_tender_award_document_json_bulk,
    put_tender_award_document,
    patch_tender_award_document,
    create_award_document_bot,
    patch_not_author,
    create_tender_lots_award_document,
    put_tender_lots_award_document,
    patch_tender_lots_award_document,
    create_tender_award_with_scale_not_required,
    create_tender_award_no_scale,
)


class TenderAwardResourceTestMixin(object):
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)
    test_get_tender_award = snitch(get_tender_award)
    test_check_tender_award_complaint_period_dates = snitch(check_tender_award_complaint_period_dates)


class TenderAwardComplaintResourceTestMixin(object):
    test_create_tender_award_complaint_invalid = snitch(create_tender_award_complaint_invalid)
    test_get_tender_award_complaint = snitch(get_tender_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_award_complaints)


class TenderAwardDocumentResourceTestMixin(object):
    test_not_found_award_document = snitch(not_found_award_document)
    test_create_tender_award_document = snitch(create_tender_award_document)
    test_create_tender_award_document_json_bulk = snitch(create_tender_award_document_json_bulk)
    test_put_tender_award_document = snitch(put_tender_award_document)
    test_patch_tender_award_document = snitch(patch_tender_award_document)
    test_create_award_document_bot = snitch(create_award_document_bot)
    test_patch_not_author = snitch(patch_not_author)


class TenderAwardComplaintDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_tender_award_complaint_document = snitch(create_tender_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_award_complaint_document)


class TenderLotAwardCheckResourceTestMixin(object):
    test_check_tender_award = snitch(check_tender_award)


class Tender2LotAwardDocumentResourceTestMixin(object):
    test_create_tender_lots_award_document = snitch(create_tender_lots_award_document)
    test_put_tender_lots_award_document = snitch(put_tender_lots_award_document)
    test_patch_tender_lots_award_document = snitch(patch_tender_lots_award_document)


class TenderAwardResourceTest(TenderContentWebTest, TenderAwardResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_below_bids
    docservice = True

    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)


class TenderAwardResourceScaleTest(TenderContentWebTest):
    initial_status = "active.qualification"
    docservice = True

    def setUp(self):
        patcher = mock.patch("openprocurement.tender.core.procedure.models.organization.ORGANIZATION_SCALE_FROM",
                             get_now() + timedelta(days=1))
        patcher.start()
        self.addCleanup(patcher.stop)
        test_bid = deepcopy(test_tender_below_bids[0])
        test_bid["tenderers"][0].pop("scale")
        self.initial_bids = [test_bid]
        super(TenderAwardResourceScaleTest, self).setUp()
        self.app.authorization = ("Basic", ("token", ""))

    test_create_tender_award_with_scale_not_required = snitch(create_tender_award_with_scale_not_required)
    test_create_tender_award_with_no_scale = snitch(create_tender_award_no_scale)


class TenderLotAwardCheckResourceTest(TenderContentWebTest, TenderLotAwardCheckResourceTestMixin):
    initial_status = "active.auction"
    initial_lots = test_tender_below_lots
    initial_bids = deepcopy(test_tender_below_bids)
    initial_bids.append(deepcopy(test_tender_below_bids[0]))
    initial_bids[1]["tenderers"][0]["name"] = "Не зовсім Державне управління справами"
    initial_bids[1]["tenderers"][0]["identifier"]["id"] = "88837256"
    initial_bids[2]["tenderers"][0]["name"] = "Точно не Державне управління справами"
    initial_bids[2]["tenderers"][0]["identifier"]["id"] = "44437256"
    reverse = TenderBelowThersholdConfigurator.reverse_awarding_criteria
    awarding_key = TenderBelowThersholdConfigurator.awarding_criteria_key
    docservice = True

    def setUp(self):
        super(TenderLotAwardCheckResourceTest, self).setUp()
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = [
            {
                # "id": b["id"],
                "lotValues": b["lotValues"],
            }
            for b in response.json["data"]["bids"]
        ]
        for lot_id in self.initial_lots:
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")


class TenderLotAwardResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_below_bids
    docservice = True

    test_create_tender_lot_award = snitch(create_tender_lot_award)
    test_patch_tender_lot_award = snitch(patch_tender_lot_award)
    test_patch_tender_lot_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class Tender2LotAwardResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_tender_below_lots
    initial_bids = test_tender_below_bids
    docservice = True

    test_create_tender_lots_award = snitch(create_tender_lots_award)
    test_patch_tender_lots_award = snitch(patch_tender_lots_award)


class TenderAwardPendingResourceTestCase(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_below_bids
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
                {"data": {"status": "active"}},
            )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class TenderAwardComplaintResourceTest(TenderAwardActiveResourceTestCase, TenderAwardComplaintResourceTestMixin):
    test_create_tender_award_complaint = snitch(create_tender_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_award_complaint)
    test_review_tender_award_complaint = snitch(review_tender_award_complaint)


class TenderLotAwardComplaintResourceTest(TenderAwardActiveResourceTestCase):
    initial_lots = test_tender_below_lots

    test_create_tender_lot_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_lot_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_lot_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_lot_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest):
    initial_lots = 2 * test_tender_below_lots

    test_create_tender_lots_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_lots_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderAwardComplaintDocumentResourceTest(
    TenderAwardActiveResourceTestCase,
    TenderAwardComplaintDocumentResourceTestMixin,
):

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()
        # Create complaint for award
        self.bid_token = list(self.initial_bids_tokens.values())[0]
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": test_tender_below_draft_claim},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(TenderAwardActiveResourceTestCase):
    initial_lots = 2 * test_tender_below_lots

    def setUp(self):
        super(Tender2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create complaint for award
        bid_token = list(self.initial_bids_tokens.values())[0]
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
            {"data": test_tender_below_draft_claim},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_lots_award_complaint_document = snitch(create_tender_lots_award_complaint_document)
    test_put_tender_lots_award_complaint_document = snitch(put_tender_lots_award_complaint_document)
    test_patch_tender_lots_award_complaint_document = snitch(patch_tender_lots_award_complaint_document)


class TenderAwardDocumentResourceTest(TenderAwardPendingResourceTestCase, TenderAwardDocumentResourceTestMixin):
    pass


class Tender2LotAwardDocumentResourceTest(TenderAwardPendingResourceTestCase, Tender2LotAwardDocumentResourceTestMixin):
    initial_lots = 2 * test_tender_below_lots


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
