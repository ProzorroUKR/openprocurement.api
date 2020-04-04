# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_draft_claim
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    test_bids,
    test_lots,
    test_author,
    test_tenderer,
)
from openprocurement.tender.openeu.tests.qualification_blanks import (
    # TenderStage2EUQualificationResourceTest
    post_tender_qualifications,
    get_tender_qualifications_collection,
    patch_tender_qualifications,
    get_tender_qualifications,
    patch_tender_qualifications_after_status_change,
    # TenderStage2EU2LotQualificationResourceTest
    lot_patch_tender_qualifications,
    lot_get_tender_qualifications_collection,
    tender_qualification_cancelled,
    lot_patch_tender_qualifications_lots_none,
    # TenderStage2EUQualificationDocumentResourceTest
    not_found,
    create_qualification_document,
    put_qualification_document,
    patch_qualification_document,
    create_qualification_document_after_status_change,
    put_qualification_document_after_status_change,
    tender_owner_create_qualification_document,
    # TenderStage2EUQualificationComplaintResourceTest
    create_tender_qualification_complaint_invalid,
    create_tender_qualification_complaint,
    patch_tender_qualification_complaint,
    review_tender_qualification_complaint,
    review_tender_qualification_stopping_complaint,
    get_tender_qualification_complaint,
    get_tender_qualification_complaints,
    # TenderStage2EULotQualificationComplaintResourceTest
    create_tender_lot_qualification_complaint,
    patch_tender_lot_qualification_complaint,
    get_tender_lot_qualification_complaint,
    get_tender_lot_qualification_complaints,
    # TenderStage2EU2LotQualificationComplaintResourceTest
    create_tender_2lot_qualification_complaint,
    # TenderStage2EUQualificationComplaintDocumentResourceTest
    complaint_not_found,
    create_tender_qualification_complaint_document,
    put_tender_qualification_complaint_document,
    patch_tender_qualification_complaint_document,
    # TenderStage2EU2LotQualificationComplaintDocumentResourceTest
    create_tender_2lot_qualification_complaint_document,
    put_tender_2lot_qualification_complaint_document,
    bot_patch_tender_qualification_complaint,
    bot_patch_tender_qualification_complaint_forbidden,
)

test_tender_bids = deepcopy(test_bids[:2])
for test_bid in test_tender_bids:
    test_bid["tenderers"] = [test_tenderer]


class TenderStage2EUQualificationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"  # 'active.pre-qualification' status sets in setUp
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderStage2EUQualificationResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})

        # simulate chronograph tick
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    test_post_tender_qualifications = snitch(post_tender_qualifications)
    test_get_tender_qualifications_collection = snitch(get_tender_qualifications_collection)
    test_patch_tender_qualifications = snitch(patch_tender_qualifications)
    test_get_tender_qualifications = snitch(get_tender_qualifications)
    test_patch_tender_qualifications_after_status_change = snitch(patch_tender_qualifications_after_status_change)


class TenderStage2EU2LotQualificationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_lots = deepcopy(2 * test_lots)
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderStage2EU2LotQualificationResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})

        # simulate chronograph tick
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]

    test_patch_tender_qualifications = snitch(lot_patch_tender_qualifications)
    test_get_tender_qualifications_collection = snitch(lot_get_tender_qualifications_collection)
    test_tender_qualification_cancelled = snitch(tender_qualification_cancelled)
    test_lot_patch_tender_qualifications_lots_none = snitch(lot_patch_tender_qualifications_lots_none)


class TenderStage2EUQualificationDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderStage2EUQualificationDocumentResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.time_shift("active.pre-qualification")
        self.check_chronograph()
        # list qualifications
        response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
        self.assertEqual(response.status, "200 OK")
        self.qualifications = response.json["data"]
        self.assertEqual(len(self.qualifications), 2)

    test_not_found = snitch(not_found)
    test_create_qualification_document = snitch(create_qualification_document)
    test_put_qualification_document = snitch(put_qualification_document)
    test_patch_qualification_document = snitch(patch_qualification_document)
    test_create_qualification_document_after_status_change = snitch(create_qualification_document_after_status_change)
    test_put_qualification_document_after_status_change = snitch(put_qualification_document_after_status_change)
    test_tender_owner_create_qualification_document = snitch(tender_owner_create_qualification_document)


class TenderStage2EUQualificationComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_author

    def setUp(self):
        super(TenderStage2EUQualificationComplaintResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})

        # simulate chronograph tick
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.qualification_id = qualifications[0]["id"]

        for qualification in qualifications:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "active")

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")

    test_create_tender_qualification_complaint_invalid = snitch(create_tender_qualification_complaint_invalid)
    test_create_tender_qualification_complaint = snitch(create_tender_qualification_complaint)
    test_patch_tender_qualification_complaint = snitch(patch_tender_qualification_complaint)
    test_review_tender_qualification_complaint = snitch(review_tender_qualification_complaint)
    test_review_tender_qualification_stopping_complaint = snitch(review_tender_qualification_stopping_complaint)
    test_get_tender_qualification_complaint = snitch(get_tender_qualification_complaint)
    test_get_tender_qualification_complaints = snitch(get_tender_qualification_complaints)
    test_bot_patch_tender_qualification_complaint = snitch(bot_patch_tender_qualification_complaint)
    test_bot_patch_tender_qualification_complaint_forbidden = snitch(bot_patch_tender_qualification_complaint_forbidden)


class TenderStage2EULotQualificationComplaintResourceTest(TenderStage2EUQualificationComplaintResourceTest):

    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_qualification_complaint = snitch(create_tender_lot_qualification_complaint)
    test_patch_tender_qualification_complaint = snitch(patch_tender_lot_qualification_complaint)
    test_get_tender_qualification_complaint = snitch(get_tender_lot_qualification_complaint)
    test_get_tender_qualification_complaints = snitch(get_tender_lot_qualification_complaints)


class TenderStage2EU2LotQualificationComplaintResourceTest(TenderStage2EULotQualificationComplaintResourceTest):
    initial_lots = deepcopy(2 * test_lots)
    initial_auth = ("Basic", ("broker", ""))
    test_create_tender_qualification_complaint = snitch(create_tender_2lot_qualification_complaint)


class TenderStage2EUQualificationComplaintDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_tender_bids
    author_data = test_author
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderStage2EUQualificationComplaintDocumentResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})

        # simulate chronograph tick
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.qualification_id = qualifications[0]["id"]

        for qualification in qualifications:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "active")

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")

        # Create complaint for qualification
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
                self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
            ),
            {"data": test_draft_claim},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_not_found = snitch(complaint_not_found)
    test_create_tender_qualification_complaint_document = snitch(create_tender_qualification_complaint_document)
    test_put_tender_qualification_complaint_document = snitch(put_tender_qualification_complaint_document)
    test_patch_tender_qualification_complaint_document = snitch(patch_tender_qualification_complaint_document)


class TenderStage2EU2LotQualificationComplaintDocumentResourceTest(
    TenderStage2EUQualificationComplaintDocumentResourceTest
):
    initial_lots = 2 * test_lots
    initial_auth = ("Basic", ("broker", ""))
    test_create_tender_qualification_complaint_document = snitch(create_tender_2lot_qualification_complaint_document)
    test_put_tender_qualification_complaint_document = snitch(put_tender_2lot_qualification_complaint_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUQualificationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUQualificationComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotQualificationComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotQualificationComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUQualificationComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotQualificationComplaintDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
