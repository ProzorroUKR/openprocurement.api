from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource,
)
from openprocurement.tender.openua.procedure.state.complaint_document import (
    OpenUAComplaintDocumentState,
)


@resource(
    name="{}:Tender Cancellation Complaint Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender cancellation complaint documents",
)
class CD2EUCancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = OpenUAComplaintDocumentState


@resource(
    name="{}:Tender Cancellation Complaint Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender cancellation complaint documents",
)
class CD2UACancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = OpenUAComplaintDocumentState
