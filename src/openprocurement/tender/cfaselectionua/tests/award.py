# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    patch_tender_lot_award_lots_none,
    create_tender_award_with_the_invalid_document_type,
)
from openprocurement.tender.cfaselectionua.adapters.configurator import TenderCfaSelectionUAConfigurator
from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_bids,
    test_lots,
    test_organization,
)
from openprocurement.tender.cfaselectionua.tests.award_blanks import (
    # TenderAwardResourceTest
    create_tender_award_invalid,
    create_tender_award,
    patch_tender_award,
    patch_tender_award_unsuccessful,
    get_tender_award,
    patch_tender_award_Administrator_change,
    # TenderLotAwardCheckResourceTest
    check_tender_award,
    # TenderLotAwardResourceTest
    create_tender_lot_award,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    # Tender2LotAwardResourceTest
    create_tender_lots_award,
    patch_tender_lots_award,
    # TenderAwardDocumentResourceTest
    not_found_award_document,
    create_tender_award_document,
    put_tender_award_document,
    patch_tender_award_document,
    create_award_document_bot,
    patch_not_author,
    # Tender2LotAwardDocumentResourceTest
    create_tender_lots_award_document,
    put_tender_lots_award_document,
    patch_tender_lots_award_document,
)

skip_multi_lots = True


class TenderAwardResourceTestMixin(object):
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_get_tender_award = snitch(get_tender_award)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)


class TenderAwardDocumentResourceTestMixin(object):
    test_not_found_award_document = snitch(not_found_award_document)
    test_create_tender_award_document = snitch(create_tender_award_document)
    test_create_tender_award_with_the_invalid_document_type = snitch(create_tender_award_with_the_invalid_document_type)
    test_put_tender_award_document = snitch(put_tender_award_document)
    test_patch_tender_award_document = snitch(patch_tender_award_document)
    test_create_award_document_bot = snitch(create_award_document_bot)
    test_patch_not_author = snitch(patch_not_author)


class TenderLotAwardCheckResourceTestMixin(object):
    test_check_tender_award = snitch(check_tender_award)


class Tender2LotAwardDocumentResourceTestMixin(object):
    test_create_tender_lots_award_document = snitch(create_tender_lots_award_document)
    test_put_tender_lots_award_document = snitch(put_tender_lots_award_document)
    test_patch_tender_lots_award_document = snitch(patch_tender_lots_award_document)


class TenderLotAwardCheckResourceTest(TenderContentWebTest, TenderLotAwardCheckResourceTestMixin):
    initial_status = "active.auction"
    initial_lots = test_lots
    initial_bids = deepcopy(test_bids)
    initial_bids.append(deepcopy(test_bids[0]))
    initial_bids[1]["tenderers"][0]["name"] = u"Не зовсім Державне управління справами"
    # initial_bids[1]['tenderers'][0]['identifier']['id'] = u'88837256'
    initial_bids[2]["tenderers"][0]["name"] = u"Точно не Державне управління справами"
    # initial_bids[2]['tenderers'][0]['identifier']['id'] = u'44437256'
    reverse = TenderCfaSelectionUAConfigurator.reverse_awarding_criteria
    awarding_key = TenderCfaSelectionUAConfigurator.awarding_criteria_key

    def setUp(self):
        super(TenderLotAwardCheckResourceTest, self).setUp()
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
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
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_tender_lot_award = snitch(create_tender_lot_award)
    test_patch_tender_lot_award = snitch(patch_tender_lot_award)
    test_patch_tender_lot_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


@unittest.skipIf(skip_multi_lots, "Skip multi-lots tests")
class Tender2LotAwardResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_tender_lots_award = snitch(create_tender_lots_award)
    test_patch_tender_lots_award = snitch(patch_tender_lots_award)


class TenderAwardDocumentResourceTest(TenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = test_lots


class TenderAwardDocumentWithDSResourceTest(TenderAwardDocumentResourceTest):
    docservice = True


@unittest.skipIf(skip_multi_lots, "Skip multi-lots tests")
class Tender2LotAwardDocumentResourceTest(TenderContentWebTest, Tender2LotAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
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
        self.app.authorization = auth


@unittest.skipIf(skip_multi_lots, "Skip multi-lots tests")
class Tender2LotAwardDocumentWithDSResourceTest(Tender2LotAwardDocumentResourceTest):
    docservice = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tender2LotAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
