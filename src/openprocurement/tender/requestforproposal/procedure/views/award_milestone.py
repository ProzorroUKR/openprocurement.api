from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)
from openprocurement.tender.requestforproposal.procedure.state.award_milestone import (
    RequestForProposalAwardMilestoneState,
)


@resource(
    name="requestForProposal:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType="requestForProposal",
)
class RequestForProposalAwardMilestoneResource(BaseAwardMilestoneResource):
    state_class = RequestForProposalAwardMilestoneState
