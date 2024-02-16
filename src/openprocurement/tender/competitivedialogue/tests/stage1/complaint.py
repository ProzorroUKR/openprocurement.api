import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
)
from openprocurement.tender.belowthreshold.tests.complaint import (
    TenderComplaintResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (  # TenderStage2EU(UA)ComplaintDocumentResourceTest
    create_tender_complaint_document,
    not_found,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUContentWebTest,
    BaseCompetitiveDialogUAContentWebTest,
    test_tender_cd_author,
    test_tender_cd_lots,
)
from openprocurement.tender.openeu.tests.base import test_tender_openeu_bids
from openprocurement.tender.openua.tests.complaint import (
    TenderUAComplaintResourceTestMixin,
)
from openprocurement.tender.openua.tests.complaint_blanks import (  # TenderStage2EU(UA)LotAwardComplaintResourceTest; TenderStage2EU(UA)ComplaintDocumentResourceTest
    create_tender_lot_complaint,
    patch_tender_complaint_document,
    put_tender_complaint_document,
)


class CompetitiveDialogEUComplaintResourceTest(
    BaseCompetitiveDialogEUContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_cd_author  # TODO: change attribute identifier


class CompetitiveDialogEULotAwardComplaintResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_cd_author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class CompetitiveDialogEUComplaintDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest):
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


class CompetitiveDialogUAComplaintResourceTest(
    BaseCompetitiveDialogUAContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_cd_author  # TODO: change attribute identifier


class CompetitiveDialogUALotAwardComplaintResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_cd_author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class CompetitiveDialogUAComplaintDocumentResourceTest(BaseCompetitiveDialogUAContentWebTest):
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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogEUComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogEULotAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogUAComplaintResourceTest))
    suite.addTest(unittest.makesuite(CompetitiveDialogUALotAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogEUComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogUAComplaintDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
