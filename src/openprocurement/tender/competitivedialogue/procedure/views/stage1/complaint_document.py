from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.complaint_document import (
    AboveThresholdComplaintDocumentState,
)


@resource(
    name="{}:Tender Complaint Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Competitive Dialogue complaint documents",
)
class CDEUComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = AboveThresholdComplaintDocumentState


@resource(
    name="{}:Tender Complaint Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Competitive Dialogue complaint documents",
)
class CDUAComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = AboveThresholdComplaintDocumentState
