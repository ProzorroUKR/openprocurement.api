# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.complaint_document import (
    TenderUaComplaintDocumentResource as TenderComplaintDocumentResource,
)


@optendersresource(
    name="simple.defense:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="simple.defense",
    description="Tender complaint documents",
)
class TenderUaComplaintDocumentResource(TenderComplaintDocumentResource):
    """ """
