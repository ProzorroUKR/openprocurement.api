import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_cancellation,
    test_tender_below_draft_complaint,
    test_tender_below_lots,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    create_tender_complaint_document,
    not_found,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.open.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_open_bids,
)
from openprocurement.tender.open.tests.complaint_blanks import (
    bot_patch_tender_complaint,
    bot_patch_tender_complaint_forbidden,
    bot_patch_tender_complaint_mistaken,
    create_complaint_objection_validation,
    create_tender_complaint,
    mistaken_status_tender_complaint,
    objection_related_award_statuses,
    objection_related_document_of_evidence,
    objection_related_item_equals_related_cancellation,
    objection_related_item_equals_related_lot,
    patch_complaint_objection,
    patch_tender_complaint,
    patch_tender_complaint_document,
    put_tender_complaint_document,
    review_tender_complaint,
    review_tender_stopping_complaint,
)


class TenderUAComplaintResourceTestMixin:
    test_create_tender_complaint = snitch(create_tender_complaint)
    test_patch_tender_complaint = snitch(patch_tender_complaint)
    test_review_tender_complaint = snitch(review_tender_complaint)
    test_review_tender_stopping_complaint = snitch(review_tender_stopping_complaint)
    test_mistaken_status_tender_complaint = snitch(mistaken_status_tender_complaint)
    test_bot_patch_tender_complaint = snitch(bot_patch_tender_complaint)
    test_bot_patch_tender_complaint_mistaken = snitch(bot_patch_tender_complaint_mistaken)
    test_bot_patch_tender_complaint_forbidden = snitch(bot_patch_tender_complaint_forbidden)


class TenderComplaintResourceTest(
    BaseTenderUAContentWebTest,
    TenderUAComplaintResourceTestMixin,
):
    test_author = test_tender_below_author
    initial_lots = test_tender_below_lots


class TenderComplaintDocumentResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_tender_below_lots

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


class ComplaintObjectionMixin:
    test_create_complaint_objection_validation = snitch(create_complaint_objection_validation)
    test_patch_complaint_objection = snitch(patch_complaint_objection)


class TenderComplaintObjectionMixin:
    app = None
    tender_id = None
    tender_token = None
    complaint_on = "tender"

    def create_complaint(self, complaint_data, status=201, with_valid_relates_to=False):
        if with_valid_relates_to:
            complaint_data["objections"][0]["relatesTo"] = self.complaint_on
            complaint_data["objections"][0]["relatedItem"] = self.tender_id
        url = f"/tenders/{self.tender_id}/complaints"
        return self.app.post_json(url, {"data": complaint_data}, status=status)

    def add_complaint_document(self, complaint_id, complaint_token, status=201):
        doc_data = {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
        url = f"/tenders/{self.tender_id}/complaints/{complaint_id}/documents?acc_token={complaint_token}"
        return self.app.post_json(url, {"data": doc_data}, status=status)

    def patch_complaint(self, complaint_id, complaint_data, complaint_token, status=200):
        url = f"/tenders/{self.tender_id}/complaints/{complaint_id}?acc_token={complaint_token}"
        return self.app.patch_json(url, {"data": complaint_data}, status=status)


class TenderCancellationComplaintObjectionMixin:
    app = None
    tender_id = None
    tender_token = None
    cancellation_id = None
    complaint_on = "cancellation"

    def create_complaint(self, complaint_data, status=201, with_valid_relates_to=False):
        if with_valid_relates_to:
            complaint_data["objections"][0]["relatesTo"] = self.complaint_on
            complaint_data["objections"][0]["relatedItem"] = self.cancellation_id
        url = f"/tenders/{self.tender_id}/cancellations/{self.cancellation_id}/complaints"
        return self.app.post_json(url, {"data": complaint_data}, status=status)

    def patch_complaint(self, complaint_id, complaint_data, complaint_token, status=200):
        url = (
            f"/tenders/{self.tender_id}/cancellations/{self.cancellation_id}/complaints/{complaint_id}?"
            f"acc_token={complaint_token}"
        )
        return self.app.patch_json(url, {"data": complaint_data}, status=status)

    def create_cancellation(self, related_lot=None):
        # Create cancellation
        cancellation = deepcopy(test_tender_below_cancellation)
        cancellation.update({"reasonType": "noDemand"})
        if self.initial_data.get("lots"):
            cancellation.update({"relatedLot": related_lot if related_lot else self.initial_data["lots"][0]["id"]})
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/cancellations?acc_token={self.tender_token}",
            {"data": cancellation},
        )
        cancellation = response.json["data"]
        self.cancellation_id = cancellation["id"]

        # Add document and update cancellation status to pending

        self.app.post_json(
            f"/tenders/{self.tender_id}/cancellations/{self.cancellation_id}/documents?acc_token={self.tender_token}",
            {
                "data": {
                    "title": "укр.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.app.patch_json(
            f"/tenders/{self.tender_id}/cancellations/{self.cancellation_id}?acc_token={self.tender_token}",
            {"data": {"status": "pending"}},
        )


class TenderQualificationComplaintObjectionMixin:
    app = None
    tender_id = None
    tender_token = None
    qualification_id = None
    complaint_on = "qualification"

    def create_qualification(self):
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

        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")

    def create_complaint(self, complaint_data, status=201, with_valid_relates_to=False):
        if with_valid_relates_to:
            complaint_data["objections"][0]["relatesTo"] = self.complaint_on
            complaint_data["objections"][0]["relatedItem"] = self.qualification_id
        url = (
            f"/tenders/{self.tender_id}/qualifications/{self.qualification_id}/"
            f"complaints?acc_token={list(self.initial_bids_tokens.values())[0]}"
        )
        return self.app.post_json(url, {"data": complaint_data}, status=status)

    def add_complaint_document(self, complaint_id, complaint_token, status=201):
        doc_data = {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
        url = (
            f"/tenders/{self.tender_id}/qualifications/{self.qualification_id}/"
            f"complaints/{complaint_id}/documents?acc_token={complaint_token}"
        )
        return self.app.post_json(url, {"data": doc_data}, status=status)

    def patch_complaint(self, complaint_id, complaint_data, complaint_token, status=200):
        url = (
            f"/tenders/{self.tender_id}/qualifications/{self.qualification_id}/complaints/{complaint_id}?"
            f"acc_token={complaint_token}"
        )
        return self.app.patch_json(url, {"data": complaint_data}, status=status)


class TenderAwardComplaintObjectionMixin:
    app = None
    tender_id = None
    tender_token = None
    award_id = None
    complaint_on = "award"

    def create_award(self):
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                f"/tenders/{self.tender_id}/awards",
                {
                    "data": {
                        "suppliers": [test_tender_below_organization],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                        "lotID": self.initial_lots[0]["id"],
                    }
                },
            )

        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")

        with change_auth(self.app, ("Basic", ("token", ""))):
            self.app.patch_json(
                f"/tenders/{self.tender_id}/awards/{self.award_id}",
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )

    def create_complaint(self, complaint_data, status=201, with_valid_relates_to=False):
        if with_valid_relates_to:
            complaint_data["objections"][0]["relatesTo"] = self.complaint_on
            complaint_data["objections"][0]["relatedItem"] = self.award_id
        url = (
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints"
            f"?acc_token={list(self.initial_bids_tokens.values())[0]}"
        )
        return self.app.post_json(url, {"data": complaint_data}, status=status)

    def add_complaint_document(self, complaint_id, complaint_token, status=201):
        doc_data = {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
        url = (
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints/"
            f"{complaint_id}/documents?acc_token={complaint_token}"
        )
        return self.app.post_json(url, {"data": doc_data}, status=status)

    def patch_complaint(self, complaint_id, complaint_data, complaint_token, status=200):
        url = (
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints/{complaint_id}?"
            f"acc_token={complaint_token}"
        )
        return self.app.patch_json(url, {"data": complaint_data}, status=status)


class TenderComplaintObjectionTest(
    BaseTenderUAContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    initial_lots = test_tender_below_lots * 2

    test_objection_related_item_equals_related_lot = snitch(objection_related_item_equals_related_lot)
    test_objection_related_document_of_evidence = snitch(objection_related_document_of_evidence)


class TenderCancellationComplaintObjectionTest(
    BaseTenderUAContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    initial_lots = test_tender_below_lots * 2

    test_objection_related_item_equals_related_cancellation = snitch(objection_related_item_equals_related_cancellation)

    def setUp(self):
        super().setUp()
        self.set_complaint_period_end()
        self.create_cancellation()


class TenderAwardComplaintObjectionTest(
    BaseTenderUAContentWebTest,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    initial_status = "active.qualification"
    initial_bids = test_tender_open_bids
    initial_lots = test_tender_below_lots

    test_objection_related_award_statuses = snitch(objection_related_award_statuses)
    test_objection_related_document_of_evidence = snitch(objection_related_document_of_evidence)

    def setUp(self):
        super().setUp()
        self.create_award()


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
