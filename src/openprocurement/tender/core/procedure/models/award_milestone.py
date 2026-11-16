from enum import StrEnum
from typing import Literal

from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import model_field_validator
from openprocurement.tender.core.procedure.models.milestone import (
    QualificationMilestone,
    QualificationMilestoneListMixin,
)
from openprocurement.tender.core.procedure.models.qualification_milestone import (
    PostQualificationMilestone,
)


class AwardMilestoneCode(StrEnum):
    CODE_24_HOURS = "24h"
    CODE_LOW_PRICE = "alp"
    CODE_EXTENSION_PERIOD = "extensionPeriod"


class PostAwardMilestone(PostQualificationMilestone):
    code: Literal[AwardMilestoneCode.CODE_24_HOURS, AwardMilestoneCode.CODE_EXTENSION_PERIOD]

    @model_field_validator("description")
    def validate_description(self, value):
        if self.code == AwardMilestoneCode.CODE_EXTENSION_PERIOD.value and value is None:
            raise ValidationError("This field is required.")


class AwardMilestone(QualificationMilestone):
    code: Literal[
        AwardMilestoneCode.CODE_24_HOURS,
        AwardMilestoneCode.CODE_LOW_PRICE,
        AwardMilestoneCode.CODE_EXTENSION_PERIOD,
    ]


class AwardMilestoneListMixin(QualificationMilestoneListMixin):
    milestones: list[AwardMilestone] | None = None
