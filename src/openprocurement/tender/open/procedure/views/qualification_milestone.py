from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.state.qualification_milestone import QualificationMilestoneState
from openprocurement.tender.core.procedure.views.qualification_milestone import QualificationMilestoneResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.qualification_milestone import RFPQualificationMilestoneState


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    description="Tender qualification milestones",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenQualificationMilestoneResource(QualificationMilestoneResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: QualificationMilestoneState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: QualificationMilestoneState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: QualificationMilestoneState,
        ProcurementMethodType.OPEN_TENDERING: QualificationMilestoneState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: QualificationMilestoneState,
        ProcurementMethodType.SIMPLE_DEFENSE: QualificationMilestoneState,
        ProcurementMethodType.COMPETITIVE_ORDERING: QualificationMilestoneState,
        ProcurementMethodType.BELOW_THRESHOLD: QualificationMilestoneState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPQualificationMilestoneState,
    }
