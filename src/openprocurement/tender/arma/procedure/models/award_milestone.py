from schematics.types import StringType

from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestone,
    AwardMilestoneCode,
    AwardMilestoneListMixin,
    PostAwardMilestone,
)


class ARMAPostAwardMilestone(PostAwardMilestone):
    code = StringType(
        required=True,
        choices=[
            AwardMilestoneCode.CODE_24_HOURS.value,
        ],
    )


class ARMAAwardMilestone(AwardMilestone):
    code = StringType(
        required=True,
        choices=[
            AwardMilestoneCode.CODE_24_HOURS.value,
            AwardMilestoneCode.CODE_LOW_PRICE.value,
        ],
    )


class ARMAAwardMilestoneListMixin(AwardMilestoneListMixin):
    milestones = ListType(ModelType(ARMAAwardMilestone, required=True))
