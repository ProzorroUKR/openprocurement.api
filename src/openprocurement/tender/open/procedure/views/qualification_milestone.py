from cornice.resource import resource

from openprocurement.tender.core.procedure.state.qualification_milestone import QualificationMilestoneState
from openprocurement.tender.core.procedure.views.qualification_milestone import QualificationMilestoneResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.qualification_milestone import RFPQualificationMilestoneState


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    description="Tender qualification milestones",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenQualificationMilestoneResource(QualificationMilestoneResource):
    state_classes = {
        ABOVE_THRESHOLD: QualificationMilestoneState,
        ABOVE_THRESHOLD_UA: QualificationMilestoneState,
        ABOVE_THRESHOLD_EU: QualificationMilestoneState,
        ABOVE_THRESHOLD_UA_DEFENSE: QualificationMilestoneState,
        SIMPLE_DEFENSE: QualificationMilestoneState,
        COMPETITIVE_ORDERING: QualificationMilestoneState,
        BELOW_THRESHOLD: QualificationMilestoneState,
        REQUEST_FOR_PROPOSAL: RFPQualificationMilestoneState,
    }
