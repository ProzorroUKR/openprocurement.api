from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.procedure.state.award_claim import OpenAwardClaimState
from openprocurement.tender.open.procedure.state.award_complaint import (
    OpenAwardComplaintState,
)


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    request_method=["GET"],
    description="Tender award complaints get",
)
class OpenAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class OpenTenderAwardClaimResource(AwardClaimResource):
    state_class = OpenAwardClaimState


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class OpenAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = OpenAwardComplaintState
