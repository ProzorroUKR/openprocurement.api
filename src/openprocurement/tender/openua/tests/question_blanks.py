# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import activate_cancellation_with_complaints_after_2020_04_19
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_cancellation


# TenderLotQuestionResourceTest


def tender_has_unanswered_questions(self):
    question_id = self.create_question_for("tender", self.tender_id)

    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_tender_below_cancellation)
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
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_tender_below_cancellation)
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
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "unsuccessful")


def item_has_unanswered_questions(self):
    items = self.app.get("/tenders/{}".format(self.tender_id)).json["data"]["items"]
    question_id = self.create_question_for("item", items[0]["id"])

    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_tender_below_cancellation)
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
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "unsuccessful")
