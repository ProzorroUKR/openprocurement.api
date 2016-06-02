# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource


@opresource(name='Competitive Dialogue EU Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Tender EU related binary files (PDFs, etc.)")
class CompetitiveDialogueEUDocumentResource(TenderUaDocumentResource):
    pass


@opresource(name='Competitive Dialogue UA Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Competitive Dialogue UA related binary files (PDFs, etc.)")
class CompetitiveDialogueUADocumentResource(TenderUaDocumentResource):
    pass

