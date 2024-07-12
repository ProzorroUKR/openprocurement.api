import csv
import json
import os
from copy import deepcopy
from datetime import timedelta

import standards
from tests.base.constants import DOCS_URL
from tests.base.data import test_docs_tenderer
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.mask import (
    AGREEMENT_MASK_MAPPING,
    QUALIFICATION_MASK_MAPPING,
    SUBMISSION_MASK_MAPPING,
)
from openprocurement.framework.dps.tests.base import (
    BaseFrameworkWebTest,
    test_framework_dps_data,
)

TARGET_DIR_RESTRICTED = 'docs/source/frameworks/config/http/restricted/'
TARGET_CSV_DIR_RESTRICTED = 'docs/source/frameworks/config/csv/restricted/'
TARGET_CSV_DIR = 'docs/source/frameworks/config/csv/'

test_framework_open_data = deepcopy(test_framework_dps_data)


class FrameworkConfigCSVMixin:
    def get_config_possible_values(self, config_schema):
        separator = ","
        empty = ""
        if "enum" in config_schema:
            config_values_enum = config_schema.get("enum", "")
            config_values = separator.join(map(json.dumps, config_values_enum))
            return config_values
        elif "minimum" in config_schema and "maximum" in config_schema:
            config_values_min = config_schema.get("minimum", "")
            config_values_max = config_schema.get("maximum", "")
            if config_values_min == config_values_max:
                return config_values_min
            else:
                return f'{config_values_min} - {config_values_max}'
        else:
            return empty

    def get_config_row(self, name, config_schema):
        row = [name, self.get_config_possible_values(config_schema)]
        config_default = config_schema.get("default", "")
        row.append(json.dumps(config_default))
        return row

    def write_config_values_csv(self, config_name, file_path):
        framework_types = [
            "dynamicPurchasingSystem",
            "electronicCatalogue",
        ]

        headers = [
            "frameworkType",
            "values",
            "default",
        ]

        rows = []

        for framework_type in framework_types:
            schema = standards.load(f"data_model/schema/FrameworkConfig/{framework_type}.json")
            config_schema = schema["properties"][config_name]
            row = self.get_config_row(framework_type, config_schema)
            rows.append(row)

        with open(file_path, 'w', newline='') as file_csv:
            writer = csv.writer(file_csv, lineterminator='\n')
            writer.writerow(headers)
            writer.writerows(rows)

    @staticmethod
    def write_config_mask_csv(mapping, file_path):
        headers = [
            "path",
            "value",
        ]

        rows = []

        for path, rule in mapping.items():
            rows.append([path, rule["value"]])

        with open(file_path, 'w', newline='') as file_csv:
            writer = csv.writer(file_csv, lineterminator='\n')
            writer.writerow(headers)
            writer.writerows(rows)


class FrameworkConfigBaseResouceTest(BaseFrameworkWebTest, MockWebTestMixin, FrameworkConfigCSVMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    initial_data = test_framework_open_data
    docservice_url = DOCS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def create_framework(self):
        pass

    def test_docs_restricted_submission_mask_mapping_csv(self):
        self.write_config_mask_csv(
            mapping=SUBMISSION_MASK_MAPPING,
            file_path=TARGET_CSV_DIR_RESTRICTED + "submission-mask-mapping.csv",
        )

    def test_docs_restricted_qualification_mask_mapping_csv(self):
        self.write_config_mask_csv(
            mapping=QUALIFICATION_MASK_MAPPING,
            file_path=TARGET_CSV_DIR_RESTRICTED + "qualification-mask-mapping.csv",
        )

    def test_docs_restricted_agreement_mask_mapping_csv(self):
        self.write_config_mask_csv(
            mapping=AGREEMENT_MASK_MAPPING,
            file_path=TARGET_CSV_DIR_RESTRICTED + "agreement-mask-mapping.csv",
        )


class RestrictedFrameworkOpenResourceTest(FrameworkConfigBaseResouceTest):
    def test_docs(self):
        # empty frameworks listing
        data = deepcopy(self.initial_data)
        data["qualificationPeriod"]["endDate"] = (get_now() + timedelta(days=60)).isoformat()
        data["procuringEntity"]["kind"] = "defense"
        response = self.app.get('/frameworks')
        self.assertEqual(response.json['data'], [])

        # create frameworks
        with change_auth(self.app, ("Basic", ("brokerr", ""))):
            with open(TARGET_DIR_RESTRICTED + 'framework-create-broker.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/frameworks',
                    {
                        'data': data,
                        'config': {
                            'restrictedDerivatives': True,
                            'clarificationUntilDuration': 3,
                        },
                    },
                )
                self.assertEqual(response.status, '201 Created')

            framework = response.json['data']
            self.framework_id = framework["id"]
            owner_token = response.json['access']['token']

            with open(TARGET_DIR_RESTRICTED + 'framework-activate-broker.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/frameworks/{}?acc_token={}'.format(framework['id'], owner_token), {'data': {"status": "active"}}
                )
                self.assertEqual(response.status, '200 OK')

        # Submissions

        # Create by Broker
        with change_auth(self.app, ("Basic", ("brokerr", ""))):
            with open(TARGET_DIR_RESTRICTED + 'submission-register-broker.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/submissions',
                    {
                        'data': {
                            "tenderers": [test_docs_tenderer],
                            "frameworkID": self.framework_id,
                        },
                        'config': {
                            'restricted': True,
                        },
                    },
                )
                self.assertEqual(response.status, '201 Created')

        self.submission1_id = response.json["data"]["id"]
        self.submission1_token = response.json["access"]["token"]

        # Add Submission document
        with change_auth(self.app, ("Basic", ("brokerr", ""))):
            response = self.app.post_json(
                '/submissions/{}/documents?acc_token={}'.format(self.submission1_id, self.submission1_token),
                {
                    "data": {
                        "title": "укр.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
                status=201,
            )

        # Activate Submission
        with change_auth(self.app, ("Basic", ("brokerr", ""))):
            with open(TARGET_DIR_RESTRICTED + 'submission-activate-broker.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/submissions/{}?acc_token={}'.format(self.submission1_id, self.submission1_token),
                    {'data': {"status": "active"}},
                )
                self.assertEqual(response.status, '200 OK')

            self.qualification1_id = response.json["data"]["qualificationID"]

        # Check by Broker, can see submissions
        with change_auth(self.app, ("Basic", ("brokerr", ""))):
            with open(TARGET_DIR_RESTRICTED + 'submission-feed-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions?opt_fields=frameworkID,status,documents')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR_RESTRICTED + 'submission-get-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission1_id))
                self.assertEqual(response.status, '200 OK')

        # Check by Anonymous
        with change_auth(self.app, None):
            with open(TARGET_DIR_RESTRICTED + 'submission-feed-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions?opt_fields=frameworkID,status,documents')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR_RESTRICTED + 'submission-get-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission1_id))
                self.assertEqual(response.status, '200 OK')

        # Qualification

        # Add Qualification document
        with change_auth(self.app, ("Basic", ("brokerr", ""))):
            response = self.app.post_json(
                '/qualifications/{}/documents?acc_token={}'.format(self.qualification1_id, owner_token),
                {
                    "data": {
                        "title": "укр.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
                status=201,
            )

        # Check by Broker, can see qualifications
        with change_auth(self.app, ("Basic", ("brokerr", ""))):
            with open(TARGET_DIR_RESTRICTED + 'qualification-feed-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications?opt_fields=frameworkID,status,documents')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR_RESTRICTED + 'qualification-get-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification1_id))
                self.assertEqual(response.status, '200 OK')

        # Check by Anonymous
        with change_auth(self.app, None):
            with open(TARGET_DIR_RESTRICTED + 'qualification-feed-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications?opt_fields=frameworkID,status,documents')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR_RESTRICTED + 'qualification-get-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification1_id))
                self.assertEqual(response.status, '200 OK')

        # Activate Qualifications
        with change_auth(self.app, ("Basic", ("brokerr", ""))):
            response = self.app.post_json(
                '/qualifications/{}/documents?acc_token={}'.format(self.qualification1_id, owner_token),
                {
                    "data": {
                        "title": "sign.p7s",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pkcs7-signature",
                        "documentType": "evaluationReports",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
            with open(TARGET_DIR_RESTRICTED + 'qualification-activate-broker.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/qualifications/{}?acc_token={}'.format(self.qualification1_id, owner_token),
                    {'data': {"status": "active"}},
                )
                self.assertEqual(response.status, '200 OK')

        # Agreement

        with change_auth(self.app, None):
            with open(TARGET_DIR_RESTRICTED + 'framework-with-agreement.http', 'w') as self.app.file_obj:
                response = self.app.get(f'/frameworks/{self.framework_id}')
                self.assertEqual(response.status, '200 OK')
                self.agreement_id = response.json["data"]["agreementID"]

        # Check by Broker
        with change_auth(self.app, ("Basic", ("brokerr", ""))):
            with open(TARGET_DIR_RESTRICTED + 'agreement-feed-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements?opt_fields=status,procuringEntity')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR_RESTRICTED + 'agreement-get-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements/{}'.format(self.agreement_id))
                self.assertEqual(response.status, '200 OK')

        # Check by Anonymous
        with change_auth(self.app, None):
            with open(TARGET_DIR_RESTRICTED + 'agreement-feed-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements?opt_fields=status,procuringEntity')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR_RESTRICTED + 'agreement-get-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements/{}'.format(self.agreement_id))
                self.assertEqual(response.status, '200 OK')


class FrameworkClarificationUntilDurationResourceTest(FrameworkConfigBaseResouceTest):
    def test_docs_clarification_until_duration_values_csv(self):
        self.write_config_values_csv(
            config_name="clarificationUntilDuration",
            file_path=TARGET_CSV_DIR + "clarification-until-duration-values.csv",
        )
