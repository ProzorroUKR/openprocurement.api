# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award_complaint import TenderUaAwardComplaintResource as TenderAwardComplaintResource


@opresource(name='Tender UA.defense Award Complaints',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender award complaints")
class TenderUaAwardComplaintResource(TenderAwardComplaintResource):
    """ """
