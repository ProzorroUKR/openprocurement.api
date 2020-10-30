# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
    create_tender_contract_proforma_document_json_invalid,
    create_tender_contract_proforma_document_json,
    create_tender_documents_by_registry_bot,
    create_tender_documents_by_registry_bot_invalid,
    create_tender_contract_data_document_json,
    upload_tender_document_by_renderer_bot,
    patch_tender_contract_proforma_document_invalid,
    put_tender_contract_proforma_document,
)


from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
)
from openprocurement.tender.competitivedialogue.tests.stage1.document_blanks import (
    put_tender_document,
    patch_tender_document,
    create_document_with_the_invalid_document_type,
    put_tender_json_document_of_document,
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


class TenderStage2EUDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderDocumentResourceTestMixin):

    docservice = False
    initial_auth = ("Basic", ("broker", ""))

    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)
    test_create_document_with_the_invalid_document_type = snitch(create_document_with_the_invalid_document_type)

class TenderStage2DocumentWithDSResourceTest(TenderStage2EUDocumentResourceTest, TenderDocumentResourceTestMixin):
    docservice = True

    test_create_tender_contract_proforma_document_json_invalid = \
        snitch(create_tender_contract_proforma_document_json_invalid)
    test_create_tender_contract_proforma_document_json = snitch(create_tender_contract_proforma_document_json)
    test_create_tender_documents_by_registry_bot = snitch(create_tender_documents_by_registry_bot)
    test_create_tender_documents_by_registry_bot_invalid = snitch(create_tender_documents_by_registry_bot_invalid)
    test_create_tender_contract_data_document_json = snitch(create_tender_contract_data_document_json)
    test_upload_tender_document_by_renderer_bot = snitch(upload_tender_document_by_renderer_bot)
    test_patch_tender_contract_proforma_document_invalid = snitch(patch_tender_contract_proforma_document_invalid)
    test_put_tender_contract_proforma_document = snitch(put_tender_contract_proforma_document)


##########
#  UA
##########


class TenderStage2UADocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderDocumentResourceTestMixin):

    docservice = False

    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)
    test_put_tender_json_document_of_document = snitch(put_tender_json_document_of_document)

class TenderStage2UADocumentWithDSResourceTest(TenderStage2UADocumentResourceTest, TenderDocumentResourceTestMixin):
    docservice = True

    test_create_tender_contract_proforma_document_json_invalid = \
        snitch(create_tender_contract_proforma_document_json_invalid)
    test_create_tender_contract_proforma_document_json = snitch(create_tender_contract_proforma_document_json)
    test_create_tender_documents_by_registry_bot = snitch(create_tender_documents_by_registry_bot)
    test_create_tender_documents_by_registry_bot_invalid = snitch(create_tender_documents_by_registry_bot_invalid)
    test_create_tender_contract_data_document_json = snitch(create_tender_contract_data_document_json)
    test_upload_tender_document_by_renderer_bot = snitch(upload_tender_document_by_renderer_bot)
    test_patch_tender_contract_proforma_document_invalid = snitch(patch_tender_contract_proforma_document_invalid)
    test_put_tender_contract_proforma_document = snitch(put_tender_contract_proforma_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2DocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UADocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UADocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
