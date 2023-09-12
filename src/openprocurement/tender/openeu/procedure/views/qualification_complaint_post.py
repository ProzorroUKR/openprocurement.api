from openprocurement.tender.core.procedure.views.qualification_complaint_post import QualificationComplaintPostResource
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Qualification Complaint Posts",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender qualification complaint posts",
)
class OpenEUQualificationComplaintPostResource(QualificationComplaintPostResource):
    pass
