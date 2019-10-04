# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.award_complaint import TenderEUAwardComplaintResource


@optendersresource(
    name="esco:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    description="Tender ESCO Award complaints",
)
class TenderESCOAwardComplaintResource(TenderEUAwardComplaintResource):
    """ Tender ESCO Award Complaint Resource """
