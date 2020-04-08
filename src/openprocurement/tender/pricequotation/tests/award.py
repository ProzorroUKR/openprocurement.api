# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.adapters import\
    PQTenderConfigurator as TenderBelowThersholdConfigurator
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_bids,
    test_organization,
)
from openprocurement.tender.pricequotation.tests.award_blanks import (
    # TenderAwardResourceTest
    create_tender_award_invalid,
    create_tender_award_no_scale_invalid,
    create_tender_award,
    patch_tender_award,
    # patch_tender_award_unsuccessful,
    get_tender_award,
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
    # test_patch_unsuccessful = snitch(patch_tender_award_unsuccessful)


class TenderAwardDocumentResourceTestMixin(object):
    test_not_found_award_document = snitch(not_found_award_document)
    test_create_tender_award_document = snitch(create_tender_award_document)
    test_put_tender_award_document = snitch(put_tender_award_document)
    test_patch_tender_award_document = snitch(patch_tender_award_document)
    test_create_award_document_bot = snitch(create_award_document_bot)
    test_patch_not_author = snitch(patch_not_author)


class TenderAwardResourceTest(TenderContentWebTest, TenderAwardResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids

    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_check_tender_award = snitch(check_tender_award)


class TenderAwardResourceScaleTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids

    test_create_tender_award_no_scale = snitch(create_tender_award_no_scale)
    test_create_tender_award_no_scale_invalid = snitch(
        create_tender_award_no_scale_invalid
    )
    test_create_tender_award_with_scale_not_required = snitch(
        create_tender_award_with_scale_not_required
    )


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
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceScaleTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
