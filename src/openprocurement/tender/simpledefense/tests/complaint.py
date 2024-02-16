import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_draft_complaint,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.complaint import (
    TenderComplaintResourceTestMixin,
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
)
from openprocurement.tender.openua.tests.complaint import (
    CreateAwardComplaintMixin,
    TenderUAComplaintResourceTestMixin,
)
from openprocurement.tender.openua.tests.complaint_blanks import (
    create_tender_lot_complaint,
    mistaken_status_tender_complaint,
    patch_tender_complaint_document,
    put_tender_complaint_document,
)
from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest,
    test_tender_simpledefense_bids,
)


class TenderComplaintResourceTest(
    BaseSimpleDefContentWebTest,
    TenderComplaintResourceTestMixin,
    TenderUAComplaintResourceTestMixin,
):
    test_author = test_tender_below_author
    test_mistaken_status_tender_complaint = snitch(mistaken_status_tender_complaint)


class TenderLotAwardComplaintResourceTest(BaseSimpleDefContentWebTest):
    initial_lots = test_tender_below_lots
    test_author = test_tender_below_author

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class TenderComplaintDocumentResourceTest(BaseSimpleDefContentWebTest):
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

    test_author = test_tender_below_author

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


class TenderComplaintObjectionResourceTest(
    BaseSimpleDefContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True


class TenderAwardComplaintObjectionResourceTest(
    BaseSimpleDefContentWebTest,
    CreateAwardComplaintMixin,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.qualification"
    initial_bids = test_tender_simpledefense_bids
    initial_lots = test_tender_below_lots

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderCancellationComplaintObjectionResourceTest(
    BaseSimpleDefContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True

    def setUp(self):
        super().setUp()
        self.set_complaint_period_end()
        self.create_cancellation()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintObjectionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintObjectionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationComplaintObjectionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
