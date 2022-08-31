# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.award_complaint import (
    BaseTenderAwardComplaintResource,
    BaseTenderAwardClaimResource
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    request_method=["GET"],
    description="Tender award complaints get",
)
class TenderAwardComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class TenderAwardComplaintResource(BaseTenderAwardComplaintResource):
    """ """


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class TenderAwardClaimResource(BaseTenderAwardClaimResource):
    """ """
