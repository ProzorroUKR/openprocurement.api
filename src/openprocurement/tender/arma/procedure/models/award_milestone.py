from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestone as BaseAwardMilestone,
)
from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneCode,
)
from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneListMixin as BaseAwardMilestoneListMixin,
)
from openprocurement.tender.core.procedure.models.award_milestone import (
    PostAwardMilestone as BasePostAwardMilestone,
)


class PostAwardMilestone(BasePostAwardMilestone):
    code = StringType(
        required=True,
        choices=[
            AwardMilestoneCode.CODE_24_HOURS.value,
        ],
    )


class AwardMilestone(BaseAwardMilestone):
    code = StringType(
        required=True,
        choices=[
            AwardMilestoneCode.CODE_24_HOURS.value,
            AwardMilestoneCode.CODE_LOW_PRICE.value,
        ],
    )


class AwardMilestoneListMixin(BaseAwardMilestoneListMixin):
    milestones = ListType(ModelType(AwardMilestone, required=True))
