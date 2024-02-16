import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_draft_complaint,
)
from openprocurement.tender.belowthreshold.tests.complaint import (
    TenderComplaintResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    create_tender_complaint_document,
    not_found,
)
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_cfaua_bids,
    test_tender_cfaua_lots,
)
from openprocurement.tender.cfaua.tests.complaint_blanks import (
    create_tender_complaint,
    create_tender_lot_complaint,
)
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
    TenderComplaintObjectionMixin,
)
from openprocurement.tender.openeu.tests.complaint_blanks import (
    put_tender_complaint_document,
)
from openprocurement.tender.openua.tests.complaint import (
    TenderUAComplaintResourceTestMixin,
)
from openprocurement.tender.openua.tests.complaint_blanks import (
    patch_tender_complaint_document,
)


class TenderComplaintResourceTest(BaseTenderContentWebTest, TenderUAComplaintResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_below_author

    test_create_tender_complaint = snitch(create_tender_complaint)


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


class TenderComplaintObjectionTest(
    BaseTenderContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_below_author


class TenderCancellationComplaintObjectionTest(
    BaseTenderContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True

    def setUp(self):
        super().setUp()
        self.set_complaint_period_end()
        self.create_cancellation()


class TenderAwardComplaintObjectionTest(
    BaseTenderContentWebTest,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.qualification.stand-still"
    initial_lots = test_tender_cfaua_lots
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        response = self.app.get(f"/tenders/{self.tender_id}/awards")
        self.awards_ids = [award["id"] for award in response.json["data"]]
        self.award_id = self.awards_ids[0]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintObjectionTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationComplaintObjectionTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintObjectionTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
