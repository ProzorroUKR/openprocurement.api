import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.framework.dps.tests.base import (
    BaseDSFrameworkContentWebTest,
    FrameworkContentWebTest,
    test_dps_documents,
    test_framework_dps_data,
)
from openprocurement.framework.dps.tests.document_blanks import (
    create_framework_document,
    create_framework_document_forbidden,
    create_framework_document_json_bulk,
    get_document_by_id,
    get_documents_list,
    not_found,
    put_contract_document,
)


class TestDocumentGet(FrameworkContentWebTest):
    initial_data = deepcopy(test_framework_dps_data)

    def setUp(self):
        self.initial_data["documents"] = deepcopy(test_dps_documents)
        for document in self.initial_data["documents"]:
            document["url"] = self.generate_docservice_url()
        super().setUp()

    test_get_documents_list = snitch(get_documents_list)
    test_get_document_by_id = snitch(get_document_by_id)


class TestDocumentsCreate(BaseDSFrameworkContentWebTest):
    initial_data = test_framework_dps_data
    initial_auth = ("Basic", ("broker", ""))

    test_create_framework_document_forbidden = snitch(create_framework_document_forbidden)
    test_create_framework_document = snitch(create_framework_document)
    test_create_framework_document_json_bulk = snitch(create_framework_document_json_bulk)


class OpenDocumentWithDSResourceTest(BaseDSFrameworkContentWebTest):
    initial_data = test_framework_dps_data

    test_not_found = snitch(not_found)
    test_put_contract_document = snitch(put_contract_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestDocumentGet))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestDocumentsCreate))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(OpenDocumentWithDSResourceTest))
    return suite
