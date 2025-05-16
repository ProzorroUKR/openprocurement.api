from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseTenderComplaintAppealDocumentResource,
)


@resource(
    name="aboveThresholdEU:Tender Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender complaint appeal documents",
)
class OpenEUComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass
