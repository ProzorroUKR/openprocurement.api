# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.validation import (
    validate_award_milestone_data,
    validate_award_milestone_24hours,
    validate_24h_milestone_released,
)
from openprocurement.tender.core.views.qualification_milestone import BaseQualificationMilestoneResource


class BaseAwardMilestoneResource(BaseQualificationMilestoneResource):

    context_name = "award"

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_24h_milestone_released,
            validate_award_milestone_data,
            validate_award_milestone_24hours,
        ),
    )
    def collection_post(self):
        return super(BaseAwardMilestoneResource, self).collection_post()
