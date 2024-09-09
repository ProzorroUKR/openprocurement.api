from schematics.exceptions import ValidationError
from schematics.types import BooleanType

from openprocurement.tender.core.procedure.models.award import Award as BaseAward
from openprocurement.tender.core.procedure.models.award import (
    PatchAward as BasePatchAward,
)
from openprocurement.tender.core.procedure.models.award import (
    PostAward as BasePostAward,
)


class Award(BaseAward):
    eligible = BooleanType()

    def validate_eligible(self, data, eligible):
        if data["status"] == "active" and not eligible:
            raise ValidationError("Can't update award to active status with not eligible")


class PatchAward(BasePatchAward):
    eligible = BooleanType()


class PostAward(BasePostAward):
    pass
