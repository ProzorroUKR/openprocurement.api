import unittest
from copy import deepcopy
from unittest.mock import patch

from openprocurement.api.constants import FRAMEWORK_CONFIG_JSONSCHEMAS
from openprocurement.api.tests.base import snitch
from openprocurement.framework.dps.tests.qualification_blanks import (  # Documents
    activate_qualification_for_submission_with_docs,
    active_qualification_changes_atomic,
    create_qualification_document,
    create_qualification_document_forbidden,
    create_qualification_document_json_bulk,
    date_qualification,
    dateModified_qualification,
    document_not_found,
    get_document_by_id,
    get_documents_list,
    get_qualification,
    listing,
    listing_changes,
    patch_qualification_active,
    patch_qualification_active_mock,
    patch_qualification_unsuccessful,
    patch_submission_pending,
    put_qualification_document,
    qualification_evaluation_reports_documents,
    qualification_fields,
    qualification_not_found,
    qualification_token_invalid,
)
from openprocurement.framework.ifi.tests.base import (
    SubmissionContentWebTest,
    test_framework_ifi_config,
    test_framework_ifi_data,
    test_submission_config,
    test_submission_data,
)

test_mocked_framework_ifi_config = deepcopy(test_framework_ifi_config)
test_mocked_framework_ifi_config["qualificationComplainDuration"] = 5


class QualificationContentWebTest(SubmissionContentWebTest):
    def setUp(self):
        super().setUp()
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
            {"data": {"status": "active"}},
        )

        self.qualification_id = response.json["data"]["qualificationID"]


class QualificationResourceTest(SubmissionContentWebTest):
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_patch_submission_pending = snitch(patch_submission_pending)
    test_patch_qualification_active = snitch(patch_qualification_active)
    test_activate_qualification_for_submission_with_docs = snitch(activate_qualification_for_submission_with_docs)
    test_patch_qualification_unsuccessful = snitch(patch_qualification_unsuccessful)
    test_get_qualification = snitch(get_qualification)
    test_qualification_fields = snitch(qualification_fields)
    test_active_qualification_changes_atomic = snitch(active_qualification_changes_atomic)
    test_qualification_evaluation_reports_documents = snitch(qualification_evaluation_reports_documents)

    test_date_qualification = snitch(date_qualification)
    test_dateModified_qualification = snitch(dateModified_qualification)
    test_qualification_not_found = snitch(qualification_not_found)
    test_qualification_token_invalid = snitch(qualification_token_invalid)

    initial_data = test_framework_ifi_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))


class TestMockedQualificationResourceTest(QualificationContentWebTest):
    initial_submission_config = test_submission_config
    initial_submission_data = test_submission_data
    initial_data = test_framework_ifi_data
    initial_config = test_mocked_framework_ifi_config
    docservice = True

    def setUp(self):
        patched_schema_properties = {
            "qualificationComplainDuration": {
                'type': 'integer',
                'minimum': 5,
                'maximum': 5,
                'default': 5,
            }
        }

        def patched_schemas_get(key):
            schema = deepcopy(FRAMEWORK_CONFIG_JSONSCHEMAS[key])
            schema["properties"].update(patched_schema_properties)
            return schema

        patch_path = 'openprocurement.framework.core.procedure.state.framework.FRAMEWORK_CONFIG_JSONSCHEMAS'
        with patch(patch_path) as patched_schemas:
            patched_schemas.get = patched_schemas_get

            super().setUp()

    test_patch_qualification_active_mock = snitch(patch_qualification_active_mock)


class TestQualificationDocumentGet(QualificationContentWebTest):
    initial_data = deepcopy(test_framework_ifi_data)
    initial_submission_data = deepcopy(test_submission_data)

    test_get_documents_list = snitch(get_documents_list)
    test_get_document_by_id = snitch(get_document_by_id)


class TestQualificationDocumentsCreate(QualificationContentWebTest):
    initial_data = test_framework_ifi_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))

    test_create_qualification_document_forbidden = snitch(create_qualification_document_forbidden)
    test_create_qualification_document = snitch(create_qualification_document)
    test_create_qualification_document_json_bulk = snitch(create_qualification_document_json_bulk)
    test_document_not_found = snitch(document_not_found)
    test_put_qualification_document = snitch(put_qualification_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(QualificationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestQualificationDocumentGet))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestQualificationDocumentsCreate))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
