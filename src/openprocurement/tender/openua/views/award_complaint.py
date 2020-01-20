# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.award_complaint import BaseTenderAwardComplaintResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="aboveThresholdUA:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender award complaints",
)
class TenderUaAwardComplaintResource(BaseTenderAwardComplaintResource):
    pass