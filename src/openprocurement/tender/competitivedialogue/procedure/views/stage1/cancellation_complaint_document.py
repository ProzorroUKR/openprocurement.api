from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.complaint_document import (
    AboveThresholdUAComplaintDocumentState,
)


@resource(
    name="{}:Tender Cancellation Complaint Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Tender cancellation complaint documents",
)
class CDEUCancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = AboveThresholdUAComplaintDocumentState


@resource(
    name="{}:Tender Cancellation Complaint Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Tender cancellation complaint documents",
)
class CDUACancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = AboveThresholdUAComplaintDocumentState
