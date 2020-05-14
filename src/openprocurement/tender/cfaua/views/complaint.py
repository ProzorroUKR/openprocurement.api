# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.complaint import TenderUaComplaintResource


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU complaints",
)
class TenderEUComplaintResource(TenderUaComplaintResource):
    pass
