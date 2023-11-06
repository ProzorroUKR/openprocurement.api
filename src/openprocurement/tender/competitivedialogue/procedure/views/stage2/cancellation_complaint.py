from cornice.resource import resource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.stage2.cancellation_complaint import \
    (
    CDEUStage2CancellationComplaintState, CDUAStage2CancellationComplaintState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU cancellation complaints",
    request_method=["GET"],
)
class CD2EUCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class CD2EUCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = CDEUStage2CancellationComplaintState


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA cancellation complaints",
    request_method=["GET"],
)
class CD2UACancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class CD2UACancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = CDUAStage2CancellationComplaintState
