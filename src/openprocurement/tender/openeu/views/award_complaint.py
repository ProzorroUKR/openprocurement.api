# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.award_complaint import BaseTenderAwardComplaintResource


@optendersresource(
    name="aboveThresholdEU:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU award complaints",
)
class TenderEUAwardComplaintResource(BaseTenderAwardComplaintResource):
    pass
