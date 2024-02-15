from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.stage1.cancellation_complaint import (
    CDStage1CancellationComplaintState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)


@resource(
    name="{}:Tender Cancellation Complaints Get".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU cancellation complaints",
    request_method=["GET"],
)
class CDEUCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaints".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class CDEUCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = CDStage1CancellationComplaintState


@resource(
    name="{}:Tender Cancellation Complaints Get".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA cancellation complaints",
    request_method=["GET"],
)
class CDUACancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="{}:Tender Cancellation Complaints".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class CDUACancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = CDStage1CancellationComplaintState
