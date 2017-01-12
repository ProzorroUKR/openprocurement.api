# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource as TenderUADocumentResource
from openprocurement.tender.openeu.views.tender_document import TenderEUDocumentResource
from openprocurement.tender.limited.views.tender_document import TenderDocumentResource as TenderReportingDocumentResource


@opresource(name='Tender ESCO UA Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA related binary files (PDFs, etc.)")
class TenderESCOUADocumentResource(TenderUADocumentResource):
    """ Tender ESCO UA Document Resource """


@opresource(name='Tender ESCO EU Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU related binary files (PDFs, etc.)")
class TenderESCOEUDocumentResource(TenderEUDocumentResource):
    """ Tender ESCO EU Document Resource """


@opresource(name='Tender ESCO Reporting Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='esco.reporting',
            description="Tender ESCO Reporting related binary files (PDFs, etc.)")
class TenderESCOReportingDocumentResource(TenderReportingDocumentResource):
    """ Tender ESCO Reporting Document Resource """
