# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openuadefense.views.award_complaint import TenderUaAwardComplaintResource


@optendersresource(
    name="simple.defense:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    description="Tender award complaints",
)
class TenderSimpleDefAwardComplaintResource(TenderUaAwardComplaintResource):
    """ """
