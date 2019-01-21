# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_document import (
    TenderUaAwardDocumentResource
)
from openprocurement.tender.openeu.views.award_document import (
    TenderAwardDocumentResource as TenderEUAwardDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
)


@optendersresource(name='{}:Tender Award Documents'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Tender award documents")
class CompetitiveDialogueStage2EUAwardDocumentResource(TenderEUAwardDocumentResource):
    pass


@optendersresource(name='{}:Tender Award Documents'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue Stage 2 UA award documents")
class CompetitiveDialogueStage2UAAwardDocumentResource(TenderUaAwardDocumentResource):
    pass
