# -*- coding: utf-8 -*-
import unittest
import mock

from copy import deepcopy
from datetime import timedelta

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.adapters import\
    PQTenderConfigurator as TenderBelowThersholdConfigurator
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_bids,
    test_organization,
    test_author,
    test_draft_claim,
    test_claim,
)
from openprocurement.tender.pricequotation.tests.award_blanks import (
    # TenderAwardResourceTest
    create_tender_award_invalid,
    create_tender_award_no_scale_invalid,
    create_tender_award,
    patch_tender_award,
    patch_tender_award_unsuccessful,
    get_tender_award,
    patch_tender_award_Administrator_change,
    # TenderLotAwardCheckResourceTest
    check_tender_award,
    # TenderAwardDocumentResourceTest
    not_found_award_document,
    create_tender_award_document,
    put_tender_award_document,
    patch_tender_award_document,
    create_award_document_bot,
    patch_not_author,
    # TenderAwardResourceScaleTest
    create_tender_award_with_scale_not_required,
    create_tender_award_no_scale,
)


class TenderAwardResourceTestMixin(object):
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_get_tender_award = snitch(get_tender_award)


class TenderAwardComplaintResourceTestMixin(object):
    """"""


class TenderAwardDocumentResourceTestMixin(object):
    test_not_found_award_document = snitch(not_found_award_document)
    test_create_tender_award_document = snitch(create_tender_award_document)
    test_put_tender_award_document = snitch(put_tender_award_document)
    test_patch_tender_award_document = snitch(patch_tender_award_document)
    test_create_award_document_bot = snitch(create_award_document_bot)
    test_patch_not_author = snitch(patch_not_author)


class TenderAwardComplaintDocumentResourceTestMixin(object):
    """"""

class TenderLotAwardCheckResourceTestMixin(object):
    test_check_tender_award = snitch(check_tender_award)


class Tender2LotAwardDocumentResourceTestMixin(object):
    """"""


class TenderAwardResourceTest(TenderContentWebTest, TenderAwardResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids

    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)


class TenderAwardResourceScaleTest(TenderContentWebTest):
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


class TenderLotAwardCheckResourceTest(TenderContentWebTest, TenderLotAwardCheckResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_bids)
    initial_bids.append(deepcopy(test_bids[0]))
    initial_bids[1]["tenderers"][0]["name"] = u"Не зовсім Державне управління справами"
    initial_bids[1]["tenderers"][0]["identifier"]["id"] = u"88837256"
    initial_bids[2]["tenderers"][0]["name"] = u"Точно не Державне управління справами"
    initial_bids[2]["tenderers"][0]["identifier"]["id"] = u"44437256"
    reverse = TenderBelowThersholdConfigurator.reverse_awarding_criteria
    awarding_key = TenderBelowThersholdConfigurator.awarding_criteria_key

    def setUp(self):
        super(TenderLotAwardCheckResourceTest, self).setUp()
        # TODO: swithc to active.qualification
        # self.app.authorization = ("Basic", ("auction", ""))
        # response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        # auction_bids_data = response.json["data"]["bids"]
        # for lot_id in self.initial_lots:
        #     response = self.app.post_json(
        #         "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
        #     )
        #     self.assertEqual(response.status, "200 OK")
        #     self.assertEqual(response.content_type, "application/json")
        # response = self.app.get("/tenders/{}".format(self.tender_id))
        # self.assertEqual(response.json["data"]["status"], "active.qualification")


class TenderLotAwardResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids


class Tender2LotAwardResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids


class TenderAwardComplaintResourceTest(TenderContentWebTest, TenderAwardComplaintResourceTestMixin):
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
        self.app.authorization = auth




class TenderAwardComplaintDocumentResourceTest(TenderContentWebTest, TenderAwardComplaintDocumentResourceTestMixin):
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
        self.app.authorization = auth

        # Create complaint for award
        self.bid_token = self.initial_bids_tokens.values()[0]
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": test_draft_claim},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]



class TenderAwardDocumentResourceTest(TenderContentWebTest, TenderAwardDocumentResourceTestMixin):
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


class TenderAwardDocumentWithDSResourceTest(TenderAwardDocumentResourceTest):
    docservice = True



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tender2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
