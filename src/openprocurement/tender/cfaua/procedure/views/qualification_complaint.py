from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.qualification_claim import (
    CFAUAQualificationClaimState,
)
from openprocurement.tender.cfaua.procedure.state.qualification_complaint import (
    CFAUAQualificationComplaintState,
)
from openprocurement.tender.core.procedure.views.qualification_claim import (
    QualificationClaimResource,
)
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
    QualificationComplaintWriteResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification Complaints Get",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["GET"],
    description="Tender EU qualification complaints get",
)
class CFAUAQualificationClaimAndComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification Claims",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU qualification claims",
)
class CFAUATenderQualificationClaimResource(QualificationClaimResource):
    state_class = CFAUAQualificationClaimState


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification Complaints",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU qualification complaints",
)
class CFAUAQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_class = CFAUAQualificationComplaintState
