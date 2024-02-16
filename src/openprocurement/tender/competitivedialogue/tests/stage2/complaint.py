import unittest
from copy import deepcopy

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
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cd_author,
    test_tender_cd_lots,
    test_tender_cd_shortlisted_firms,
    test_tender_openeu_bids,
)
from openprocurement.tender.competitivedialogue.tests.stage2.award import (
    test_tender_bids,
)
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
    TenderComplaintObjectionMixin,
    TenderQualificationComplaintObjectionMixin,
)
from openprocurement.tender.openua.tests.complaint import (
    CreateAwardComplaintMixin,
    TenderUAComplaintResourceTestMixin,
)
from openprocurement.tender.openua.tests.complaint_blanks import (  # TenderStage2EU(UA)LotAwardComplaintResourceTest; TenderStage2EU(UA)ComplaintDocumentResourceTest
    create_tender_lot_complaint,
    patch_tender_complaint_document,
    put_tender_complaint_document,
)


class TenderStage2EUComplaintResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderUAComplaintResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_cd_author
    initial_lots = test_tender_cd_lots


class TenderStage2EUComplaintDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        # Create complaint
        claim_data = deepcopy(test_tender_below_draft_complaint)
        claim_data["author"] = test_tender_cd_author
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {"data": claim_data},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


class TenderStage2UAComplaintResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest, TenderUAComplaintResourceTestMixin
):
    test_author = test_tender_cd_author  # TODO: change attribute identifier
    initial_lots = test_tender_cd_lots


class TenderStage2UAComplaintDocumentResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest, TenderStage2EUComplaintDocumentResourceTest
):
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        # Create complaint
        claim_data = deepcopy(test_tender_below_draft_complaint)
        claim_data["author"] = test_tender_cd_author
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {"data": claim_data},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]


class TenderCompetitiveDialogEUObjectionResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_lots = test_tender_cd_lots


class TenderCompetitiveDialogUAObjectionResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_lots = test_tender_cd_lots


class TenderCompetitiveDialogEUStage2AwardComplaintObjectionResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest,
    CreateAwardComplaintMixin,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.tendering"  # 'active.qualification' status sets in setUp
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})

        # simulate chronograph tick
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        response = self.app.get(f"/tenders/{self.tender_id}/qualifications")
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.qualification_id = qualifications[0]["id"]

        for qualification in qualifications:
            response = self.app.patch_json(
                f"/tenders/{self.tender_id}/qualifications/{qualification['id']}?acc_token={self.tender_token}",
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "active")

        self.set_status("active.qualification")

        self.create_award()


class TenderCompetitiveDialogUAStage2AwardComplaintObjectionResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest,
    CreateAwardComplaintMixin,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.qualification"
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        self.create_award()


class TenderCompetitiveDialogEUQualificationComplaintObjectionResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest,
    TenderQualificationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_cd_author
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        self.create_qualification()


class TenderCancellationComplaintObjectionResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_lots = test_tender_cd_lots

    def setUp(self):
        super().setUp()
        self.set_complaint_period_end()
        self.create_cancellation()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UAComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UAComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCompetitiveDialogEUObjectionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCompetitiveDialogUAObjectionResourceTest))
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TenderCompetitiveDialogUAStage2AwardComplaintObjectionResourceTest
        )
    )
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TenderCompetitiveDialogUAStage2AwardComplaintObjectionResourceTest
        )
    )
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TenderCompetitiveDialogEUQualificationComplaintObjectionResourceTest
        )
    )
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCancellationComplaintObjectionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
