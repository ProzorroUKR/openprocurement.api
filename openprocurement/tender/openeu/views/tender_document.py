# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource


@opresource(name='Tender EU Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU related binary files (PDFs, etc.)")
class TenderEUDocumentResource(TenderUaDocumentResource):
    pass
