# -*- coding: utf-8 -*-
from copy import deepcopy
from uuid import uuid4


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
        [{"description": "Author can't create question", "location": "body", "name": "author"}],
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
        [{"description": "Author can't create question", "location": "body", "name": "author"}],
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


def lot_create_tender_question_without_perm(self):
    tender = self.mongodb.tenders.get(self.tender_id)
    lot_id = self.lots[0]["id"]
    for firm in tender["shortlistedFirms"]:
        firm["lots"] = [{"id": self.lots[1]["id"]}]
    self.mongodb.tenders.save(tender)

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
        [{"description": "Author can't create question", "location": "body", "name": "author"}],
    )


def lot_create_tender_question_on_item(self):
    tender = self.mongodb.tenders.get(self.tender_id)
    item = tender["items"][0]
    new_item = deepcopy(item)
    new_item["id"] = uuid4().hex
    new_item["relatedLot"] = self.lots[1]["id"]
    tender["items"] = [item, new_item]
    for firm in tender["shortlistedFirms"]:
        firm["lots"] = [{"id": self.lots[1]["id"]}]
    self.mongodb.tenders.save(tender)

    # Create question on item
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "item",
                "relatedItem": new_item["id"],
                "author": self.author_data,
            }
        },
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # Can't create question on item, on which we haven't access
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "item",
                "relatedItem": item["id"],
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
        [{"description": "Author can't create question", "location": "body", "name": "author"}],
    )

    # Create question on tender
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "tender",
                "author": self.author_data,
            }
        },
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

def create_tender_question_on_item(self):
    tender = self.mongodb.tenders.get(self.tender_id)
    item = tender["items"][0]
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "item",
                "relatedItem": item["id"],
                "author": self.author_data,
            }
        },
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "tender",
                "author": self.author_data,
            }
        },
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
