# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.tender_document import (
    TenderUaDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@optendersresource(name='{}:Tender Documents'.format(CD_EU_TYPE),
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType=CD_EU_TYPE,
                   description="Tender EU related binary files (PDFs, etc.)")
class CompetitiveDialogueEUDocumentResource(TenderUaDocumentResource):
    pass


@optendersresource(name='{}:Tender Documents'.format(CD_UA_TYPE),
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType=CD_UA_TYPE,
                   description="Competitive Dialogue UA related binary files (PDFs, etc.)")
class CompetitiveDialogueUADocumentResource(TenderUaDocumentResource):
    pass
