from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage1.qualification_claim import (
    CDStage1QualificationClaimState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.qualification_complaint import (
    CDStage1QualificationComplaintState,
)
from openprocurement.tender.core.procedure.views.qualification_claim import (
    QualificationClaimResource,
)
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
    QualificationComplaintWriteResource,
)


@resource(
    name="{}:Tender Qualification Complaints Get".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    request_method=["GET"],
    description="Competitive Dialogue EU qualification complaints get",
)
class CDEUQualificationClaimAndComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name="{}:Tender Qualification Claims".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue EU qualification claims",
)
class CDEUTenderQualificationClaimResource(QualificationClaimResource):
    state_class = CDStage1QualificationClaimState


@resource(
    name="{}:Tender Qualification Complaints".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue EU qualification complaints",
)
class CDEUQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_class = CDStage1QualificationComplaintState


@resource(
    name="{}:Tender Qualification Complaints Get".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    request_method=["GET"],
    description="Competitive Dialogue UA qualification complaints get",
)
class CDUAQualificationClaimAndComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name="{}:Tender Qualification Claims".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Competitive Dialogue UA qualification claims",
)
class CDUATenderQualificationClaimResource(QualificationClaimResource):
    state_class = CDStage1QualificationClaimState


@resource(
    name="{}:Tender Qualification Complaints".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue UA qualification complaints",
)
class CDUAQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_class = CDStage1QualificationComplaintState
