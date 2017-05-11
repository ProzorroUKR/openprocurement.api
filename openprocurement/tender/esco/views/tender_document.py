# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource as TenderUADocumentResource
from openprocurement.tender.openeu.views.tender_document import TenderEUDocumentResource


@optendersresource(name='Tender ESCO UA Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA related binary files (PDFs, etc.)")
class TenderESCOUADocumentResource(TenderUADocumentResource):
    """ Tender ESCO UA Document Resource """


@optendersresource(name='Tender ESCO EU Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU related binary files (PDFs, etc.)")
class TenderESCOEUDocumentResource(TenderEUDocumentResource):
    """ Tender ESCO EU Document Resource """
