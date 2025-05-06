from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseTenderComplaintAppealDocumentResource,
)
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE


@resource(
    name=f"{ABOVE_THRESHOLD_UA_DEFENSE}:Tender Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_UA_DEFENSE,
    description="Tender complaint appeal documents",
)
class OpenUADefenseComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass
