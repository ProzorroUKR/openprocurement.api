# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openuadefense.views.complaint import TenderUaComplaintResource


@optendersresource(
    name="simple.defense:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    description="Tender complaints",
)
class TenderSimpleComplaintResource(TenderUaComplaintResource):
    pass