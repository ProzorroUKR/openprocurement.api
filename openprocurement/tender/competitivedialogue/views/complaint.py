# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE


@opresource(name='Competitive Dialogue EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType=CD_EU_TYPE,
            description="Competitive Dialogue EU complaints")
class CompetitiveDialogueEUComplaintResource(TenderEUComplaintResource):
    pass


@opresource(name='Competitive Dialogue UA Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType=CD_UA_TYPE,
            description="Competitive Dialogue UA complaints")
class CompetitiveDialogueUAComplaintResource(TenderEUComplaintResource):
    pass
