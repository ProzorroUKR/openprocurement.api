import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.award_blanks import contract_sign
from openprocurement.tender.cfaselectionua.tests.award_blanks import (  # TenderAwardResourceTest; TenderLotAwardCheckResourceTest; TenderLotAwardResourceTest; Tender2LotAwardResourceTest; TenderAwardDocumentResourceTest; Tender2LotAwardDocumentResourceTest
    check_tender_award,
    create_award_document_bot,
    create_tender_award_document,
    create_tender_award_invalid,
    create_tender_lot_award,
    create_tender_lots_award,
    create_tender_lots_award_document,
    get_tender_award,
    not_found_award_document,
    patch_not_author,
    patch_tender_award_Administrator_change,
    patch_tender_award_document,
    patch_tender_lot_award,
    patch_tender_lot_award_lots_none,
    patch_tender_lot_award_unsuccessful,
    patch_tender_lots_award,
    patch_tender_lots_award_document,
    put_tender_award_document,
    put_tender_lots_award_document,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_tender_cfaselectionua_bids,
    test_tender_cfaselectionua_lots,
    test_tender_cfaselectionua_organization,
)

skip_multi_lots = True


class TenderAwardResourceTestMixin:
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_get_tender_award = snitch(get_tender_award)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)


class TenderAwardDocumentResourceTestMixin:
    test_not_found_award_document = snitch(not_found_award_document)
    test_create_tender_award_document = snitch(create_tender_award_document)
    test_put_tender_award_document = snitch(put_tender_award_document)
    test_patch_tender_award_document = snitch(patch_tender_award_document)
    test_create_award_document_bot = snitch(create_award_document_bot)
    test_patch_not_author = snitch(patch_not_author)


class TenderLotAwardCheckResourceTestMixin:
    test_check_tender_award = snitch(check_tender_award)


class Tender2LotAwardDocumentResourceTestMixin:
    test_create_tender_lots_award_document = snitch(create_tender_lots_award_document)
    test_put_tender_lots_award_document = snitch(put_tender_lots_award_document)
    test_patch_tender_lots_award_document = snitch(patch_tender_lots_award_document)


class TenderLotAwardCheckResourceTest(TenderContentWebTest, TenderLotAwardCheckResourceTestMixin):
    initial_status = "active.auction"
    initial_lots = test_tender_cfaselectionua_lots
    initial_bids = deepcopy(test_tender_cfaselectionua_bids)
    initial_bids.append(deepcopy(test_tender_cfaselectionua_bids[0]))
    initial_bids[1]["tenderers"][0]["name"] = "Не зовсім Державне управління справами"
    # initial_bids[1]['tenderers'][0]['identifier']['id'] = u'88837256'
    initial_bids[2]["tenderers"][0]["name"] = "Точно не Державне управління справами"
    # initial_bids[2]['tenderers'][0]['identifier']['id'] = u'44437256'
    reverse = False
    awarding_key = "amount"

    def setUp(self):
        super().setUp()
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        for lot_id in self.initial_lots:
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]),
                {
                    "data": {
                        "bids": [
                            {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                            for b in auction_bids_data
                        ]
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")


class TenderLotAwardResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_tender_cfaselectionua_lots
    initial_bids = test_tender_cfaselectionua_bids

    test_create_tender_lot_award = snitch(create_tender_lot_award)
    test_patch_tender_lot_award = snitch(patch_tender_lot_award)
    test_patch_tender_lot_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)
    test_contract_sign = snitch(contract_sign)


@unittest.skipIf(skip_multi_lots, "Skip multi-lots tests")
class Tender2LotAwardResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_tender_cfaselectionua_lots
    initial_bids = test_tender_cfaselectionua_bids

    test_create_tender_lots_award = snitch(create_tender_lots_award)
    test_patch_tender_lots_award = snitch(patch_tender_lots_award)


class TenderAwardDocumentResourceTest(TenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = test_tender_cfaselectionua_lots


@unittest.skipIf(skip_multi_lots, "Skip multi-lots tests")
class Tender2LotAwardDocumentResourceTest(TenderContentWebTest, Tender2LotAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_cfaselectionua_bids
    initial_lots = 2 * test_tender_cfaselectionua_lots

    def setUp(self):
        super().setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        bid = self.initial_bids[0]
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_cfaselectionua_organization],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": bid["lotValues"][0]["relatedLot"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = auth


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
