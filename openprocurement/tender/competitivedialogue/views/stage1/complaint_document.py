# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.complaint_document import (
    TenderUaComplaintDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@optendersresource(name='{}:Tender Complaint Documents'.format(CD_EU_TYPE),
                   collection_path='/tenders/{tender_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType=CD_EU_TYPE,
                   description="Competitive Dialogue complaint documents")
class CompetitiveDialogueEUComplaintDocumentResource(TenderUaComplaintDocumentResource):
    pass


@optendersresource(name='{}:Tender Complaint Documents'.format(CD_UA_TYPE),
                   collection_path='/tenders/{tender_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType=CD_UA_TYPE,
                   description="Competitive Dialogue complaint documents")
class CompetitiveDialogueUAComplaintDocumentResource(TenderUaComplaintDocumentResource):
    pass
