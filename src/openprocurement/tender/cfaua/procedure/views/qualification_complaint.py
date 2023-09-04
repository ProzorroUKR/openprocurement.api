from cornice.resource import resource
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
    QualificationComplaintWriteResource,
)
from openprocurement.tender.core.procedure.views.qualification_claim import QualificationClaimResource


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
    pass


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
    pass

