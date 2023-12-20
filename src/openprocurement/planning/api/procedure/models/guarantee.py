from schematics.types import StringType

from openprocurement.api.procedure.models.guarantee import (
    Guarantee as BaseGuarantee,
    validate_currency,
)
from openprocurement.planning.api.procedure.context import get_plan


class Guarantee(BaseGuarantee):
    def validate_currency(self, guarantee, currency):
        validate_currency(get_plan(), guarantee, currency)


class PostGuarantee(Guarantee):
    currency = StringType(required=True, default="UAH", max_length=3, min_length=3)
