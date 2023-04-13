# -*- coding: utf-8 -*-
from openprocurement.api.tests.base import change_auth
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_author,
    test_tender_below_cancellation,
)
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.core.utils import get_now


def create_tender_question_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/questions",
        {"data": {"title": "question title", "description": "question description", "author": test_tender_below_author}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    request_path = "/tenders/{}/questions".format(self.tender_id)

    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Content-Type header should be one of ['application/json']",
                "location": "header",
                "name": "Content-Type",
            }
        ],
    )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {"description": ["This field is required."], "location": "body", "name": "author"},
            {"description": ["This field is required."], "location": "body", "name": "title"},
        ],
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"author": {"identifier": "invalid_value"}}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "identifier": ["Please use a mapping for this field or Identifier instance instead of str."]
                },
                "location": "body",
                "name": "author",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"title": "question title", "description": "question description", "author": {"identifier": {}}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "contactPoint": ["This field is required."],
                    "identifier": {"scheme": ["This field is required."], "id": ["This field is required."]},
                    "name": ["This field is required."],
                    "address": ["This field is required."],
                },
                "location": "body",
                "name": "author",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "author": {"name": "name", "identifier": {"uri": "invalid_value"}},
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "contactPoint": ["This field is required."],
                    "identifier": {
                        "scheme": ["This field is required."],
                        "id": ["This field is required."],
                        "uri": ["Not a well formed URL."],
                    },
                    "address": ["This field is required."],
                },
                "location": "body",
                "name": "author",
            }
        ],
    )

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "author": test_tender_below_author,
                "questionOf": "lot",
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "relatedItem"}],
    )

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "author": test_tender_below_author,
                "questionOf": "lot",
                "relatedItem": "0" * 32,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["relatedItem should be one of lots"], "location": "body", "name": "relatedItem"}],
    )

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "author": test_tender_below_author,
                "questionOf": "item",
                "relatedItem": "0" * 32,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["relatedItem should be one of items"], "location": "body", "name": "relatedItem"}],
    )

    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post_json(
            "/tenders/{}/questions".format(self.tender_id),
            {
                "data": {
                    "title": "question title",
                    "description": "question description",
                    "author": test_tender_below_author,
                },
            },
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Broker Accreditation level does not permit question creation"
    )


def create_tender_question(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": test_tender_below_author}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    self.assertEqual(question["author"]["name"], test_tender_below_organization["name"])
    self.assertIn("id", question)
    self.assertIn(question["id"], response.headers["Location"])

    self.set_enquiry_period_end()
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": test_tender_below_author}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")

    self.set_status(self.forbidden_question_add_actions_status)
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": test_tender_below_author}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")


def patch_tender_question(self):
    author = getattr(self, "author_data", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": author}},
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

    response = self.app.patch_json(
        "/tenders/{}/questions/some_id".format(self.tender_id), {"data": {"answer": "answer"}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "question_id"}]
    )

    response = self.app.patch_json("/tenders/some_id/questions/some_id", {"data": {"answer": "answer"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/questions/{}".format(self.tender_id, question["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["answer"], "answer")
    self.assertIn("dateAnswered", response.json["data"])

    if self.forbidden_question_add_actions_status != self.forbidden_question_update_actions_status:
        response = self.app.post_json(
            "/tenders/{}/questions".format(self.tender_id),
            {"data": {"title": "question title", "description": "question description", "author": author}},
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
        {"data": {"answer": "another answer"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update question in current ({}) tender status".format(
            self.forbidden_question_update_actions_status
        ),
    )


def get_tender_question(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": test_tender_below_author}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    response = self.app.get("/tenders/{}/questions/{}".format(self.tender_id, question["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(set(response.json["data"]), set(["id", "date", "title", "description", "questionOf"]))

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/questions/{}".format(self.tender_id, question["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], question)

    response = self.app.get("/tenders/{}/questions/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "question_id"}]
    )

    response = self.app.get("/tenders/some_id/questions/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def get_tender_questions(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": test_tender_below_author}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    response = self.app.get("/tenders/{}/questions".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(set(response.json["data"][0]), set(["id", "date", "title", "description", "questionOf"]))

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/questions".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], question)

    response = self.app.get("/tenders/some_id/questions", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


# TenderLotQuestionResourceTest


def lot_create_tender_question(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    without_complaints = ["reporting", "belowThreshold", "closeFrameworkAgreementSelectionUA"]
    if RELEASE_2020_04_19 > get_now() or tender["procurementMethodType"] in without_complaints:
        # For procedures: openua, openuadefense, openeu, negotiation, negotiation.quick, esco, copetitivedialogue, cfaua
        # validation after RELEASE_2020_04_19 is useless, because enquiryPeriod ended before complaintPeriod

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

        if RELEASE_2020_04_19 < get_now():
            activate_cancellation_after_2020_04_19(self, cancellation_id)

        response = self.app.post_json(
            "/tenders/{}/questions".format(self.tender_id, self.tender_token),
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
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
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
    self.assertEqual(question["author"]["name"], self.author_data["name"])
    self.assertIn("id", question)
    self.assertIn(question["id"], response.headers["Location"])

    self.set_enquiry_period_end()
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
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
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
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
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
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

    without_complaints = ["reporting", "belowThreshold", "closeFrameworkAgreementSelectionUA"]
    if RELEASE_2020_04_19 > get_now() or tender["procurementMethodType"] in without_complaints:
        # For procedures: openua, openuadefense, openeu, negotiation, negotiation.quick, esco, copetitivedialogue, cfaua
        # validation after RELEASE_2020_04_19 is useless, because enquiryPeriod ended before complaintPeriod

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
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
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
            "/tenders/{}/questions".format(self.tender_id, self.tender_token),
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
        "Can't update question in current ({}) tender status".format(
            self.forbidden_question_update_actions_status
        ),
    )


def lot_patch_tender_question_lots_none(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    lots = response.json["data"]["lots"]
    lots[0]["id"] = "1" * 32

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
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

    for l in lots:
        l.pop("auctionPeriod", None)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"lots": lots}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")

    errors = {error["name"]: error["description"] for error in response.json["errors"]}
    self.assertEqual(errors["questions"][0], {"relatedItem": ["relatedItem should be one of lots"]})


def lot_patch_tender_question_items_none(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    items = response.json["data"]["items"]
    items[0]["id"] = "1"

    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "item",
                "relatedItem": response.json["data"]["items"][0]["id"],
                "author": self.author_data,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")

    errors = {error["name"]: error["description"] for error in response.json["errors"]}
    self.assertEqual(errors["questions"][0], {"relatedItem": ["relatedItem should be one of items"]})
