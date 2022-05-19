from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import validate_item_owner
from openprocurement.tender.core.validation import validate_24h_milestone_released
from openprocurement.tender.core.procedure.validation import validate_input_data
from openprocurement.tender.core.procedure.models.qualification_milestone import PostQualificationMilestone
from openprocurement.tender.core.procedure.views.qualification_milestone import (
    BaseQualificationMilestoneResource,
    resolve_milestone,
)
from openprocurement.tender.core.procedure.views.award import resolve_award


class BaseAwardMilestoneResource(BaseQualificationMilestoneResource):

    context_name = "award"

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
            validate_input_data(PostQualificationMilestone),
        ),
    )
    def collection_post(self):
        return super(BaseAwardMilestoneResource, self).collection_post()
