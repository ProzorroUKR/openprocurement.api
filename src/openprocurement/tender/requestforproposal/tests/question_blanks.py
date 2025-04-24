from copy import deepcopy

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.requestforproposal.tests.base import (
    test_tender_rfp_cancellation,
)

# TenderLotQuestionResourceTest


def lot_create_tender_question(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    without_complaints = ["reporting", "requestForProposal", "closeFrameworkAgreementSelectionUA"]
    if RELEASE_2020_04_19 > get_now() or tender["procurementMethodType"] in without_complaints:
        # For procedures: openua, openuadefense, openeu, negotiation, negotiation.quick, esco, copetitivedialogue, cfaua
        # validation after RELEASE_2020_04_19 is useless, because enquiryPeriod ended before complaintPeriod

        cancellation = deepcopy(test_tender_rfp_cancellation)
        cancellation.update(
            {
                "status": "active",
                "cancellationOf": "lot",
                "relatedLot": self.initial_lots[0]["id"],
            }
        )
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        self.assertEqual(response.status, "201 Created")

        cancellation_id = response.json["data"]["id"]

        if RELEASE_2020_04_19 < get_now():
            activate_cancellation_after_2020_04_19(self, cancellation_id)

        response = self.app.post_json(
            "/tenders/{}/questions".format(self.tender_id),
            {
                "data": {
                    "title": "question title",
                    "description": "question description",
                    "questionOf": "lot",
                    "relatedItem": self.initial_lots[0]["id"],
                    "author": self.author_data,
                }
            },
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can add/update question only in active lot status",
        )

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[1]["id"],
                "author": self.author_data,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    self.assertIn("id", question)
    self.assertIn(question["id"], response.headers["Location"])

    self.set_enquiry_period_end()
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[1]["id"],
                "author": self.author_data,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")

    self.set_status(self.forbidden_question_add_actions_status)
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[1]["id"],
                "author": self.author_data,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")


def lot_patch_tender_question(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": self.author_data,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    without_complaints = ["reporting", "requestForProposal", "closeFrameworkAgreementSelectionUA"]
    if RELEASE_2020_04_19 > get_now() or tender["procurementMethodType"] in without_complaints:
        # For procedures: openua, openuadefense, openeu, negotiation, negotiation.quick, esco, copetitivedialogue, cfaua
        # validation after RELEASE_2020_04_19 is useless, because enquiryPeriod ended before complaintPeriod

        cancellation = deepcopy(test_tender_rfp_cancellation)
        cancellation.update(
            {
                "status": "active",
                "cancellationOf": "lot",
                "relatedLot": self.initial_lots[0]["id"],
            }
        )
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        self.assertEqual(response.status, "201 Created")
        cancellation_id = response.json["data"]["id"]

        if RELEASE_2020_04_19 < get_now():
            activate_cancellation_after_2020_04_19(self, cancellation_id)

        response = self.app.patch_json(
            "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question["id"], self.tender_token),
            {"data": {"answer": "answer"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can add/update question only in active lot status",
        )

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[1]["id"],
                "author": self.author_data,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question["id"], self.tender_token),
        {"data": {"answer": "answer"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["answer"], "answer")
    self.assertIn("dateAnswered", response.json["data"])

    response = self.app.get(
        "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question["id"], self.tender_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["answer"], "answer")
    self.assertIn("dateAnswered", response.json["data"])

    if self.forbidden_question_add_actions_status != self.forbidden_question_update_actions_status:
        response = self.app.post_json(
            "/tenders/{}/questions".format(self.tender_id),
            {
                "data": {
                    "title": "question title",
                    "description": "question description",
                    "questionOf": "lot",
                    "relatedItem": self.initial_lots[1]["id"],
                    "author": self.author_data,
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        question = response.json["data"]

        self.set_status(self.forbidden_question_add_actions_status)

        response = self.app.patch_json(
            "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question["id"], self.tender_token),
            {"data": {"answer": "answer"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["answer"], "answer")
        self.assertIn("dateAnswered", response.json["data"])

    self.set_status(self.forbidden_question_update_actions_status)

    response = self.app.patch_json(
        "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question["id"], self.tender_token),
        {"data": {"answer": "changed answer"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update question in current ({}) tender status".format(self.forbidden_question_update_actions_status),
    )
