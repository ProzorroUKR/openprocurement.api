from cornice.resource import resource
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
    QualificationComplaintWriteResource,
)
from openprocurement.tender.core.procedure.views.qualification_claim import QualificationClaimResource
from openprocurement.tender.esco.procedure.state.qualification_complaint import ESCOQualificationComplaintState
from openprocurement.tender.esco.procedure.state.qualification_claim import ESCOQualificationClaimState


@resource(
    name="esco:Tender Qualification Complaints Get",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["GET"],
    description="Tender EU qualification complaints get",
)
class ESCOQualificationClaimAndComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name="esco:Tender Qualification Claims",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender ESCO qualification claims",
)
class ESCOTenderQualificationClaimResource(QualificationClaimResource):
    state_class = ESCOQualificationClaimState


@resource(
    name="esco:Tender Qualification Complaints",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender ESCO qualification complaints",
)
class ESCOQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_class = ESCOQualificationComplaintState
