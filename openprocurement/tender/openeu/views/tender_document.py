# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource
LOGGER = getLogger(__name__)


@opresource(name='Tender EU Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU related binary files (PDFs, etc.)")
class TenderEUDocumentResource(TenderUaDocumentResource):
    pass