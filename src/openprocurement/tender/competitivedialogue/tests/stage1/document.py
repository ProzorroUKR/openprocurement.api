import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUContentWebTest,
    BaseCompetitiveDialogUAContentWebTest,
)
from openprocurement.tender.competitivedialogue.tests.stage1.document_blanks import (
    patch_tender_document,
    put_tender_document,
)


class DialogEUDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_auth = ("Basic", ("broker", ""))

    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


class DialogUADocumentResourceTest(BaseCompetitiveDialogUAContentWebTest, TenderDocumentResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(DialogEUDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(DialogUADocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
