# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.views.award_complaint_document import TenderAwardComplaintDocumentResource
from openprocurement.api.utils import opresource



LOGGER = getLogger(__name__)


@opresource(name='Tender Award Complaint Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender award complaint documents")
class TenderUaAwardComplaintDocumentResource(TenderAwardComplaintDocumentResource):
    pass