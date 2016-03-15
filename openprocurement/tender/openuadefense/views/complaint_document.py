# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.complaint_document import TenderUaComplaintDocumentResource as TenderComplaintDocumentResource


@opresource(name='Tender UA.defense Complaint Documents',
            collection_path='/tenders/{tender_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender complaint documents")
class TenderUaComplaintDocumentResource(TenderComplaintDocumentResource):
    """ """
