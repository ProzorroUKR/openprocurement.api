import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_draft_complaint,
)
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    create_tender_complaint_document,
    not_found,
)
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
    TenderComplaintObjectionMixin,
    TenderQualificationComplaintObjectionMixin,
)
from openprocurement.tender.open.tests.complaint_blanks import (
    objection_related_document_of_evidence,
)
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_tender_openeu_bids,
    test_tender_openeu_lots,
)
from openprocurement.tender.openeu.tests.complaint_blanks import (
    put_tender_complaint_document,
)
from openprocurement.tender.openua.tests.complaint import (
    CreateAwardComplaintMixin,
    TenderUAComplaintResourceTestMixin,
)
from openprocurement.tender.openua.tests.complaint_blanks import (
    patch_tender_complaint_document,
)


class TenderComplaintResourceTest(BaseTenderContentWebTest, TenderUAComplaintResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_below_author


class TenderComplaintDocumentResourceTest(BaseTenderContentWebTest):
    test_author = test_tender_below_author
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
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
    initial_auth = ("Basic", ("broker", ""))


class TenderQualificationComplaintObjectionResourceTest(
    BaseTenderContentWebTest,
    TenderQualificationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_tender_openeu_bids
    initial_lots = test_tender_openeu_lots
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_below_author

    test_objection_related_document_of_evidence = snitch(objection_related_document_of_evidence)

    def setUp(self):
        super().setUp()
        self.create_qualification()


class TenderAwardComplaintObjectionResourceTest(
    BaseTenderContentWebTest,
    CreateAwardComplaintMixin,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_openeu_bids
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_openeu_lots

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderCancellationComplaintObjectionResourceTest(
    BaseTenderContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        self.set_complaint_period_end()
        self.create_cancellation()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintObjectionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderQualificationComplaintObjectionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintObjectionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationComplaintObjectionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
