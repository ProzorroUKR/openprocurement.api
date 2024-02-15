from copy import deepcopy

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_cancellation,
)
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_with_complaints_after_2020_04_19,
)

# TenderLotQuestionResourceTest


def tender_has_unanswered_questions(self):
    question_id = self.create_question_for("tender", self.tender_id)

    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
        }
    )
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

    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "unsuccessful")
    else:
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "unsuccessful")


# TenderDPSLotQuestionResourceTest
def dps_create_tender_question_valid_author(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": test_tender_below_author,
            }
        },
    )
    self.assertEqual(response.status, "201 OK")


def dps_create_tender_question_check_author(self):
    # supplier not form agreement contract
    author_data = deepcopy(test_tender_below_author)
    author_data["identifier"]["id"] = "111111"
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": author_data,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden to add question for non-qualified suppliers")

    # suspended contract supplier
    author_data["identifier"]["id"] = "87654321"
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": author_data,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden to add question for non-qualified suppliers")

    # active contract supplier
    author_data["identifier"]["id"] = "00037256"
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": author_data,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
