import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    test_tender_cd_author,
    test_tender_cd_lots,
    test_tender_cd_tenderer,
    test_tender_openeu_bids,
)
from openprocurement.tender.openeu.tests.qualification import (
    TenderQualificationRequirementResponseEvidenceTestMixin,
    TenderQualificationRequirementResponseTestMixin,
)
from openprocurement.tender.openeu.tests.qualification_blanks import (  # TenderStage2EUQualificationResourceTest; TenderStage2EU2LotQualificationResourceTest; TenderStage2EUQualificationDocumentResourceTest; TenderStage2EUQualificationComplaintResourceTest; TenderStage2EULotQualificationComplaintResourceTest; TenderStage2EU2LotQualificationComplaintResourceTest; TenderStage2EUQualificationComplaintDocumentResourceTest; TenderStage2EU2LotQualificationComplaintDocumentResourceTest; TenderStage2EUQualificationDocumentWithDSResourceTest
    bot_patch_tender_qualification_complaint,
    bot_patch_tender_qualification_complaint_forbidden,
    check_sign_doc_qualifications_before_stand_still,
    complaint_not_found,
    create_qualification_document,
    create_qualification_document_after_status_change,
    create_tender_2lot_qualification_complaint,
    create_tender_2lot_qualification_complaint_document,
    create_tender_lot_qualification_complaint,
    create_tender_qualification_complaint,
    create_tender_qualification_complaint_document,
    create_tender_qualification_complaint_invalid,
    create_tender_qualifications_document_json_bulk,
    get_tender_lot_qualification_complaint,
    get_tender_lot_qualification_complaints,
    get_tender_qualification_complaint,
    get_tender_qualification_complaints,
    get_tender_qualifications,
    get_tender_qualifications_collection,
    lot_get_tender_qualifications_collection,
    lot_patch_tender_qualifications,
    lot_patch_tender_qualifications_lots_none,
    not_found,
    patch_qualification_document,
    patch_tender_lot_qualification_complaint,
    patch_tender_qualification_complaint,
    patch_tender_qualification_complaint_document,
    patch_tender_qualifications,
    patch_tender_qualifications_after_status_change,
    post_tender_qualifications,
    put_qualification_document,
    put_qualification_document_after_status_change,
    put_tender_2lot_qualification_complaint_document,
    put_tender_qualification_complaint_document,
    review_tender_qualification_complaint,
    review_tender_qualification_stopping_complaint,
    tender_owner_create_qualification_document,
    tender_qualification_cancelled,
)

test_tender_bids = deepcopy(test_tender_openeu_bids[:2])
for test_bid in test_tender_bids:
    test_bid["tenderers"] = [test_tender_cd_tenderer]


class TenderQualificationBaseTestCase(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = "active.tendering"  # 'active.pre-qualification' status sets in setUp
    initial_bids = test_tender_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_cd_author
    initial_lots = test_tender_cd_lots
    docservice = True

    def setUp(self):
        super().setUp()
        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.qualification_id = qualifications[0]["id"]


class TenderStage2EUQualificationResourceTest(TenderQualificationBaseTestCase):
    test_post_tender_qualifications = snitch(post_tender_qualifications)
    test_get_tender_qualifications_collection = snitch(get_tender_qualifications_collection)
    test_patch_tender_qualifications = snitch(patch_tender_qualifications)
    test_get_tender_qualifications = snitch(get_tender_qualifications)
    test_patch_tender_qualifications_after_status_change = snitch(patch_tender_qualifications_after_status_change)


class TenderStage2EU2LotQualificationResourceTest(TenderQualificationBaseTestCase):
    initial_lots = deepcopy(2 * test_tender_cd_lots)

    test_patch_tender_qualifications = snitch(lot_patch_tender_qualifications)
    test_get_tender_qualifications_collection = snitch(lot_get_tender_qualifications_collection)
    test_tender_qualification_cancelled = snitch(tender_qualification_cancelled)
    test_lot_patch_tender_qualifications_lots_none = snitch(lot_patch_tender_qualifications_lots_none)
    test_check_sign_doc_qualifications_before_stand_still = snitch(check_sign_doc_qualifications_before_stand_still)


class TenderStage2EUQualificationDocumentResourceTest(TenderQualificationBaseTestCase):
    docservice = True

    def setUp(self):
        super().setUp()
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


class TenderStage2EUQualificationDocumentWithDSResourceTest(TenderStage2EUQualificationDocumentResourceTest):
    docservice = True

    test_create_tender_qualifications_document_json_bulk = snitch(create_tender_qualifications_document_json_bulk)


class TenderStage2EUQualificationComplaintResourceTest(TenderQualificationBaseTestCase):
    def setUp(self):
        super().setUp()

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

        self.add_qualification_sign_doc(self.tender_id, self.tender_token)
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
    initial_lots = test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_qualification_complaint = snitch(create_tender_lot_qualification_complaint)
    test_patch_tender_qualification_complaint = snitch(patch_tender_lot_qualification_complaint)
    test_get_tender_qualification_complaint = snitch(get_tender_lot_qualification_complaint)
    test_get_tender_qualification_complaints = snitch(get_tender_lot_qualification_complaints)


class TenderStage2EU2LotQualificationComplaintResourceTest(TenderStage2EULotQualificationComplaintResourceTest):
    initial_lots = deepcopy(2 * test_tender_cd_lots)
    initial_auth = ("Basic", ("broker", ""))
    test_create_tender_qualification_complaint = snitch(create_tender_2lot_qualification_complaint)


class TenderStage2EUQualificationComplaintDocumentResourceTest(TenderQualificationBaseTestCase):
    def setUp(self):
        super().setUp()

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

        self.add_qualification_sign_doc(self.tender_id, self.tender_token)
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")

        # Create complaint for qualification
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
                self.tender_id, self.qualification_id, list(self.initial_bids_tokens.values())[0]
            ),
            {"data": test_tender_below_draft_complaint},
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
    initial_lots = 2 * test_tender_cd_lots
    initial_auth = ("Basic", ("broker", ""))
    test_create_tender_qualification_complaint_document = snitch(create_tender_2lot_qualification_complaint_document)
    test_put_tender_qualification_complaint_document = snitch(put_tender_2lot_qualification_complaint_document)


class TenderStage2EUQualificationRequirementResponseResourceTest(
    TenderQualificationRequirementResponseTestMixin,
    TenderQualificationBaseTestCase,
):
    pass


class TenderStageEUQualificationRequirementResponseEvidenceResourceTest(
    TenderQualificationRequirementResponseEvidenceTestMixin,
    TenderQualificationBaseTestCase,
):
    docservice = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUQualificationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EU2LotQualificationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUQualificationDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUQualificationComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EULotQualificationComplaintResourceTest))
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EU2LotQualificationComplaintResourceTest)
    )
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EUQualificationComplaintDocumentResourceTest)
    )
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2EU2LotQualificationComplaintDocumentResourceTest)
    )
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
