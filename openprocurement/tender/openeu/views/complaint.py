# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.complaint import TenderUaComplaintResource


@opresource(name='Tender EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU complaints")
class TenderEUComplaintResource(TenderUaComplaintResource):

    def complaints_len(self, tender):
        return sum([len(i.complaints) for i in tender.awards], sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)))
