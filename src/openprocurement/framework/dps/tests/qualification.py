# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.framework.dps.tests.base import (
    SubmissionContentWebTest,
    test_framework_dps_data,
    test_submission_data,
)
from openprocurement.framework.dps.tests.qualification_blanks import (
    listing,
    listing_changes,
    patch_submission_pending,
    patch_qualification_active,
    patch_qualification_unsuccessful,
    get_qualification,
    qualification_fields,
    date_qualification,
    dateModified_qualification,
    qualification_not_found,
    qualification_token_invalid,
    # Documents
    get_documents_list,
    get_document_by_id,
    create_qualification_document_forbidden,
    create_qualification_document,
    document_not_found,
    put_qualification_document,
    create_qualification_document_json_bulk,
    patch_submission_pending_config_test,
    patch_submission_pending_config_restricted,
)


class QualificationContentWebTest(SubmissionContentWebTest):
    def setUp(self):
        super(QualificationContentWebTest, self).setUp()
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
            {"data": {"status": "active"}},
        )

        self.qualification_id = response.json["data"]["qualificationID"]


class QualificationResourceTest(SubmissionContentWebTest):
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_patch_submission_pending = snitch(patch_submission_pending)
    test_patch_submission_pending_config_test = snitch(patch_submission_pending_config_test)
    test_patch_submission_pending_config_restricted = snitch(patch_submission_pending_config_restricted)
    test_patch_qualification_active = snitch(patch_qualification_active)
    test_patch_qualification_unsuccessful = snitch(patch_qualification_unsuccessful)
    test_get_qualification = snitch(get_qualification)
    test_qualification_fields = snitch(qualification_fields)

    test_date_qualification = snitch(date_qualification)
    test_dateModified_qualification = snitch(dateModified_qualification)
    test_qualification_not_found = snitch(qualification_not_found)
    test_qualification_token_invalid = snitch(qualification_token_invalid)

    initial_data = test_framework_dps_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))


class TestQualificationDocumentGet(QualificationContentWebTest):
    initial_data = deepcopy(test_framework_dps_data)
    initial_submission_data = deepcopy(test_submission_data)

    test_get_documents_list = snitch(get_documents_list)
    test_get_document_by_id = snitch(get_document_by_id)


class TestQualificationDocumentsCreate(QualificationContentWebTest):
    initial_data = test_framework_dps_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))
    docservice = True

    test_create_qualification_document_forbidden = snitch(create_qualification_document_forbidden)
    test_create_qualification_document = snitch(create_qualification_document)
    test_create_qualification_document_json_bulk = snitch(create_qualification_document_json_bulk)
    test_document_not_found = snitch(document_not_found)
    test_put_qualification_document = snitch(put_qualification_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QualificationResourceTest))
    suite.addTest(unittest.makeSuite(TestQualificationDocumentGet))
    suite.addTest(unittest.makeSuite(TestQualificationDocumentsCreate))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
