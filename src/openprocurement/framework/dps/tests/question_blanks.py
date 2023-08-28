from datetime import timedelta
from freezegun import freeze_time

from openprocurement.api.context import get_now
from openprocurement.framework.dps.tests.base import test_question_data
from openprocurement.tender.core.procedure.utils import dt_from_iso


def create_question_invalid(self):
    request_path = f"/frameworks/{self.framework_id}/questions"

    response = self.app.post_json(
        "/frameworks/some_id/questions",
        {"data": test_question_data},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "framework_id"}]
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


def create_question_check_framework_status(self):
    request_path = f"/frameworks/{self.framework_id}/questions"
    response = self.app.get(f"/frameworks/{self.framework_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "draft")

    response = self.app.post_json(
        request_path,
        {"data": test_question_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add question in current (draft) framework status"
    )

    self.activate_framework()
    response = self.app.get(f"/frameworks/{self.framework_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.post_json(
        request_path,
        {"data": test_question_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    self.assertIn("id", question)
    self.assertIn(question["id"], response.headers["Location"])


def create_question_check_enquiry_period(self):
    self.activate_framework()
    self.framework_document = self.mongodb.frameworks.get(self.framework_id)
    self.framework_document_patch = {"enquiryPeriod": {"endDate": (get_now() - timedelta(days=1)).isoformat()}}
    self.save_changes()

    request_path = f"/frameworks/{self.framework_id}/questions"
    response = self.app.post_json(
        request_path,
        {"data": test_question_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn(
        "Question can be add only during the enquiry period",
        response.json["errors"][0]["description"],
    )

    self.framework_document = self.mongodb.frameworks.get(self.framework_id)
    self.framework_document_patch = {
        "enquiryPeriod": {
            "startDate": (get_now() + timedelta(days=1)).isoformat(),
            "endDate": (get_now() + timedelta(days=11)).isoformat(),
        }
    }
    self.save_changes()

    response = self.app.post_json(
        request_path,
        {"data": test_question_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn(
        "Question can be add only during the enquiry period",
        response.json["errors"][0]["description"],
    )


def patch_framework_question(self):
    request_path = f"/frameworks/{self.framework_id}/questions"
    self.activate_framework()
    response = self.app.post_json(
        request_path,
        {"data": test_question_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    request_path = f"/frameworks/{self.framework_id}/questions/{question['id']}"

    response = self.app.patch_json(
        request_path,
        {"data": {"answer": "answer"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden"
    )

    response = self.app.patch_json(
        f"{request_path}?acc_token={self.framework_token}",
        {"data": {}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {
            "location": "body",
            "name": "answer",
            "description": [
                "This field is required."
            ]
        }
    )

    response = self.app.patch_json(
        f"{request_path}?acc_token={self.framework_token}",
        {"data": {"test": "test"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {
            "location": "body",
            "name": "test",
            "description": "Rogue field"
        }
    )

    response = self.app.get(f"/frameworks/{self.framework_id}")
    framework = response.json["data"]
    with freeze_time((dt_from_iso(framework["enquiryPeriod"]["endDate"]) + timedelta(days=1)).isoformat()):

        response = self.app.patch_json(
            f"{request_path}?acc_token={self.framework_token}",
            {"data": {"answer": "answer"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["answer"], "answer")
        self.assertIn("dateAnswered", response.json["data"])

    with freeze_time((dt_from_iso(framework["enquiryPeriod"]["clarificationsUntil"]) + timedelta(minutes=1)).isoformat()):
        response = self.app.patch_json(
            f"{request_path}?acc_token={self.framework_token}",
            {"data": {"answer": "answer"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0],
            {
                "location": "body",
                "name": "data",
                "description": "Allowed to update question only before enquiryPeriod.clarificationsUntil"
            }
        )

    response = self.app.patch_json(
        f"/frameworks/{self.framework_id}/questions/some_id", {"data": {"answer": "answer"}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "question_id"}]
    )

    response = self.app.patch_json("/frameworks/some_id/questions/some_id", {"data": {"answer": "answer"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "framework_id"}]
    )


def get_framework_question(self):
    request_path = f"/frameworks/{self.framework_id}/questions"
    self.activate_framework()
    response = self.app.post_json(
        request_path,
        {"data": test_question_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]
    request_path = f"/frameworks/{self.framework_id}/questions/{question['id']}"

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"],  question)

    response = self.app.get(f"/frameworks/{self.framework_id}/questions/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "question_id"}]
    )

    response = self.app.get("/frameworks/some_id/questions/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "framework_id"}]
    )


def get_framework_questions(self):
    request_path = f"/frameworks/{self.framework_id}/questions"
    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])

    self.activate_framework()

    # create first question
    response = self.app.post_json(
        request_path,
        {"data": test_question_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    # create second question
    response = self.app.post_json(
        request_path,
        {"data": test_question_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0], question)

    response = self.app.get("/frameworks/some_id/questions", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "framework_id"}]
    )
