from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)
from openprocurement.tender.limited.procedure.state.award_milestone import (
    ReportingAwardMilestoneState,
)


@resource(
    name="reporting:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType="reporting",
)
class ReportingAwardMilestoneResource(BaseAwardMilestoneResource):
    state_class = ReportingAwardMilestoneState


@resource(
    name="negotiation:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType="negotiation",
)
class NegotiationAwardMilestoneResource(ReportingAwardMilestoneResource):
    pass


@resource(
    name="negotiation.quick:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType="negotiation.quick",
)
class NegotiationQuickAwardMilestoneResource(ReportingAwardMilestoneResource):
    pass
