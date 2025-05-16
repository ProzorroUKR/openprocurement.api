from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_complaint_appeal_document import (
    QualificationComplaintAppealDocumentResource,
)


@resource(
    name="aboveThresholdEU:Tender Qualification Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender qualification complaint appeal documents",
)
class OpenEUQualificationComplaintAppealDocumentResource(QualificationComplaintAppealDocumentResource):
    pass
