from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.award_claim import (
    AboveThresholdAwardClaimState,
    AboveThresholdEUAwardClaimState,
    BelowThresholdAwardClaimState,
    COAwardClaimState,
    DefenseAwardClaimState,
    RFPAwardClaimState,
    SimpleDefenseAwardClaimState,
)
from openprocurement.tender.open.procedure.state.award_complaint import (
    AboveThresholdAwardComplaintState,
    AboveThresholdEUAwardComplaintState,
    COAwardComplaintState,
    DefenseAwardComplaintState,
    SimpleDefenseAwardComplaintState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    request_method=["GET"],
    description="Tender award complaints get",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenAwardComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenAwardClaimResource(AwardClaimResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdAwardClaimState,
        ABOVE_THRESHOLD_UA: AboveThresholdAwardClaimState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUAwardClaimState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseAwardClaimState,
        SIMPLE_DEFENSE: SimpleDefenseAwardClaimState,
        COMPETITIVE_ORDERING: COAwardClaimState,
        BELOW_THRESHOLD: BelowThresholdAwardClaimState,
        REQUEST_FOR_PROPOSAL: RFPAwardClaimState,
    }


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        ABOVE_THRESHOLD_UA_DEFENSE,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
    ],
)
class OpenAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdAwardComplaintState,
        ABOVE_THRESHOLD_UA: AboveThresholdAwardComplaintState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUAwardComplaintState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseAwardComplaintState,
        SIMPLE_DEFENSE: SimpleDefenseAwardComplaintState,
        COMPETITIVE_ORDERING: COAwardComplaintState,
    }
