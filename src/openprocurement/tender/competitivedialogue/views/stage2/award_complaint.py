# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_complaint import (
    TenderUaAwardComplaintResource
)
from openprocurement.tender.openeu.views.award_complaint import (
    TenderEUAwardComplaintResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
)


@optendersresource(name='{}:Tender Award Complaints'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue Stage 2 EU award complaints")
class CompetitiveDialogueStage2EUAwardComplaintResource(TenderEUAwardComplaintResource):
    pass


@optendersresource(name='{}:Tender Award Complaints'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue Stage 2 UA award complaints")
class CompetitiveDialogueStage2UAAwardComplaintResource(TenderUaAwardComplaintResource):
    pass
