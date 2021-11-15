# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.award_complaint import (
    BaseTenderAwardComplaintResource,
    BaseTenderAwardClaimResource
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)

@optendersresource(
    name="aboveThresholdEU:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["GET"],
    description="Tender EU award complaints get",
)
class TenderEUAwardComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name="aboveThresholdEU:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU award complaints",
)
class TenderEUAwardComplaintResource(BaseTenderAwardComplaintResource):
    """"""


@optendersresource(
    name="aboveThresholdEU:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU award claims",
)
class TenderEUAwardClaimResource(BaseTenderAwardClaimResource):
    """"""
