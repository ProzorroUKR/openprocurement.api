from enum import StrEnum

from schematics.types import StringType

from openprocurement.api.constants import TENDER_CAUSE_DECREE_1178, TENDER_CAUSE_LAW_922
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.validation import ValidationError


class CauseScheme(StrEnum):
    DECREE_1178 = "DECREE1178"
    LAW_922 = "LAW922"


CAUSE_SCHEME_MAPPING = {
    CauseScheme.DECREE_1178.value: TENDER_CAUSE_DECREE_1178,
    CauseScheme.LAW_922.value: TENDER_CAUSE_LAW_922,
}


class CauseDetails(Model):
    title = StringType(required=True)
    scheme = StringType(
        required=True,
        choices=[
            CauseScheme.DECREE_1178.value,
            CauseScheme.LAW_922.value,
        ],
    )
    description = StringType()
    description_en = StringType()

    def validate_title(self, data, value):
        if value is not None and value not in CAUSE_SCHEME_MAPPING[data["scheme"]]:
            raise ValidationError(f"Value must be one of {CAUSE_SCHEME_MAPPING[data['scheme']]}.")
