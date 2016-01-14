# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.api.views.tender_document import TenderDocumentResource


LOGGER = getLogger(__name__)


@opresource(name='TenderUa Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender related binary files (PDFs, etc.)")
class TenderUaDocumentResource(TenderDocumentResource):
    pass
