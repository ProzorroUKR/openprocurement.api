from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.award_milestone import (
    PostAwardMilestone,
)
from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)
from openprocurement.tender.limited.procedure.state.award_milestone import (
    ReportingAwardMilestoneState,
)
from openprocurement.tender.limited.procedure.validation import (
    validate_award_operation_not_in_active_status,
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

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PostAwardMilestone),
            validate_award_operation_not_in_active_status,
        ),
    )
    def collection_post(self):
        return super().collection_post()


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
