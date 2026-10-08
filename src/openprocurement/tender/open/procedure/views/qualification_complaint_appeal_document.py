from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_complaint_appeal_document import (
    QualificationComplaintAppealDocumentResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_EU, OPEN_ROUTE_PREFIX


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    description="Tender qualification complaint appeal documents",
    procurementMethodType=[ABOVE_THRESHOLD_EU],
)
class OpenQualificationComplaintAppealDocumentResource(QualificationComplaintAppealDocumentResource):
    pass
