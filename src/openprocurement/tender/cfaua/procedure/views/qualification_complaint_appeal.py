from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_appeal import (
    CFAUAComplaintAppealState,
)
from openprocurement.tender.core.procedure.views.qualification_complaint_appeal import (
    QualificationComplaintAppealResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification Complaint Appeals",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender qualification complaint posts",
)
class CFAUAQualificationComplaintAppealResource(QualificationComplaintAppealResource):
    state_class = CFAUAComplaintAppealState
