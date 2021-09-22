# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.planning.api.tests.base import BasePlanWebTest
from openprocurement.planning.api.tests.document_blanks import (
    not_found,
    create_plan_document,
    put_plan_document,
    patch_plan_document,
    create_plan_document_json_invalid,
    create_plan_document_json,
    put_plan_document_json,
)


class PlanDocumentResourceTest(BasePlanWebTest):
    test_not_found = snitch(not_found)
    test_create_plan_document = snitch(create_plan_document)
    test_put_plan_document = snitch(put_plan_document)
    test_patch_plan_document = snitch(patch_plan_document)


class PlanDocumentWithDSResourceTest(PlanDocumentResourceTest):
    test_create_plan_document_json_invalid = snitch(create_plan_document_json_invalid)
    test_create_plan_document_json = snitch(create_plan_document_json)
    test_put_plan_document_json = snitch(put_plan_document_json)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PlanDocumentResourceTest))
    suite.addTest(unittest.makeSuite(PlanDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
