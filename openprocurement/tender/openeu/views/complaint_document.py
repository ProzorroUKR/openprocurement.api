# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.complaint_document import TenderUaComplaintDocumentResource

LOGGER = getLogger(__name__)


@opresource(name='Tender EU Award Complaint Documents',
            collection_path='/tenders/{tender_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender complaint documents")
class TenderEUComplaintDocumentResource(TenderUaComplaintDocumentResource):
    pass
