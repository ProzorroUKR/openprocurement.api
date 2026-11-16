from typing import Literal

from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestone,
    AwardMilestoneCode,
    AwardMilestoneListMixin,
    PostAwardMilestone,
)


class ARMAPostAwardMilestone(PostAwardMilestone):
    code: Literal[AwardMilestoneCode.CODE_24_HOURS]  # type: ignore[valid-type]


class ARMAAwardMilestone(AwardMilestone):
    code: Literal[AwardMilestoneCode.CODE_24_HOURS, AwardMilestoneCode.CODE_LOW_PRICE]  # type: ignore[valid-type]


class ARMAAwardMilestoneListMixin(AwardMilestoneListMixin):
    milestones: list[ARMAAwardMilestone] | None = None
