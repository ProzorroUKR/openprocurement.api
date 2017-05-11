# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.tender_document import TenderEUDocumentResource


@opresource(name='Tender ESCO EU Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU related binary files (PDFs, etc.)")
class TenderESCOEUDocumentResource(TenderEUDocumentResource):
    """ Tender ESCO EU Document Resource """
