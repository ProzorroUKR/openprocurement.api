# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_draft_complaint,
)

from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    not_found,
    create_tender_complaint_document,
)
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
    TenderQualificationComplaintObjectionMixin,
    TenderComplaintObjectionMixin,
)

from openprocurement.tender.openua.tests.complaint import CreateAwardComplaintMixin, TenderUAComplaintResourceTestMixin
from openprocurement.tender.openua.tests.complaint_blanks import (
    patch_tender_complaint_document,
)

from openprocurement.tender.openeu.tests.complaint_blanks import (
    put_tender_complaint_document,
)

from openprocurement.tender.esco.tests.base import BaseESCOContentWebTest, test_tender_esco_lots, test_tender_esco_bids


class TenderComplaintResourceTest(
    BaseESCOContentWebTest, TenderUAComplaintResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_below_author


class TenderComplaintDocumentResourceTest(BaseESCOContentWebTest):

    test_author = test_tender_below_author
    initial_auth = ("Basic", ("broker", ""))

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

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


class TenderComplaintObjectionResourceTest(
    BaseESCOContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True


class TenderQualificationComplaintPostResourceTest(
    BaseESCOContentWebTest,
    TenderQualificationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_tender_esco_bids
    initial_lots = test_tender_esco_lots
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_below_author

    def setUp(self):
        super(TenderQualificationComplaintPostResourceTest, self).setUp()
        self.create_qualification()


class TenderAwardComplaintObjectionResourceTest(
    BaseESCOContentWebTest,
    CreateAwardComplaintMixin,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.qualification"
    initial_bids = test_tender_esco_bids
    initial_lots = test_tender_esco_lots

    def setUp(self):
        super(TenderAwardComplaintObjectionResourceTest, self).setUp()
        self.create_award()


class TenderCancellationComplaintObjectionResourceTest(
    BaseESCOContentWebTest,
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
    suite.addTest(unittest.makeSuite(TenderQualificationComplaintPostResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationComplaintObjectionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
