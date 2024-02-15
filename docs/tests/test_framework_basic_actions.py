# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from tests.base.constants import DOCS_URL
from tests.base.data import test_docs_tenderer
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.framework.dps.tests.base import (
    BaseFrameworkWebTest,
    test_framework_dps_config,
    test_framework_dps_data,
    test_question_data,
)

TARGET_DIR_QUESTIONS = 'docs/source/frameworks/basic-actions/http/questions/'

test_framework_open_data = deepcopy(test_framework_dps_data)
test_framework_open_config = deepcopy(test_framework_dps_config)


class QuestionsFrameworkOpenResourceTest(BaseFrameworkWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    initial_data = test_framework_open_data
    freezing_datetime = '2023-01-01T00:00:00+02:00'
    docservice = True
    docservice_url = DOCS_URL

    def setUp(self):
        super(QuestionsFrameworkOpenResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(QuestionsFrameworkOpenResourceTest, self).tearDown()

    def create_framework(self):
        pass

    def test_docs(self):
        self.app.authorization = ('Basic', ('broker', ''))

        # empty frameworks listing
        data = deepcopy(self.initial_data)
        data["qualificationPeriod"]["endDate"] = (get_now() + timedelta(days=60)).isoformat()
        response = self.app.get('/frameworks')
        self.assertEqual(response.json['data'], [])

        # create frameworks
        response = self.app.post_json('/frameworks', {'data': data, 'config': test_framework_open_config})
        self.assertEqual(response.status, '201 Created')

        framework = response.json['data']
        self.framework_id = framework["id"]
        owner_token = response.json['access']['token']

        response = self.app.patch_json(
            '/frameworks/{}?acc_token={}'.format(framework['id'], owner_token), {'data': {"status": "active"}}
        )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_QUESTIONS + 'get-framework.http', 'w') as self.app.file_obj:
            response = self.app.get('/frameworks/{}'.format(framework['id']))
            self.assertEqual(response.status, '200 OK')

        # Questions

        with open(TARGET_DIR_QUESTIONS + 'ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(f"/frameworks/{framework['id']}/questions", {'data': test_question_data})
            self.assertEqual(response.status, '201 Created')
            question = response.json["data"]

        with open(TARGET_DIR_QUESTIONS + 'answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f"/frameworks/{framework['id']}/questions/{question['id']}?acc_token={owner_token}",
                {'data': {"answer": "Таблицю додано в файлі"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_QUESTIONS + 'answer-question-invalid.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f"/frameworks/{framework['id']}/questions/{question['id']}",
                {'data': {"answer": "Таблицю додано в файлі"}},
                status=403,
            )
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR_QUESTIONS + 'list-questions.http', 'w') as self.app.file_obj:
            response = self.app.get(f"/frameworks/{framework['id']}/questions")
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_QUESTIONS + 'get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get(f"/frameworks/{framework['id']}/questions/{question['id']}")
            self.assertEqual(response.status, '200 OK')

        # Speed up time
        self.tick(delta=timedelta(days=14))

        with open(TARGET_DIR_QUESTIONS + 'ask-question-invalid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f"/frameworks/{framework['id']}/questions",
                {'data': test_question_data},
                status=403,
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertIn(
                "Question can be add only during the enquiry period",
                response.json["errors"][0]["description"],
            )

        self.tick_delta = None
        self.tick(delta=timedelta(days=5))  # after enquiryPeriod.clarificationsUntil pass
        with open(TARGET_DIR_QUESTIONS + 'answer-question-after-clarifications-until.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f"/frameworks/{framework['id']}/questions/{question['id']}?acc_token={owner_token}",
                {'data': {"answer": "Таблицю додано"}},
                status=403,
            )
            self.assertEqual(response.status, '403 Forbidden')
            self.assertIn(
                "Allowed to update question only before enquiryPeriod.clarificationsUntil",
                response.json["errors"][0]["description"],
            )
