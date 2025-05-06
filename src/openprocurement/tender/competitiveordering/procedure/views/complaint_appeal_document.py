from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseTenderComplaintAppealDocumentResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender complaint appeal documents",
)
class COComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass
