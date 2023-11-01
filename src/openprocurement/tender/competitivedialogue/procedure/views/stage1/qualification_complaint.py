from cornice.resource import resource

from openprocurement.tender.competitivedialogue.procedure.state.stage1.qualification_claim import (
    CDStage1QualificationClaimState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.qualification_complaint import (
    CDStage1QualificationComplaintState,
)
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
    QualificationComplaintWriteResource,
)
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.qualification_claim import QualificationClaimResource


@resource(
    name="{}:Tender Qualification Complaints Get".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue EU qualification complaints get",
)
class CDEUQualificationClaimAndComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name="{}:Tender Qualification Claims".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue EU qualification claims",
)
class CDEUTenderQualificationClaimResource(QualificationClaimResource):
    state_class = CDStage1QualificationClaimState


@resource(
    name="{}:Tender Qualification Complaints".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue EU qualification complaints",
)
class CDEUQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_class = CDStage1QualificationComplaintState


@resource(
    name="{}:Tender Qualification Complaints Get".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue UA qualification complaints get",
)
class CDUAQualificationClaimAndComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name="{}:Tender Qualification Claims".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA qualification claims",
)
class CDUATenderQualificationClaimResource(QualificationClaimResource):
    state_class = CDStage1QualificationClaimState


@resource(
    name="{}:Tender Qualification Complaints".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue UA qualification complaints",
)
class CDUAQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_class = CDStage1QualificationComplaintState
