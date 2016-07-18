# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource
from openprocurement.tender.openua.views.complaint import TenderUaComplaintResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@opresource(name='Competitive Dialogue stage2 EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue stage2 EU complaints")
class CompetitiveDialogueStage2EUComplaintResource(TenderEUComplaintResource):
    pass


@opresource(name='Competitive Dialogue stage2 UA Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue stage2 UA complaints")
class CompetitiveDialogueStage2UAComplaintResource(TenderUaComplaintResource):
    pass
