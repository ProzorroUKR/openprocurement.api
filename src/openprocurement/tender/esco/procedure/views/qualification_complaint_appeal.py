from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_complaint_appeal import (
    QualificationComplaintAppealResource,
)
from openprocurement.tender.esco.constants import ESCO


@resource(
    name=f"{ESCO}:Tender Qualification Complaint Appeals",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ESCO,
    description="Tender qualification complaint appeals",
)
class ESCOQualificationComplaintAppealResource(QualificationComplaintAppealResource):
    pass
