# -*- coding: utf-8 -*-


# CompetitiveDialogEUQuestionResourceTest
def create_tender_question_invalid_eu(self):
    """
      Test the creating invalid question
    """

    # Try create question with invalid tender_id
    response = self.app.post_json(
        "/tenders/some_id/questions",
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    request_path = "/tenders/{}/questions".format(self.tender_id)

    # Try create question without content_type
    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Content-Type header should be one of ['application/json']",
                u"location": u"header",
                u"name": u"Content-Type",
            }
        ],
    )

    # Try create question with bad json
    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"No JSON object could be decoded", u"location": u"body", u"name": u"data"}],
    )

    # Try create question with bad json
    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    # Try create question with invalid json
    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    # Try create question without required fields
    response = self.app.post_json(request_path, {"data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {u"description": [u"This field is required."], u"location": u"body", u"name": u"author"},
            {u"description": [u"This field is required."], u"location": u"body", u"name": u"title"},
        ],
    )

    # Try create question with invalid fields
    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    # Try create question with invalid identifier
    response = self.app.post_json(request_path, {"data": {"author": {"identifier": "invalid_value"}}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {
                    u"identifier": [u"Please use a mapping for this field or Identifier instance instead of unicode."]
                },
                u"location": u"body",
                u"name": u"author",
            }
        ],
    )

    # Try create question without required fields
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
                u"description": {
                    u"contactPoint": [u"This field is required."],
                    u"identifier": {u"scheme": [u"This field is required."], u"id": [u"This field is required."]},
                    u"name": [u"This field is required."],
                    u"address": [u"This field is required."],
                },
                u"location": u"body",
                u"name": u"author",
            }
        ],
    )

    # Try create question without required fields and with invalid identifier.uri
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
                u"description": {
                    u"contactPoint": [u"This field is required."],
                    u"identifier": {
                        u"scheme": [u"This field is required."],
                        u"id": [u"This field is required."],
                        u"uri": [u"Not a well formed URL."],
                    },
                    u"address": [u"This field is required."],
                },
                u"location": u"body",
                u"name": u"author",
            }
        ],
    )

    # Try create question without required field(description)
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "author": self.author_data,
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
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"relatedItem"}],
    )

    # Try create question with bad relatedItem id
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "author": self.author_data,
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
        [{u"description": [u"relatedItem should be one of lots"], u"location": u"body", u"name": u"relatedItem"}],
    )


def create_tender_question_eu(self):
    """
      Create question with many posible ways
    """

    # Create question, and check fields match
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    self.assertEqual(question["author"]["name"], self.test_bids_data[0]["tenderers"][0]["name"])
    self.assertIn("id", question)
    self.assertIn(question["id"], response.headers["Location"])

    # Shift time to end of enquiry period
    self.set_enquiry_period_end()

    # Try create question, when enquiry period end
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")

    self.time_shift("active.pre-qualification")  # Shift time to status active.pre-qualification
    self.check_chronograph()

    # Try create question when tender in status active.pre-qualification
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add question only in enquiryPeriod")


def get_tender_question_eu(self):
    """
      Try get tender question
    """
    # Create question
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]  # save question

    # Get question by tender_id, and question_id
    response = self.app.get("/tenders/{}/questions/{}".format(self.tender_id, question["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(set(response.json["data"]), set([u"id", u"date", u"title", u"description", u"questionOf"]))

    # Add answer to question
    response = self.app.patch_json(
        "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question["id"], self.tender_token),
        {"data": {"answer": "answer"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["answer"], "answer")
    self.assertIn("dateAnswered", response.json["data"])
    question["answer"] = "answer"
    question["dateAnswered"] = response.json["data"]["dateAnswered"]

    self.time_shift("active.pre-qualification")  # Shift time tender to status active.pre-qualification
    response = self.check_chronograph()

    # Get question by token_id, and question_id
    response = self.app.get("/tenders/{}/questions/{}".format(self.tender_id, question["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], question)

    # Try get question by bad question_id
    response = self.app.get("/tenders/{}/questions/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"question_id"}]
    )

    # Try get question by bad token_id, and question_id
    response = self.app.get("/tenders/some_id/questions/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def get_tender_questions_eu(self):
    """
      Test the get questions
    """
    # Create question
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    # Get question
    response = self.app.get("/tenders/{}/questions".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"date", u"title", u"description", u"questionOf"]))

    # Add answer on question
    response = self.app.patch_json(
        "/tenders/{}/questions/{}?acc_token={}".format(self.tender_id, question["id"], self.tender_token),
        {"data": {"answer": "answer"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["answer"], "answer")
    self.assertIn("dateAnswered", response.json["data"])
    question["answer"] = "answer"
    question["dateAnswered"] = response.json["data"]["dateAnswered"]

    self.time_shift("active.pre-qualification")  # Shift time to tender status active.pre-qualification
    self.check_chronograph()

    # Try get questions by tender_id
    response = self.app.get("/tenders/{}/questions".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], question)

    # Try get question by bad tender_id
    response = self.app.get("/tenders/some_id/questions", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )
