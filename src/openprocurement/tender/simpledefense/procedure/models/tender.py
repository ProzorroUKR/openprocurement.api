from schematics.types import StringType

from openprocurement.tender.openuadefense.procedure.models.tender import (
    PatchTender as BasePatchTender,
)
from openprocurement.tender.openuadefense.procedure.models.tender import (
    PostTender as BasePostTender,
)
from openprocurement.tender.openuadefense.procedure.models.tender import (
    Tender as BaseTender,
)
from openprocurement.tender.simpledefense.constants import SIMPLE_DEFENSE


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[SIMPLE_DEFENSE], default=SIMPLE_DEFENSE)


class PatchTender(BasePatchTender):
    procurementMethodType = StringType(choices=[SIMPLE_DEFENSE])


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[SIMPLE_DEFENSE], required=True)
