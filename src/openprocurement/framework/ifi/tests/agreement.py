import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.framework.dps.tests.agreement_blanks import (
    agreement_chronograph_milestones,
    change_agreement,
    create_agreement,
    create_agreement_config_test,
    create_milestone_document_forbidden,
    create_milestone_document_json_bulk,
    create_milestone_documents,
    get_document_by_id,
    get_documents_list,
    patch_activation_milestone,
    patch_agreement_terminated_status,
    patch_ban_milestone,
    patch_contract_active_status,
    patch_contract_suppliers,
    patch_several_contracts_active_status,
    post_ban_milestone,
    post_ban_milestone_with_documents,
    post_milestone_invalid,
    post_submission_with_active_contract,
    put_milestone_document,
    search_by_classification,
)
from openprocurement.framework.ifi.tests.base import (
    AgreementContentWebTest,
    MilestoneContentWebTest,
    ban_milestone_data_with_documents,
    test_framework_ifi_data,
    test_submission_data,
)
from openprocurement.framework.ifi.tests.qualification import (
    QualificationContentWebTest as BaseQualificationContentWebTest,
)


class QualificationContentWebTest(BaseQualificationContentWebTest):
    def setUp(self):
        super().setUp()
        response = self.app.post_json(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
            {
                "data": {
                    "title": "name name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")


class TestAgreementCreation(QualificationContentWebTest):
    initial_data = test_framework_ifi_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))

    test_create_agreement = snitch(create_agreement)
    test_create_agreement_config_test = snitch(create_agreement_config_test)


class TestAgreementChanges(AgreementContentWebTest):
    initial_data = test_framework_ifi_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))

    test_change_agreement = snitch(change_agreement)
    test_patch_contract_suppliers = snitch(patch_contract_suppliers)
    test_post_submission_with_active_contract = snitch(post_submission_with_active_contract)


class TestAgreementResource(AgreementContentWebTest):
    initial_data = test_framework_ifi_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))

    # Chronograph
    test_agreement_chronograph_milestones = snitch(agreement_chronograph_milestones)
    test_patch_agreement_terminated_status = snitch(patch_agreement_terminated_status)
    test_patch_contract_active_status = snitch(patch_contract_active_status)
    test_patch_several_contracts_active_status = snitch(patch_several_contracts_active_status)


class TestAgreementMilestoneResource(AgreementContentWebTest):
    initial_data = test_framework_ifi_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))

    test_patch_activation_milestone = snitch(patch_activation_milestone)
    test_post_milestone_invalid = snitch(post_milestone_invalid)
    test_post_ban_milestone_with_documents = snitch(post_ban_milestone_with_documents)
    test_post_ban_milestone = snitch(post_ban_milestone)


class TestMilestoneDocumentGet(MilestoneContentWebTest):
    initial_data = test_framework_ifi_data
    initial_submission_data = test_submission_data
    initial_milestone_data = ban_milestone_data_with_documents

    test_get_documents_list = snitch(get_documents_list)
    test_get_document_by_id = snitch(get_document_by_id)

    def setUp(self):
        for document in self.initial_milestone_data["documents"]:
            document["url"] = self.generate_docservice_url()
        super().setUp()


class TestMilestoneCreate(MilestoneContentWebTest):
    initial_data = test_framework_ifi_data
    initial_submission_data = test_submission_data
    initial_milestone_data = ban_milestone_data_with_documents
    initial_auth = ('Basic', ('broker', ''))

    test_patch_ban_milestone = snitch(patch_ban_milestone)
    test_search_by_classification = snitch(search_by_classification)

    test_create_milestone_document_forbidden = snitch(create_milestone_document_forbidden)
    test_create_milestone_documents = snitch(create_milestone_documents)
    test_create_milestone_document_json_bulk = snitch(create_milestone_document_json_bulk)
    test_put_milestone_document = snitch(put_milestone_document)

    def setUp(self):
        for document in self.initial_milestone_data["documents"]:
            document["url"] = self.generate_docservice_url()
        super().setUp()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestAgreementCreation)
    suite.addTest(TestAgreementChanges)
    suite.addTest(TestAgreementMilestoneResource)
    suite.addTest(TestMilestoneDocumentGet)
    suite.addTest(TestMilestoneCreate)


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
