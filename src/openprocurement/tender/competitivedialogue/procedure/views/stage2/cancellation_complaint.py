from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.cancellation_complaint import (
    CDStage2EUCancellationComplaintState,
    CDStage2UACancellationComplaintState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2}:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 EU cancellation complaints",
    request_method=["GET"],
)
class CD2EUCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2}:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 EU cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class CD2EUCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = CDStage2EUCancellationComplaintState


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2}:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue Stage 2 UA cancellation complaints",
    request_method=["GET"],
)
class CD2UACancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2}:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue Stage 2 UA cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class CD2UACancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = CDStage2UACancellationComplaintState
