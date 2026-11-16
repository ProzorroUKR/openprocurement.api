from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.award_claim import (
    AboveThresholdAwardClaimState,
    AboveThresholdEUAwardClaimState,
    BelowThresholdAwardClaimState,
    COAwardClaimState,
    DefenseAwardClaimState,
    OpenTenderingAwardClaimState,
    RFPAwardClaimState,
    SimpleDefenseAwardClaimState,
)
from openprocurement.tender.open.procedure.state.award_complaint import (
    AboveThresholdAwardComplaintState,
    AboveThresholdEUAwardComplaintState,
    COAwardComplaintState,
    DefenseAwardComplaintState,
    OpenTenderingAwardComplaintState,
    SimpleDefenseAwardComplaintState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    request_method=["GET"],
    description="Tender award complaints get",
    procurementMethodType=OpenProcurementMethodType,
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
    procurementMethodType=OpenProcurementMethodType,
)
class OpenAwardClaimResource(AwardClaimResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdAwardClaimState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdAwardClaimState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUAwardClaimState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingAwardClaimState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseAwardClaimState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseAwardClaimState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COAwardClaimState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdAwardClaimState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPAwardClaimState,
    }


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
    ],
)
class OpenAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdAwardComplaintState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdAwardComplaintState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUAwardComplaintState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingAwardComplaintState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseAwardComplaintState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseAwardComplaintState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COAwardComplaintState,
    }
