# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import activate_cancellation_with_complaints_after_2020_04_19
from openprocurement.tender.belowthreshold.tests.base import test_organization, test_author, test_cancellation


# TenderQuestionResourceTest


def create_tender_question(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": test_author}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    self.assertEqual(question["author"]["name"], test_organization["name"])
    self.assertIn("id", question)
    self.assertIn(question["id"], response.headers["Location"])

    self.set_enquiry_period_end()
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": test_author}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")

    self.set_status("active.auction")
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": test_author}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")


# TenderLotQuestionResourceTest


def tender_has_unanswered_questions(self):
    question_id = self.create_question_for("tender", self.tender_id)

    self.set_status("active.auction", {"status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")

    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def lot_has_unanswered_questions(self):
    question_id = self.create_question_for("lot", self.initial_lots[0]["id"])

    self.set_status("active.auction", {"status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]

    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "unsuccessful")
    else:
        self.app.authorization = ("Basic", ("chronograph", ""))
        response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json["data"]["status"], "unsuccessful")


def item_has_unanswered_questions(self):
    items = self.app.get("/tenders/{}".format(self.tender_id)).json["data"]["items"]
    question_id = self.create_question_for("item", items[0]["id"])

    self.set_status("active.auction", {"status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]

    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "unsuccessful")
    else:
        self.app.authorization = ("Basic", ("chronograph", ""))
        response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json["data"]["status"], "unsuccessful")
