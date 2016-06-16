# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource


@opresource(name='Competitive Dialogue EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Competitive Dialogue EU complaints")
class CompetitiveDialogueEUComplaintResource(TenderEUComplaintResource):
    pass


@opresource(name='Competitive Dialogue UA Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Competitive Dialogue UA complaints")
class CompetitiveDialogueUAComplaintResource(TenderEUComplaintResource):
    pass

