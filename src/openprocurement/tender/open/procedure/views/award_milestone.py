from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardExtensionMilestoneState,
    AwardMilestoneState,
)
from openprocurement.tender.core.procedure.views.award_milestone import BaseAwardMilestoneResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.award_milestone import (
    BelowThresholdAwardMilestoneState,
    RFPAwardMilestoneState,
)
from openprocurement.tender.open.procedure.views.base import (
    OpenTenderingStateClass,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenBaseAwardMilestoneResource(BaseAwardMilestoneResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AwardMilestoneState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AwardMilestoneState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AwardExtensionMilestoneState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingStateClass(
            AwardMilestoneState, AwardExtensionMilestoneState
        ),
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: AwardMilestoneState,
        ProcurementMethodType.SIMPLE_DEFENSE: AwardMilestoneState,
        ProcurementMethodType.COMPETITIVE_ORDERING: AwardMilestoneState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdAwardMilestoneState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPAwardMilestoneState,
    }
