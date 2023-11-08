# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_lots,
    test_tender_below_draft_complaint,
    test_tender_below_author,
)
from openprocurement.tender.belowthreshold.tests.complaint import TenderComplaintResourceTestMixin
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    not_found,
    create_tender_complaint_document,
)
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
    TenderComplaintObjectionMixin,
)

from openprocurement.tender.openua.tests.complaint import TenderUAComplaintResourceTestMixin, CreateAwardComplaintMixin
from openprocurement.tender.openua.tests.complaint_blanks import (
    create_tender_lot_complaint,
    put_tender_complaint_document,
    patch_tender_complaint_document,
    mistaken_status_tender_complaint,
)

from openprocurement.tender.openuadefense.tests.base import BaseTenderUAContentWebTest, test_tender_openuadefense_bids


class TenderComplaintResourceTest(
    BaseTenderUAContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin
):
    test_author = test_tender_below_author
    test_mistaken_status_tender_complaint = snitch(mistaken_status_tender_complaint)


class TenderLotAwardComplaintResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots
    test_author = test_tender_below_author

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class TenderComplaintDocumentResourceTest(BaseTenderUAContentWebTest):
    def setUp(self):
        super(TenderComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_author = test_tender_below_author

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


class TenderComplaintObjectionResourceTest(
    BaseTenderUAContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True


class TenderAwardComplaintObjectionResourceTest(
    BaseTenderUAContentWebTest,
    CreateAwardComplaintMixin,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.qualification"
    initial_bids = test_tender_openuadefense_bids

    def setUp(self):
        super(TenderAwardComplaintObjectionResourceTest, self).setUp()
        self.create_award()


class TenderCancellationComplaintObjectionResourceTest(
    BaseTenderUAContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True

    def setUp(self):
        super(TenderCancellationComplaintObjectionResourceTest, self).setUp()
        self.set_complaint_period_end()
        self.create_cancellation()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationComplaintObjectionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
