# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.tender_document import TenderEUDocumentResource


@optendersresource(name='esco.EU:Tender Documents',
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType='esco.EU',
                   description="Tender ESCO EU related binary files (PDFs, etc.)")
class TenderESCOEUDocumentResource(TenderEUDocumentResource):
    """ Tender ESCO EU Document Resource """
