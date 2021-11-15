# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.award_complaint import (
    BaseTenderAwardComplaintResource,
    BaseTenderAwardClaimResource
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="aboveThresholdUA:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["GET"],
    description="Tender award complaints get",
)
class TenderUAAwardComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name="aboveThresholdUA:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class TenderUAAwardComplaintResource(BaseTenderAwardComplaintResource):
    """ """


@optendersresource(
    name="aboveThresholdUA:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class TenderUAAwardClaimResource(BaseTenderAwardClaimResource):
    """ """
