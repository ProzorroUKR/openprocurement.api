from schematics.types import StringType

from openprocurement.api.procedure.models.guarantee import Guarantee as BaseGuarantee


class Guarantee(BaseGuarantee):
    pass


class PostGuarantee(Guarantee):
    currency = StringType(required=True, default="UAH", max_length=3, min_length=3)
