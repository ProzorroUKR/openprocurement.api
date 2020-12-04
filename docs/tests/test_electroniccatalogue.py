# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from iso8601 import parse_date
from tests.base.constants import DOCS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

from openprocurement.framework.electroniccatalogue.tests.base import (
    test_electronicCatalogue_data,
    BaseelEctronicCatalogueWebTest,
)

TARGET_DIR = 'docs/source/frameworks/electroniccatalogue/tutorial/'

test_electronicCatalogue_data = deepcopy(test_electronicCatalogue_data)


class EctronicCatalogueResourceTest(BaseelEctronicCatalogueWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_electronicCatalogue_data
    docservice = True
    docservice_url = DOCS_URL

    def setUp(self):
        super(EctronicCatalogueResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(EctronicCatalogueResourceTest, self).tearDown()

    def create_framework(self):
        pass

    def test_docs(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # empty frameworks listing
        response = self.app.get('/frameworks')
        self.assertEqual(response.json['data'], [])

        # create frameworks
        with open(TARGET_DIR + 'create-electroniccatalogue.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/frameworks', {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')

        framework = response.json['data']
        self.framework_id = framework["id"]
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'patch-electroniccatalogue-draft.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/frameworks/{}?acc_token={}'.format(framework['id'], owner_token),
                {'data': {
                    "procuringEntity": {
                        "contactPoint": {
                            "telephone": "0440000001"
                        }
                    },
                    "title": "updated in draft status"
                }}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'patch-electroniccatalogue-draft-to-active.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/frameworks/{}?acc_token={}'.format(framework['id'], owner_token), {'data': {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-framework.http', 'w') as self.app.file_obj:
            response = self.app.get('/frameworks/{}'.format(framework['id']))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'framework-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/frameworks'.format(framework['id']))
            self.assertEqual(len(response.json['data']), 1)

        with open(TARGET_DIR + 'patch-electroniccatalogue-active.http', 'w') as self.app.file_obj:
            new_endDate = (parse_date(framework["qualificationPeriod"]["endDate"]) + timedelta(days=15)).isoformat()
            response = self.app.patch_json(
                '/frameworks/{}?acc_token={}'.format(framework['id'], owner_token),
                {'data': {
                    "qualificationPeriod": {
                        "endDate": new_endDate
                    },
                    "description": "updated in active status"
                }}
            )
            self.assertEqual(response.status, '200 OK')
