from openprocurement.tender.core.procedure.views.qualification_complaint_document import (
    QualificationComplaintDocumentResource,
)
from cornice.resource import resource


@resource(
    name="esco:Tender Qualification Complaint Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO qualification complaint documents",
)
class ESCOQualificationComplaintDocumentResource(QualificationComplaintDocumentResource):
    pass
