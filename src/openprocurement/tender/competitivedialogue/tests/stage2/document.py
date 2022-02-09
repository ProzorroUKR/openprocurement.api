# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.document import TenderDocumentWithDSResourceTestMixin
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
)
from openprocurement.tender.competitivedialogue.tests.stage1.document_blanks import (
    put_tender_document,
    patch_tender_document,
)


class TenderStage2DocumentWithDSResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))

    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


class TenderStage2UADocumentWithDSResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2DocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UADocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
