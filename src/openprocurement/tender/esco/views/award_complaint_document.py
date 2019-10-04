# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.award_complaint_document import TenderEUAwardComplaintDocumentResource


@optendersresource(
    name="esco:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender award complaint documents",
)
class TenderESCOAwardComplaintDocumentResource(TenderEUAwardComplaintDocumentResource):
    """ Tender ESCO Award Complaint Document Resource """
