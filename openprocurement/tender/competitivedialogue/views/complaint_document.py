# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.complaint_document import TenderUaComplaintDocumentResource
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE


@opresource(name='Competitive Dialogue EU Complaint Documents',
            collection_path='/tenders/{tender_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType=CD_EU_TYPE,
            description="Competitive Dialogue complaint documents")
class CompetitiveDialogueEUComplaintDocumentResource(TenderUaComplaintDocumentResource):
    pass


@opresource(name='Competitive Dialogue UA Complaint Documents',
            collection_path='/tenders/{tender_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType=CD_UA_TYPE,
            description="Competitive Dialogue complaint documents")
class CompetitiveDialogueUAComplaintDocumentResource(TenderUaComplaintDocumentResource):
    pass
