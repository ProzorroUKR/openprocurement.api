# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.complaint_document import TenderEUComplaintDocumentResource


@opresource(name='Tender ESCO EU Complaint Documents',
            collection_path='/tenders/{tender_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Complaint documents")
class TenderESCOEUComplaintDocumentResource(TenderEUComplaintDocumentResource):
    """ Tender ESCO EU Complaint Document Resource """
