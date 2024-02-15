from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.stage2.qualification_claim import (
    CDEUStage2QualificationClaimState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.qualification_complaint import (
    CDEUStage2QualificationComplaintState,
)
from openprocurement.tender.core.procedure.views.qualification_claim import (
    QualificationClaimResource,
)
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
    QualificationComplaintWriteResource,
)


@resource(
    name="{}:Tender Qualification Complaints Get".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue Stage 2 EU qualification complaints get",
)
class CD2EUQualificationClaimAndComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name="{}:Tender Qualification Claims".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue Stage 2 EU qualification claims",
)
class CD2EUTenderQualificationClaimResource(QualificationClaimResource):
    state_class = CDEUStage2QualificationClaimState


@resource(
    name="{}:Tender Qualification Complaints".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue Stage 2 EU qualification complaints",
)
class CD2EUQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_class = CDEUStage2QualificationComplaintState
