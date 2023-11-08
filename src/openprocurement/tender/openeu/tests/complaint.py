# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_draft_complaint,
)

from openprocurement.tender.belowthreshold.tests.complaint import TenderComplaintResourceTestMixin
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    not_found,
    create_tender_complaint_document,
)
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
    TenderComplaintObjectionMixin,
    TenderQualificationComplaintObjectionMixin,
)
from openprocurement.tender.open.tests.complaint_blanks import objection_related_document_of_evidence

from openprocurement.tender.openua.tests.complaint import TenderUAComplaintResourceTestMixin, CreateAwardComplaintMixin
from openprocurement.tender.openua.tests.complaint_blanks import (
    patch_tender_complaint_document,
    create_tender_lot_complaint,
)

from openprocurement.tender.openeu.tests.complaint_blanks import (
    put_tender_complaint_document,
)
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_tender_openeu_lots,
    test_tender_openeu_bids,
)


class TenderComplaintResourceTest(
    BaseTenderContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_below_author


class TenderLotAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_lots = test_tender_openeu_lots
    test_author = test_tender_below_author
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class TenderComplaintDocumentResourceTest(BaseTenderContentWebTest):
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
    BaseTenderContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))


class TenderQualificationComplaintObjectionResourceTest(
    BaseTenderContentWebTest,
    TenderQualificationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_tender_openeu_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_below_author

    test_objection_related_document_of_evidence = snitch(objection_related_document_of_evidence)

    def setUp(self):
        super(TenderQualificationComplaintObjectionResourceTest, self).setUp()
        self.create_qualification()


class TenderAwardComplaintObjectionResourceTest(
    BaseTenderContentWebTest,
    CreateAwardComplaintMixin,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.qualification"
    initial_bids = test_tender_openeu_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderAwardComplaintObjectionResourceTest, self).setUp()
        self.create_award()


class TenderCancellationComplaintObjectionResourceTest(
    BaseTenderContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderCancellationComplaintObjectionResourceTest, self).setUp()
        self.set_complaint_period_end()
        self.create_cancellation()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderQualificationComplaintObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationComplaintObjectionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
