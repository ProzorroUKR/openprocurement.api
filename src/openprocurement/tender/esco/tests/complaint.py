# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_author

from openprocurement.tender.belowthreshold.tests.complaint import TenderComplaintResourceTestMixin
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    # TenderComplaintDocumentResourceTest
    not_found,
    create_tender_complaint_document,
)

from openprocurement.tender.openua.tests.complaint import TenderUAComplaintResourceTestMixin
from openprocurement.tender.openua.tests.complaint_blanks import (
    # TenderComplaintDocumentResourceTest
    patch_tender_complaint_document,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_complaint,
)

from openprocurement.tender.openeu.tests.complaint_blanks import (
    # TenderComplaintDocumentResourceTest
    put_tender_complaint_document,
)

from openprocurement.tender.esco.tests.base import BaseESCOContentWebTest, test_lots, test_bids


class TenderComplaintResourceTest(
    BaseESCOContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_author


class TenderLotAwardComplaintResourceTest(BaseESCOContentWebTest):
    initial_lots = test_lots
    test_author = test_author
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class TenderComplaintDocumentResourceTest(BaseESCOContentWebTest):

    test_author = test_author
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {"data": {"title": "complaint title", "description": "complaint description", "author": self.test_author}},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
