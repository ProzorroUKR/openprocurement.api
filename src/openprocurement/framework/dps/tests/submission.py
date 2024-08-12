import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.framework.dps.tests.base import (
    SubmissionContentWebTest,
    test_dps_documents,
    test_framework_dps_data,
    test_submission_config,
    test_submission_data,
)
from openprocurement.framework.dps.tests.submission_blanks import (  # Documents
    confidential_submission_document,
    create_submission_after_period_ends,
    create_submission_config_restricted,
    create_submission_config_test,
    create_submission_document_forbidden,
    create_submission_document_json_bulk,
    create_submission_documents,
    create_submission_draft,
    create_submission_draft_invalid,
    date_submission,
    dateModified_submission,
    datePublished_submission,
    document_not_found,
    get_document_by_id,
    get_documents_list,
    get_submission,
    listing,
    listing_changes,
    listing_draft,
    patch_submission_active,
    patch_submission_active_fast,
    patch_submission_complete,
    patch_submission_deleted,
    patch_submission_draft,
    patch_submission_draft_to_active,
    patch_submission_draft_to_active_invalid,
    patch_submission_draft_to_deleted,
    put_submission_document,
    put_submission_document_fast,
    submission_fields,
    submission_not_found,
    submission_token_invalid,
)


class SubmissionResourceTest(SubmissionContentWebTest):
    initial_data = test_framework_dps_data
    initial_submission_data = test_submission_data
    initial_submission_config = test_submission_config
    initial_auth = ('Basic', ('broker', ''))

    test_listing = snitch(listing)
    test_listing_draft = snitch(listing_draft)
    test_listing_changes = snitch(listing_changes)
    test_create_submission_draft_invalid = snitch(create_submission_draft_invalid)
    test_create_submission_draft = snitch(create_submission_draft)
    test_create_submission_config_test = snitch(create_submission_config_test)
    test_create_submission_config_restricted = snitch(create_submission_config_restricted)
    test_create_submission_after_period_ends = snitch(create_submission_after_period_ends)
    test_patch_submission_draft = snitch(patch_submission_draft)
    test_patch_submission_draft_to_active = snitch(patch_submission_draft_to_active)
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


class TestSubmissionDocumentGet(SubmissionContentWebTest):
    initial_data = deepcopy(test_framework_dps_data)
    initial_submission_data = deepcopy(test_submission_data)

    test_get_documents_list = snitch(get_documents_list)
    test_get_document_by_id = snitch(get_document_by_id)

    def setUp(self):
        self.initial_submission_data["documents"] = deepcopy(test_dps_documents)
        for document in self.initial_submission_data["documents"]:
            document["url"] = self.generate_docservice_url()
        super().setUp()


class TestDocumentsCreate(SubmissionContentWebTest):
    initial_data = test_framework_dps_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))

    test_create_submission_document_forbidden = snitch(create_submission_document_forbidden)
    test_create_submission_documents = snitch(create_submission_documents)
    test_create_submission_document_json_bulk = snitch(create_submission_document_json_bulk)
    test_document_not_found = snitch(document_not_found)
    test_put_submission_document = snitch(put_submission_document)
    test_put_submission_document_fast = snitch(put_submission_document_fast)
    test_confidential_submission_document = snitch(confidential_submission_document)


def suite():
    suite = unittest.TestSuite()
    # suite.addTest(unittest.makeSuite(FrameworkTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(SubmissionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestSubmissionDocumentGet))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
