from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.qualification_complaint_document import (
    QualificationComplaintDocumentResource,
)
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Complaint Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}",
    description="Tender qualification complaint documents",
    procurementMethodType=[ProcurementMethodType.ABOVE_THRESHOLD_EU, ProcurementMethodType.OPEN_TENDERING],
)
class OpenQualificationComplaintDocumentResource(QualificationComplaintDocumentResource):
    pass
