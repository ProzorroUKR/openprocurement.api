from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.award_complaint_document import (
    COAwardComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.award_complaint_document import (
    AwardComplaintDocumentResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender award complaint documents",
)
class COAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = COAwardComplaintDocumentState
