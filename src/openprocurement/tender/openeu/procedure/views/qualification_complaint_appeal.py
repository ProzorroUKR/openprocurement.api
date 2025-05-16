from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_complaint_appeal import (
    QualificationComplaintAppealResource,
)


@resource(
    name="aboveThresholdEU:Tender Qualification Complaint Appeals",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender qualification complaint appeals",
)
class OpenEUQualificationComplaintAppealResource(QualificationComplaintAppealResource):
    pass
