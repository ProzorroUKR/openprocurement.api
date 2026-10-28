from schematics.types import StringType

from openprocurement.api.procedure.types import ListType
from openprocurement.tender.core.procedure.models.tender import PostTender, Tender
from openprocurement.tender.open.constants import (
    OPEN_TENDERING,
    OPEN_TENDERING_PROCUREMENT_ASPECTS,
)


class OpenTenderingPostTender(PostTender):
    """
    The UA/EU variant of the procedure is set by procurementAspects
    at the tender creation; the field is not in the patch model, so it can't be changed afterwards
    (the allowed combinations of the aspects are validated by the state class)
    """

    procurementMethodType = StringType(choices=[OPEN_TENDERING], default=OPEN_TENDERING)
    procurementAspects = ListType(StringType(choices=OPEN_TENDERING_PROCUREMENT_ASPECTS), required=True, min_size=1)


class OpenTenderingTender(Tender):
    procurementMethodType = StringType(choices=[OPEN_TENDERING], required=True)
    procurementAspects = ListType(StringType(choices=OPEN_TENDERING_PROCUREMENT_ASPECTS), required=True, min_size=1)
