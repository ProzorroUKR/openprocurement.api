# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_complaint import TenderUaAwardComplaintResource


@optendersresource(name='aboveThresholdEU:Tender Award Complaints',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
                   procurementMethodType='aboveThresholdEU',
                   description="Tender EU award complaints")
class TenderEUAwardComplaintResource(TenderUaAwardComplaintResource):

    def complaints_len(self, tender):
        return sum([len(i.complaints) for i in tender.awards], sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)))
