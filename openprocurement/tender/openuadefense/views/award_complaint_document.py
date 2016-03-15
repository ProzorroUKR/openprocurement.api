# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.award_complaint_document import TenderUaAwardComplaintDocumentResource as TenderAwardComplaintDocumentResource
from openprocurement.api.utils import opresource


@opresource(name='Tender UA.defense Award Complaint Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender award complaint documents")
class TenderUaAwardComplaintDocumentResource(TenderAwardComplaintDocumentResource):
    """ """
