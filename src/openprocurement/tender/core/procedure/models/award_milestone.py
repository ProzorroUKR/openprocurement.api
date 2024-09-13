from enum import Enum

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


class AwardMilestoneCodes(Enum):
    CODE_24_HOURS = "24h"
    CODE_LOW_PRICE = "alp"
    CODE_EXTENSION_PERIOD = "extensionPeriod"


class PostAwardMilestone(PostQualificationMilestone):
    code = StringType(
        required=True,
        choices=[
            AwardMilestoneCodes.CODE_24_HOURS.value,
            AwardMilestoneCodes.CODE_EXTENSION_PERIOD.value,
            # AwardMilestoneCodes.CODE_LOW_PRICE.value,  # this one cannot be posted
        ],
    )

    def validate_description(self, data, value):
        if data["code"] == AwardMilestoneCodes.CODE_EXTENSION_PERIOD.value and value is None:
            raise ValidationError("This field is required.")


class AwardMilestone(QualificationMilestone):
    code = StringType(
        required=True,
        choices=[
            AwardMilestoneCodes.CODE_24_HOURS.value,
            AwardMilestoneCodes.CODE_LOW_PRICE.value,
            AwardMilestoneCodes.CODE_EXTENSION_PERIOD.value,
        ],
    )


class AwardMilestoneListMixin(QualificationMilestoneListMixin):
    milestones = ListType(ModelType(AwardMilestone, required=True))
