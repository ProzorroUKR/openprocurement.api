from enum import StrEnum

from schematics.exceptions import ValidationError
from schematics.types import StringType

from openprocurement.api.procedure.types import ListType, ModelType
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
    code = StringType(
        required=True,
        choices=[
            AwardMilestoneCode.CODE_24_HOURS.value,
            AwardMilestoneCode.CODE_EXTENSION_PERIOD.value,
            # AwardMilestoneCode.CODE_LOW_PRICE.value,  # this one cannot be posted
        ],
    )

    def validate_description(self, data, value):
        if data["code"] == AwardMilestoneCode.CODE_EXTENSION_PERIOD.value and value is None:
            raise ValidationError("This field is required.")


class AwardMilestone(QualificationMilestone):
    code = StringType(
        required=True,
        choices=[
            AwardMilestoneCode.CODE_24_HOURS.value,
            AwardMilestoneCode.CODE_LOW_PRICE.value,
            AwardMilestoneCode.CODE_EXTENSION_PERIOD.value,
        ],
    )


class AwardMilestoneListMixin(QualificationMilestoneListMixin):
    milestones = ListType(ModelType(AwardMilestone, required=True))
