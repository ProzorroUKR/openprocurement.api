# -*- coding: utf-8 -*-
from copy import deepcopy
from uuid import uuid4


# TenderStageAQuestionResourceTest
from openprocurement.tender.belowthreshold.tests.base import test_cancellation


def create_question_bad_author(self):

    request_path = "/tenders/{}/questions".format(self.tender_id)
    bad_author = deepcopy(self.author_data)
    good_id = bad_author["identifier"]["id"]
    good_scheme = self.author_data["identifier"]["scheme"]
    bad_author["identifier"]["id"] = "12345"
    response = self.app.post_json(
        request_path,
        {"data": {"title": "question title", "description": "question description", "author": bad_author}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Author can't create question", u"location": u"body", u"name": u"author"}],
    )
    bad_author["identifier"]["id"] = good_id
    bad_author["identifier"]["scheme"] = "XI-IATI"
    response = self.app.post_json(
        request_path,
        {"data": {"title": "question title", "description": "question descriptionn", "author": bad_author}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Author can't create question", u"location": u"body", u"name": u"author"}],
    )


def create_tender_question_with_question(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "author": self.author_data,
                "questionOf": "tender",
                "relatedItem": self.tender_id,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    self.assertEqual(question["author"]["name"], self.author_data["name"])
    self.assertIn("id", question)
    self.assertIn(question["id"], response.headers["Location"])

    self.set_enquiry_period_end()

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")

    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")


def create_tender_question(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    self.assertEqual(question["author"]["name"], self.author_data["name"])
    self.assertIn("id", question)
    self.assertIn(question["id"], response.headers["Location"])

    self.set_enquiry_period_end()

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")

    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")


# TenderStage2LotQuestionResourceTest
def create_tender_with_lots_question(self):
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.lots[0]["id"],
                "author": self.author_data,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in active lot status")

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.lots[1]["id"],
                "author": self.author_data,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    self.assertEqual(question["author"]["name"], self.test_bids_data[0]["tenderers"][0]["name"])
    self.assertIn("id", question)
    self.assertIn(question["id"], response.headers["Location"])


def create_question_on_lot_without_perm(self):
    tender = self.db.get(self.tender_id)
    lot_id = self.lots[0]["id"]
    for firm in tender["shortlistedFirms"]:
        firm["lots"] = [{"id": self.lots[1]["id"]}]
    self.db.save(tender)

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": lot_id,
                "author": self.author_data,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Author can't create question", u"location": u"body", u"name": u"author"}],
    )


def patch_tender_with_lots_question(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.lots[0]["id"],
                "author": self.author_data,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question["id"], self.tender_token),
        {"data": {"answer": "answer"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update question only in active lot status")

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.lots[1]["id"],
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

    response = self.app.get("/tenders/{}/questions/{}".format(self.tender_id, question["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["answer"], "answer")
