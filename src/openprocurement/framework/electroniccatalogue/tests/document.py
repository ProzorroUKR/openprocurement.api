# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.framework.electroniccatalogue.tests.base import (
    test_framework_electronic_catalogue_data,
    test_electronicCatalogue_documents,
    FrameworkContentWebTest,
    BaseDSFrameworkContentWebTest,
)
from openprocurement.framework.dps.tests.document_blanks import (
    get_documents_list,
    get_document_by_id,
    create_framework_document_forbidden,
    create_framework_document,
    not_found,
    put_contract_document,
    create_framework_document_json_bulk,
)


class TestDocumentGet(FrameworkContentWebTest):
    initial_data = deepcopy(test_framework_electronic_catalogue_data)

    def setUp(self):
        self.initial_data["documents"] = deepcopy(test_electronicCatalogue_documents)
        for document in self.initial_data["documents"]:
            document["url"] = self.generate_docservice_url()
        super(TestDocumentGet, self).setUp()

    test_get_documents_list = snitch(get_documents_list)
    test_get_document_by_id = snitch(get_document_by_id)


class TestDocumentsCreate(BaseDSFrameworkContentWebTest):
    initial_data = test_framework_electronic_catalogue_data
    initial_auth = ("Basic", ("broker", ""))

    test_create_framework_document_forbidden = snitch(create_framework_document_forbidden)
    test_create_framework_document = snitch(create_framework_document)
    test_create_framework_document_json_bulk = snitch(create_framework_document_json_bulk)


class ElectronicCatalogueDocumentWithDSResourceTest(BaseDSFrameworkContentWebTest):
    initial_data = test_framework_electronic_catalogue_data

    test_not_found = snitch(not_found)
    test_put_contract_document = snitch(put_contract_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocumentGet))
    suite.addTest(unittest.makeSuite(TestDocumentsCreate))
    suite.addTest(unittest.makeSuite(ElectronicCatalogueDocumentWithDSResourceTest))
    return suite
