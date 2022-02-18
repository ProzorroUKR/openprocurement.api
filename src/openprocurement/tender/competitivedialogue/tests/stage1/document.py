# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.document import TenderDocumentWithDSResourceTestMixin

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
)
from openprocurement.tender.competitivedialogue.tests.stage1.document_blanks import (
    put_tender_document,
    patch_tender_document,
)


class DialogEUDocumentWithDSResourceTest(BaseCompetitiveDialogEUContentWebTest):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))

    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


class DialogUADocumentWithDSResourceTest(BaseCompetitiveDialogUAContentWebTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DialogEUDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(DialogUADocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
