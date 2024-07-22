import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cd_lots,
)
from openprocurement.tender.competitivedialogue.tests.stage1.document_blanks import (
    patch_tender_document,
    put_tender_document,
)


class TenderStage2DocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderDocumentResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_lots = test_tender_cd_lots

    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


class TenderStage2UADocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderDocumentResourceTestMixin):
    initial_lots = test_tender_cd_lots

    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2DocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderStage2UADocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
