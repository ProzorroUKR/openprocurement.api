# -*- coding: utf-8 -*-
import unittest
from mock import patch
from datetime import timedelta

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_author, test_draft_claim, test_criteria

from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest, test_bids, test_lots
from openprocurement.tender.openeu.tests.qualification_blanks import (
    # Tender2LotQualificationComplaintDocumentResourceTest
    create_tender_2lot_qualification_complaint_document,
    put_tender_2lot_qualification_complaint_document,
    # TenderQualificationComplaintDocumentResourceTest
    complaint_not_found,
    create_tender_qualification_complaint_document,
    put_tender_qualification_complaint_document,
    patch_tender_qualification_complaint_document,
    # Tender2LotQualificationClaimResourceTest
    create_tender_qualification_claim,
    # Tender2LotQualificationComplaintResourceTest
    create_tender_2lot_qualification_complaint,
    # TenderLotQualificationComplaintResourceTest
    create_tender_lot_qualification_complaint,
    patch_tender_lot_qualification_complaint,
    get_tender_lot_qualification_complaint,
    get_tender_lot_qualification_complaints,
    # TenderQualificationComplaintResourceTest
    create_tender_qualification_complaint_invalid,
    create_tender_qualification_complaint,
    patch_tender_qualification_complaint,
    review_tender_qualification_complaint,
    review_tender_qualification_stopping_complaint,
    review_tender_award_claim,
    get_tender_qualification_complaint,
    get_tender_qualification_complaints,
    change_status_to_standstill_with_complaint,
    # TenderQualificationDocumentResourceTest
    not_found,
    tender_owner_create_qualification_document,
    create_qualification_document,
    put_qualification_document,
    patch_qualification_document,
    create_qualification_document_after_status_change,
    put_qualification_document_after_status_change,
    # Tender2LotQualificationResourceTest
    lot_patch_tender_qualifications,
    lot_get_tender_qualifications_collection,
    tender_qualification_cancelled,
    # TenderQualificationResourceTest
    post_tender_qualifications,
    get_tender_qualifications_collection,
    patch_tender_qualifications,
    get_tender_qualifications,
    patch_tender_qualifications_after_status_change,
    switch_bid_status_unsuccessul_to_active,
    lot_patch_tender_qualifications_lots_none,
    bot_patch_tender_qualification_complaint,
    bot_patch_tender_qualification_complaint_forbidden,
    # TenderQualificationRequirementResponseResourceTest
    create_qualification_requirement_response,
    patch_qualification_requirement_response,
    get_qualification_requirement_response,
    # TenderQualificationRequirementResponseEvidenceResourceTest
    create_qualification_requirement_response_evidence,
    patch_qualification_requirement_response_evidence,
    get_qualification_requirement_response_evidence,
)


@patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
class TenderQualificationRequirementResponseTestMixin(object):
    test_create_qualification_requirement_response = snitch(create_qualification_requirement_response)
    test_patch_qualification_requirement_response = snitch(patch_qualification_requirement_response)
    test_get_qualification_requirement_response = snitch(get_qualification_requirement_response)

    initial_criteria = test_criteria

    @patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderQualificationRequirementResponseTestMixin, self).setUp()
        response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
        criteria = response.json["data"]
        requirement = criteria[6]["requirementGroups"][0]["requirements"][0]
        self.requirement_id = requirement["id"]
        self.requirement_title = requirement["title"]


@patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
class TenderQualificationRequirementResponseEvidenceTestMixin(object):
    test_create_qualification_requirement_response_evidence = snitch(create_qualification_requirement_response_evidence)
    test_patch_qualification_requirement_response_evidence = snitch(patch_qualification_requirement_response_evidence)
    test_get_qualification_requirement_response_evidence = snitch(get_qualification_requirement_response_evidence)

    initial_criteria = test_criteria

    @patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderQualificationRequirementResponseEvidenceTestMixin, self).setUp()
        response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
        criteria = response.json["data"]
        requirement = criteria[6]["requirementGroups"][0]["requirements"][0]
        self.requirement_id = requirement["id"]
        self.requirement_title = requirement["title"]

        request_path = "/tenders/{}/qualifications/{}/requirement_responses?acc_token={}".format(
            self.tender_id, self.qualification_id, self.tender_token)

        rr_data = [{
            "title": "Requirement response",
            "description": "some description",
            "requirement": {
                "id": self.requirement_id,
                "title": self.requirement_title,
            },
            "value": True,
        }]

        response = self.app.post_json(request_path, {"data": rr_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.rr_id = response.json["data"][0]["id"]

        auth = self.app.authorization
        self.app.authorization = ("Basic", ("bot", ""))
        response = self.app.post(
            "/tenders/{}/qualifications/{}/documents?acc_token={}".format(
                self.tender_id, self.qualification_id, self.tender_token),
            upload_files=[("file", "name.doc", "content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.doc_id = response.json["data"]["id"]

        self.app.authorization = auth


class TenderQualificationBaseTestCase(BaseTenderContentWebTest):
    initial_status = "active.tendering"  # 'active.pre-qualification' status sets in setUp
    initial_bids = test_bids
    author_data = test_author
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderQualificationBaseTestCase, self).setUp()
        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.qualification_id = qualifications[0]["id"]


class TenderQualificationResourceTest(TenderQualificationBaseTestCase):

    test_post_tender_qualifications = snitch(post_tender_qualifications)
    test_get_tender_qualifications_collection = snitch(get_tender_qualifications_collection)
    test_patch_tender_qualifications = snitch(patch_tender_qualifications)
    test_get_tender_qualifications = snitch(get_tender_qualifications)
    test_patch_tender_qualifications_after_status_change = snitch(patch_tender_qualifications_after_status_change)


class Tender2LotQualificationResourceTest(TenderQualificationBaseTestCase):
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_lots = 2 * test_lots
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))

    test_patch_tender_qualifications = snitch(lot_patch_tender_qualifications)
    test_get_tender_qualifications_collection = snitch(lot_get_tender_qualifications_collection)
    test_tender_qualification_cancelled = snitch(tender_qualification_cancelled)
    test_lot_patch_tender_qualifications_lots_none = snitch(lot_patch_tender_qualifications_lots_none)


class TenderQualificationDocumentResourceTest(TenderQualificationBaseTestCase):
    initial_status = "active.tendering"
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderQualificationDocumentResourceTest, self).setUp()
        # list qualifications
        response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
        self.assertEqual(response.status, "200 OK")
        self.qualifications = response.json["data"]
        self.assertEqual(len(self.qualifications), 2)

    test_not_found = snitch(not_found)
    test_tender_owner_create_qualification_document = snitch(tender_owner_create_qualification_document)
    test_create_qualification_document = snitch(create_qualification_document)
    test_put_qualification_document = snitch(put_qualification_document)
    test_patch_qualification_document = snitch(patch_qualification_document)
    test_create_qualification_document_after_status_change = snitch(create_qualification_document_after_status_change)
    test_put_qualification_document_after_status_change = snitch(put_qualification_document_after_status_change)


class TenderQualificationComplaintResourceTest(TenderQualificationBaseTestCase):
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_author

    def setUp(self):
        super(TenderQualificationComplaintResourceTest, self).setUp()

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
    test_review_tender_award_claim = snitch(review_tender_award_claim)
    test_get_tender_qualification_complaint = snitch(get_tender_qualification_complaint)
    test_get_tender_qualification_complaints = snitch(get_tender_qualification_complaints)
    test_change_status_to_standstill_with_complaint = snitch(change_status_to_standstill_with_complaint)
    test_bot_patch_tender_qualification_complaint = snitch(bot_patch_tender_qualification_complaint)
    test_bot_patch_tender_qualification_complaint_forbidden = snitch(bot_patch_tender_qualification_complaint_forbidden)


class TenderLotQualificationComplaintResourceTest(TenderQualificationComplaintResourceTest):
    initial_lots = test_lots

    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_qualification_complaint = snitch(create_tender_lot_qualification_complaint)
    test_patch_tender_qualification_complaint = snitch(patch_tender_lot_qualification_complaint)
    test_get_tender_qualification_complaint = snitch(get_tender_lot_qualification_complaint)
    test_get_tender_qualification_complaints = snitch(get_tender_lot_qualification_complaints)


class Tender2LotQualificationComplaintResourceTest(TenderLotQualificationComplaintResourceTest):
    initial_lots = 2 * test_lots

    initial_auth = ("Basic", ("broker", ""))
    after_qualification_switch_to = "active.auction"

    test_create_tender_qualification_complaint = snitch(create_tender_2lot_qualification_complaint)


class Tender2LotQualificationClaimResourceTest(Tender2LotQualificationComplaintResourceTest):
    after_qualification_switch_to = "unsuccessful"

    def setUp(self):
        super(TenderQualificationComplaintResourceTest, self).setUp()

        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.qualification_id = qualifications[0]["id"]

        for qualification in qualifications:
            if qualification["bidID"] == self.initial_bids[0]["id"]:
                response = self.app.patch_json(
                    "/tenders/{}/qualifications/{}?acc_token={}".format(
                        self.tender_id, qualification["id"], self.tender_token
                    ),
                    {"data": {"status": "active", "qualified": True, "eligible": True}},
                )
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.json["data"]["status"], "active")
            else:
                response = self.app.patch_json(
                    "/tenders/{}/qualifications/{}?acc_token={}".format(
                        self.tender_id, qualification["id"], self.tender_token
                    ),
                    {"data": {"status": "unsuccessful"}},
                )
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.json["data"]["status"], "unsuccessful")
                self.unsuccessful_qualification_id = qualification["id"]

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")

    test_create_tender_qualification_claim = snitch(create_tender_qualification_claim)


class TenderQualificationComplaintDocumentResourceTest(TenderQualificationBaseTestCase):

    def setUp(self):
        super(TenderQualificationComplaintDocumentResourceTest, self).setUp()

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


class Tender2LotQualificationComplaintDocumentResourceTest(TenderQualificationComplaintDocumentResourceTest):
    initial_lots = 2 * test_lots

    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_qualification_complaint_document = snitch(create_tender_2lot_qualification_complaint_document)
    test_put_tender_qualification_complaint_document = snitch(put_tender_2lot_qualification_complaint_document)


class TenderIssueCBD1713Test(Tender2LotQualificationResourceTest):
    test_switch_bid_status_unsuccessul_to_active = snitch(switch_bid_status_unsuccessul_to_active)


class TenderQualificationRequirementResponseResourceTest(
    TenderQualificationRequirementResponseTestMixin,
    TenderQualificationBaseTestCase,
):
    pass


class TenderQualificationRequirementResponseEvidenceResourceTest(
    TenderQualificationRequirementResponseEvidenceTestMixin,
    TenderQualificationBaseTestCase,
):
    pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderQualificationRequirementResponseResourceTest))
    suite.addTest(unittest.makeSuite(TenderQualificationRequirementResponseEvidenceResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
