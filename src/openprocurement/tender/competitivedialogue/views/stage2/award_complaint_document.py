# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_complaint_document import (
    TenderUaAwardComplaintDocumentResource
)
from openprocurement.tender.openeu.views.award_complaint_document import (
    TenderEUAwardComplaintDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
)

@optendersresource(name='{}:Tender Award Complaint Documents'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue Stage 2 award complaint documents")
class CompetitiveDialogueStage2EUAwardComplaintDocumentResource(TenderEUAwardComplaintDocumentResource):
    pass


@optendersresource(name='{}:Tender Award Complaint Documents'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue Stage 2 award complaint documents")
class CompetitiveDialogueStage2UAAwardComplaintDocumentResource(TenderUaAwardComplaintDocumentResource):
    pass
