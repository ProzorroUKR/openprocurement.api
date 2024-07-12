import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.framework.dps.tests.document_blanks import (
    create_framework_document,
    create_framework_document_forbidden,
    create_framework_document_json_bulk,
    get_document_by_id,
    get_documents_list,
    not_found,
    put_contract_document,
)
from openprocurement.framework.electroniccatalogue.tests.base import (
    FrameworkContentWebTest,
    test_electronicCatalogue_documents,
    test_framework_electronic_catalogue_config,
    test_framework_electronic_catalogue_data,
)


class DocumentGetTest(FrameworkContentWebTest):
    initial_data = deepcopy(test_framework_electronic_catalogue_data)
    initial_config = test_framework_electronic_catalogue_config

    def setUp(self):
        self.initial_data["documents"] = deepcopy(test_electronicCatalogue_documents)
        for document in self.initial_data["documents"]:
            document["url"] = self.generate_docservice_url()
        super().setUp()

    test_get_documents_list = snitch(get_documents_list)
    test_get_document_by_id = snitch(get_document_by_id)


class DocumentsCreateTest(FrameworkContentWebTest):
    initial_data = test_framework_electronic_catalogue_data
    initial_config = test_framework_electronic_catalogue_config
    initial_auth = ("Basic", ("broker", ""))

    test_create_framework_document_forbidden = snitch(create_framework_document_forbidden)
    test_create_framework_document = snitch(create_framework_document)
    test_create_framework_document_json_bulk = snitch(create_framework_document_json_bulk)
    test_not_found = snitch(not_found)
    test_put_contract_document = snitch(put_contract_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(DocumentGetTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(DocumentsCreateTest))
    return suite
