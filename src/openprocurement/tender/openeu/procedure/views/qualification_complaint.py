from cornice.resource import resource
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
    QualificationComplaintWriteResource,
)
from openprocurement.tender.core.procedure.views.qualification_claim import QualificationClaimResource
from openprocurement.tender.openeu.procedure.state.qualification_claim import OpenEUQualificationClaimState
from openprocurement.tender.openeu.procedure.state.qualification_complaint import OpenEUQualificationComplaintState


@resource(
    name="aboveThresholdEU:Tender Qualification Complaints Get",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["GET"],
    description="Tender EU qualification complaints get",
)
class OpenEUQualificationClaimAndComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name="aboveThresholdEU:Tender Qualification Claims",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU qualification claims",
)
class OpenEUTenderQualificationClaimResource(QualificationClaimResource):
    state_class = OpenEUQualificationClaimState


@resource(
    name="aboveThresholdEU:Tender Qualification Complaints",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU qualification complaints",
)
class OpenEUQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_class = OpenEUQualificationComplaintState

