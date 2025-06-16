from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.award_claim import (
    COAwardClaimState,
)
from openprocurement.tender.competitiveordering.procedure.state.award_complaint import (
    COAwardComplaintState,
)
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    request_method=["GET"],
    description="Tender award complaints get",
)
class COAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class COTenderAwardClaimResource(AwardClaimResource):
    state_class = COAwardClaimState


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class COAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = COAwardComplaintState
