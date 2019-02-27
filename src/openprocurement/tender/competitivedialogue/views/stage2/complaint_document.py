# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.complaint_document import (
    TenderUaComplaintDocumentResource
)
from openprocurement.tender.openeu.views.complaint_document import (
    TenderEUComplaintDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
)


@optendersresource(name='{}:Tender Complaint Documents'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue stage2 EU complaint documents")
class CompetitiveDialogueStage2EUComplaintDocumentResource(TenderEUComplaintDocumentResource):
    pass


@optendersresource(name='{}:Tender Complaint Documents'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue stage2 UA complaint documents")
class CompetitiveDialogueStage2UAComplaintDocumentResource(TenderUaComplaintDocumentResource):
    pass
