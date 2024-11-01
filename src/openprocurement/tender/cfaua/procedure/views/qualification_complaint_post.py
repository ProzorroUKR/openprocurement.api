from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_post import (
    CFAUAComplaintPostState,
)
from openprocurement.tender.core.procedure.views.qualification_complaint_post import (
    QualificationComplaintPostResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification Complaint Posts",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender qualification complaint posts",
)
class CFAUAQualificationComplaintPostResource(QualificationComplaintPostResource):
    state_class = CFAUAComplaintPostState
