# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.complaint import TenderUaComplaintResource


@opresource(name='Competitive Dialogue EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Competitive Dialogue EU complaints")
class CompetitiveDialogueEUComplaintResource(TenderUaComplaintResource):

    def complaints_len(self, tender):
        return sum([len(i.complaints) for i in tender.awards], sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)))


@opresource(name='Competitive Dialogue UA Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Competitive Dialogue UA complaints")
class CompetitiveDialogueUAComplaintResource(TenderUaComplaintResource):
    def complaints_len(self, tender):
        return sum([len(i.complaints) for i in tender.awards],
                   sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)))
