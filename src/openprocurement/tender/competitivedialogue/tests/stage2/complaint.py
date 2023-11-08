# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_draft_complaint
from openprocurement.tender.belowthreshold.tests.complaint import TenderComplaintResourceTestMixin
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
    TenderQualificationComplaintObjectionMixin,
    TenderComplaintObjectionMixin,
)
from openprocurement.tender.openua.tests.complaint import CreateAwardComplaintMixin, TenderUAComplaintResourceTestMixin
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    # TenderStage2EU(UA)ComplaintDocumentResourceTest
    not_found,
    create_tender_complaint_document,
)
from openprocurement.tender.openua.tests.complaint_blanks import (
    # TenderStage2EU(UA)LotAwardComplaintResourceTest
    create_tender_lot_complaint,
    # TenderStage2EU(UA)ComplaintDocumentResourceTest
    put_tender_complaint_document,
    patch_tender_complaint_document,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_cd_lots,
    test_tender_openeu_bids,
    test_tender_cd_shortlisted_firms,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cd_author,
)
from openprocurement.tender.competitivedialogue.tests.stage2.award import test_tender_bids


class TenderStage2EUComplaintResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin
):

    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_cd_author


class TenderStage2EULotAwardComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_cd_author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class TenderStage2EUComplaintDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderStage2EUComplaintDocumentResourceTest, self).setUp()
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
    BaseCompetitiveDialogUAStage2ContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin
):
    test_author = test_tender_cd_author  # TODO: change attribute identifier


class TenderStage2UALotAwardComplaintResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest, TenderStage2EULotAwardComplaintResourceTest
):
    initial_lots = test_tender_cd_lots
    test_author = test_tender_cd_author  # TODO: change attribute identifier


class TenderStage2UAComplaintDocumentResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest, TenderStage2EUComplaintDocumentResourceTest
):
    def setUp(self):
        super(TenderStage2UAComplaintDocumentResourceTest, self).setUp()
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


class TenderCompetitiveDialogUAObjectionResourceTest(
    BaseCompetitiveDialogUAStage2ContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True


class TenderCompetitiveDialogEUStage2AwardComplaintObjectionResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest,
    CreateAwardComplaintMixin,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.tendering"  # 'active.qualification' status sets in setUp
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderCompetitiveDialogEUStage2AwardComplaintObjectionResourceTest, self).setUp()
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

    def setUp(self):
        super(TenderCompetitiveDialogUAStage2AwardComplaintObjectionResourceTest, self).setUp()
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

    def setUp(self):
        super(TenderCompetitiveDialogEUQualificationComplaintObjectionResourceTest, self).setUp()
        self.create_qualification()


class TenderCancellationComplaintObjectionResourceTest(
    BaseCompetitiveDialogEUStage2ContentWebTest,
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
    suite.addTest(unittest.makeSuite(TenderStage2EUComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCompetitiveDialogEUObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderCompetitiveDialogUAObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderCompetitiveDialogUAStage2AwardComplaintObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderCompetitiveDialogUAStage2AwardComplaintObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderCompetitiveDialogEUQualificationComplaintObjectionResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationComplaintObjectionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
