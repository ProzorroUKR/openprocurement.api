# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.framework.electroniccatalogue.tests.base import (
    BaseSubmissionContentWebTest,
    SubmissionContentWebTest,
    test_framework_electronic_catalogue_data,
    test_electronicCatalogue_documents,
    test_submission_data,
)
from openprocurement.framework.dps.tests.submission_blanks import (
    listing,
    listing_draft,
    listing_changes,
    create_submission_draft_invalid,
    create_submission_draft,
    patch_submission_draft,
    patch_submission_draft_to_active_invalid,
    patch_submission_active,
    patch_submission_active_fast,
    patch_submission_draft_to_deleted,
    patch_submission_deleted,
    patch_submission_complete,
    submission_fields,
    get_submission,
    date_submission,
    dateModified_submission,
    datePublished_submission,
    submission_not_found,
    submission_token_invalid,
    # Documents
    get_documents_list,
    get_document_by_id,
    create_submission_documents,
    create_submission_document_forbidden,
    document_not_found,
    put_submission_document,
    put_submission_document_fast,
    create_submission_document_json_bulk,
    create_submission_config_test,
)


class SubmissionResourceTest(BaseSubmissionContentWebTest):
    test_listing = snitch(listing)
    test_listing_draft = snitch(listing_draft)
    test_listing_changes = snitch(listing_changes)
    test_create_submission_draft_invalid = snitch(create_submission_draft_invalid)
    test_create_submission_draft = snitch(create_submission_draft)
    test_create_submission_config_test = snitch(create_submission_config_test)
    test_patch_submission_draft = snitch(patch_submission_draft)
    test_patch_submission_draft_to_active_invalid = snitch(patch_submission_draft_to_active_invalid)
    test_patch_submission_active = snitch(patch_submission_active)
    test_patch_submission_active_fast = snitch(patch_submission_active_fast)
    test_patch_submission_draft_to_deleted = snitch(patch_submission_draft_to_deleted)
    test_patch_submission_deleted = snitch(patch_submission_deleted)
    test_patch_submission_complete = snitch(patch_submission_complete)
    test_submission_fields = snitch(submission_fields)
    test_get_submission = snitch(get_submission)

    test_date_submission = snitch(date_submission)
    test_dateModified_submission = snitch(dateModified_submission)
    test_datePublished_submission = snitch(datePublished_submission)
    test_submission_not_found = snitch(submission_not_found)
    test_submission_token_invalid = snitch(submission_token_invalid)

    initial_data = test_framework_electronic_catalogue_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))


class TestSubmissionDocumentGet(SubmissionContentWebTest):
    initial_data = deepcopy(test_framework_electronic_catalogue_data)
    initial_submission_data = deepcopy(test_submission_data)

    test_get_documents_list = snitch(get_documents_list)
    test_get_document_by_id = snitch(get_document_by_id)

    def setUp(self):
        self.initial_submission_data["documents"] = deepcopy(test_electronicCatalogue_documents)
        for document in self.initial_submission_data["documents"]:
            document["url"] = self.generate_docservice_url()
        super(TestSubmissionDocumentGet, self).setUp()


class TestDocumentsCreate(SubmissionContentWebTest):
    initial_data = test_framework_electronic_catalogue_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))
    docservice = True

    test_create_submission_document_forbidden = snitch(create_submission_document_forbidden)
    test_create_submission_documents = snitch(create_submission_documents)
    test_create_submission_document_json_bulk = snitch(create_submission_document_json_bulk)
    test_document_not_found = snitch(document_not_found)
    test_put_submission_document = snitch(put_submission_document)
    test_put_submission_document_fast = snitch(put_submission_document_fast)


def suite():
    suite = unittest.TestSuite()
    # suite.addTest(unittest.makeSuite(FrameworkTest))
    suite.addTest(unittest.makeSuite(SubmissionResourceTest))
    suite.addTest(unittest.makeSuite(TestSubmissionDocumentGet))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
