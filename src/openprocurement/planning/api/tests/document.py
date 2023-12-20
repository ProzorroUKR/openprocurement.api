# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.planning.api.tests.base import BasePlanWebTest
from openprocurement.planning.api.tests.document_blanks import (
    create_plan_document_json_invalid,
    create_plan_document_json,
    put_plan_document_json,
)


class PlanDocumentWithDSResourceTest(BasePlanWebTest):
    initial_auth = ("Basic", ("broker", ""))

    test_create_plan_document_json_invalid = snitch(create_plan_document_json_invalid)
    test_create_plan_document_json = snitch(create_plan_document_json)
    test_put_plan_document_json = snitch(put_plan_document_json)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PlanDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
