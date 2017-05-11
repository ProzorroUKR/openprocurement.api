# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.award_complaint_document import TenderEUAwardComplaintDocumentResource


@opresource(name='Tender EU Award Complaint Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender award complaint documents")
class TenderESCOEUAwardComplaintDocumentResource(TenderEUAwardComplaintDocumentResource):
    """ Tender ESCO EU Award Complaint Document Resource """
