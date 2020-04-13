# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots, test_draft_claim, test_author
from openprocurement.tender.belowthreshold.tests.complaint import TenderComplaintResourceTestMixin
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    # TenderComplaintDocumentResourceTest
    not_found,
    create_tender_complaint_document,
)

from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest
from openprocurement.tender.openua.tests.complaint_blanks import (
    # TenderComplaintResourceTest
    create_tender_complaint,
    patch_tender_complaint,
    review_tender_complaint,
    review_tender_stopping_complaint,
    mistaken_status_tender_complaint,
    bot_patch_tender_complaint,
    bot_patch_tender_complaint_mistaken,
    bot_patch_tender_complaint_forbidden,
    # TenderComplaintDocumentResourceTest
    patch_tender_complaint_document,
    put_tender_complaint_document,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_complaint,
)


class TenderUAComplaintResourceTestMixin(object):
    test_create_tender_complaint = snitch(create_tender_complaint)
    test_patch_tender_complaint = snitch(patch_tender_complaint)
    test_review_tender_complaint = snitch(review_tender_complaint)
    test_review_tender_stopping_complaint = snitch(review_tender_stopping_complaint)
    test_mistaken_status_tender_complaint = snitch(mistaken_status_tender_complaint)
    test_bot_patch_tender_complaint = snitch(bot_patch_tender_complaint)
    test_bot_patch_tender_complaint_mistaken = snitch(bot_patch_tender_complaint_mistaken)
    test_bot_patch_tender_complaint_forbidden = snitch(bot_patch_tender_complaint_forbidden)


class TenderComplaintResourceTest(
    BaseTenderUAContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin
):
    test_author = test_author


class TenderLotAwardComplaintResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots
    test_author = test_author

    test_create_tender_lot_complaint = snitch(create_tender_lot_complaint)


class TenderComplaintDocumentResourceTest(BaseTenderUAContentWebTest):
    def setUp(self):
        super(TenderComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {"data": test_draft_claim},
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
    suite.addTest(unittest.makeSuite(TenderComplaintResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
