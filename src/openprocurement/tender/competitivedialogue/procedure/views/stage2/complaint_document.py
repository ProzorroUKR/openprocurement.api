from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.complaint_document import (
    AboveThresholdComplaintDocumentState,
)


@resource(
    name="{}:Tender Complaint Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue stage2 EU complaint documents",
)
class CD2EUComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = AboveThresholdComplaintDocumentState


@resource(
    name="{}:Tender Complaint Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue stage2 UA complaint documents",
)
class CD2UAComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = AboveThresholdComplaintDocumentState
