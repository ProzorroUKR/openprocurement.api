from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.award_milestone import (
    PostAwardMilestone,
)
from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardMilestoneState,
)
from openprocurement.tender.core.procedure.validation import (
    validate_24h_milestone_released,
    validate_update_award_in_not_allowed_status,
    validate_update_award_only_for_active_lots,
)
from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.qualification_milestone import (
    BaseMilestoneResource,
    resolve_milestone,
)
from openprocurement.tender.core.utils import ProcurementMethodTypePredicate


class BaseAwardMilestoneResource(BaseMilestoneResource):
    context_name = "award"
    state_class = AwardMilestoneState

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_award(request)
        resolve_milestone(request, context_name="award")

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_item_owner("tender"),
            validate_24h_milestone_released,
            validate_input_data(PostAwardMilestone),
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    def set_location(self, tender, milestone):
        parent_obj = self.request.validated[self.context_name]
        route_prefix = ProcurementMethodTypePredicate.route_prefix(self.request)
        self.request.response.headers["Location"] = self.request.route_url(
            "{}:Tender {} Milestones".format(route_prefix, self.context_name.capitalize()),
            **{
                "tender_id": tender["_id"],
                "{}_id".format(self.context_name): parent_obj["id"],
                "milestone_id": milestone["id"],
            },
        )
