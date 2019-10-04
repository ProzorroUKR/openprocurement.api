# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.complaint_document import TenderEUComplaintDocumentResource


@optendersresource(
    name="esco:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO Complaint documents",
)
class TenderESCOComplaintDocumentResource(TenderEUComplaintDocumentResource):
    """ Tender ESCO Complaint Document Resource """
