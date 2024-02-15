from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_document import (
    AwardComplaintDocumentResource,
)
from openprocurement.tender.limited.procedure.state.award_complaint_document import (
    NegotiationAwardComplaintDocumentState,
)


@resource(
    name="negotiation:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="negotiation",
    description="Tender negotiation award complaint documents",
)
class NegotiationAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = NegotiationAwardComplaintDocumentState


@resource(
    name="negotiation.quick:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="negotiation.quick",
    description="Tender negotiation.quick award complaint documents",
)
class NegotiationQuickAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = NegotiationAwardComplaintDocumentState
