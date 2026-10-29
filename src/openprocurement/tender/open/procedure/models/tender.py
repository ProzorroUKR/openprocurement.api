from schematics.types import BaseType, StringType

from openprocurement.tender.core.procedure.models.tender import PostTender, Tender
from openprocurement.tender.open.constants import OPEN_TENDERING


class OpenTenderingPostTender(PostTender):
    """
    The UA/EU variant of the procedure is set by procedure.euPublished
    at the tender creation; the field is not in the patch model, so it can't be changed afterwards
    (the structure of procedure is validated by the state class against its schema from standards)
    """

    procurementMethodType = StringType(choices=[OPEN_TENDERING], default=OPEN_TENDERING)
    procedure = BaseType(required=True)


class OpenTenderingTender(Tender):
    procurementMethodType = StringType(choices=[OPEN_TENDERING], required=True)
    procedure = BaseType(required=True)
