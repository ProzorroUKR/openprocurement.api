# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.document import TenderDocumentResourceTestMixin

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
)
from openprocurement.tender.competitivedialogue.tests.stage1.document_blanks import (
    put_tender_document,
    patch_tender_document,
    create_document_with_the_invalid_document_type,
)

#  _____________________________________________________________________
# |                                                                     |
# |                                                                     |
# |                                                                     |
# |                                 _A_                                 |
# |                         _A_     /"\      _A_                        |
# |                         /"\              /"\                        |
# |                                                                     |
# |                   _A_                         _A_                   |
# |                   /"\                         /"\                   |
# |                                                                     |
# |                                                                     |
# |                 _A_                             _A_                 |
# |                 /"\                             /"\                 |
# |                                                                     |
# |                                                                     |
# |                   _A_                         _A_                   |
# |                   /"\                         /"\                   |
# |                                                                     |
# |                         _A_             _A_                         |
# |                         /"\     _A_     /"\                         |
# |                                 /"\                                 |
# |                                                                     |
# |                                                                     |
# |___________________________________________________________________sm|


class DialogEUDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest, TenderDocumentResourceTestMixin):
    docservice = False

    initial_auth = ("Basic", ("broker", ""))

    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


class DialogEUDocumentWithDSResourceTest(DialogEUDocumentResourceTest):
    docservice = True


class DialogUADocumentResourceTest(BaseCompetitiveDialogUAContentWebTest, TenderDocumentResourceTestMixin):
    docservice = False

    initial_auth = ("Basic", ("broker", ""))

    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)
    test_put_tender_json_document_of_document =snitch(put_tender_json_document_of_document)
    test_create_document_with_the_invalid_document_type = snitch(create_document_with_the_invalid_document_type)

class DialogUADocumentWithDSResourceTest(DialogUADocumentResourceTest):
    docservice = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DialogEUDocumentResourceTest))
    suite.addTest(unittest.makeSuite(DialogEUDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
