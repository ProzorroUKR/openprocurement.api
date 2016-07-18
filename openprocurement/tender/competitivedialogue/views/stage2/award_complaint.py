# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award_complaint import TenderUaAwardComplaintResource
from openprocurement.tender.openeu.views.award_complaint import TenderEUAwardComplaintResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@opresource(name='Competitive Dialogue Stage 2 EU Award Complaints',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue Stage 2 EU award complaints")
class CompetitiveDialogueEUAwardComplaintResource(TenderEUAwardComplaintResource):
    pass


@opresource(name='Competitive Dialogue Stage 2 UA Award Complaints',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue Stage 2 UA award complaints")
class CompetitiveDialogueEUAwardComplaintResource(TenderUaAwardComplaintResource):
    pass
