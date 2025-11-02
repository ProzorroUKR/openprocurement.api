import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.framework.core.tests.base import BaseFrameworkCoreWebTest
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.tests.base import (
    test_framework_dps_config,
    test_framework_dps_data,
    test_question_data,
)
from tests.base.constants import DOCS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

TARGET_DIR_QUESTIONS = "docs/source/frameworks/basic-actions/http/questions/"

test_framework_dps_data = deepcopy(test_framework_dps_data)
test_framework_dps_config = deepcopy(test_framework_dps_config)


class QuestionsFrameworkOpenResourceTest(BaseFrameworkCoreWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    initial_data = test_framework_dps_data
    initial_config = test_framework_dps_config
    framework_type = DPS_TYPE
    freezing_datetime = "2023-01-01T00:00:00+02:00"
    docservice_url = DOCS_URL

    def setUp(self):
        self.setUpMock()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.tearDownMock()

    def test_docs(self):
        self.app.authorization = ("Basic", ("broker", ""))

        # empty frameworks listing
        data = deepcopy(self.initial_data)
        data["qualificationPeriod"]["endDate"] = (get_now() + timedelta(days=400)).isoformat()
        response = self.app.get("/frameworks")
        self.assertEqual(response.json["data"], [])

        # create frameworks
        self.create_framework(data=data)
        self.activate_framework()

        with open(TARGET_DIR_QUESTIONS + "get-framework.http", "w") as self.app.file_obj:
            response = self.app.get("/frameworks/{}".format(self.framework_id))
            self.assertEqual(response.status, "200 OK")

        # Questions

        with open(TARGET_DIR_QUESTIONS + "ask-question.http", "w") as self.app.file_obj:
            response = self.app.post_json(f"/frameworks/{self.framework_id}/questions", {"data": test_question_data})
            self.assertEqual(response.status, "201 Created")
            question = response.json["data"]

        with open(TARGET_DIR_QUESTIONS + "get-question.http", "w") as self.app.file_obj:
            response = self.app.get(
                f"/frameworks/{self.framework_id}/questions/{question['id']}?acc_token={self.framework_token}",
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR_QUESTIONS + "answer-question.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                f"/frameworks/{self.framework_id}/questions/{question['id']}?acc_token={self.framework_token}",
                {"data": {"answer": "Таблицю додано в файлі"}},
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR_QUESTIONS + "answer-question-invalid.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                f"/frameworks/{self.framework_id}/questions/{question['id']}",
                {"data": {"answer": "Таблицю додано в файлі"}},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")

        with open(TARGET_DIR_QUESTIONS + "list-questions.http", "w") as self.app.file_obj:
            response = self.app.get(f"/frameworks/{self.framework_id}/questions")
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR_QUESTIONS + "get-answer.http", "w") as self.app.file_obj:
            response = self.app.get(f"/frameworks/{self.framework_id}/questions/{question['id']}")
            self.assertEqual(response.status, "200 OK")

        # Speed up time
        self.tick(delta=timedelta(days=14))

        with open(TARGET_DIR_QUESTIONS + "ask-question-invalid.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                f"/frameworks/{self.framework_id}/questions",
                {"data": test_question_data},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertIn(
                "Question can be add only during the enquiry period",
                response.json["errors"][0]["description"],
            )

        self.tick_delta = None
        self.tick(delta=timedelta(days=5))  # after enquiryPeriod.clarificationsUntil pass
        with open(TARGET_DIR_QUESTIONS + "answer-question-after-clarifications-until.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                f"/frameworks/{self.framework_id}/questions/{question['id']}?acc_token={self.framework_token}",
                {"data": {"answer": "Таблицю додано"}},
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertIn(
                "Allowed to update question only before enquiryPeriod.clarificationsUntil",
                response.json["errors"][0]["description"],
            )
