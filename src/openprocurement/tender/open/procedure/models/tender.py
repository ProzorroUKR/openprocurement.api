from schematics.types import StringType

from openprocurement.tender.core.procedure.models.tender import PostTender, Tender
from openprocurement.tender.open.constants import OPEN_TENDERING, OPEN_TENDERING_SUBTYPES


class OpenTenderingPostTender(PostTender):
    """
    The UA/EU variant of the procedure is set by procurementMethodSubtype
    at the tender creation; the field is not in the patch model, so it can't be changed afterwards
    """

    procurementMethodType = StringType(choices=[OPEN_TENDERING], default=OPEN_TENDERING)
    procurementMethodSubtype = StringType(choices=OPEN_TENDERING_SUBTYPES, required=True)


class OpenTenderingTender(Tender):
    procurementMethodType = StringType(choices=[OPEN_TENDERING], required=True)
    procurementMethodSubtype = StringType(choices=OPEN_TENDERING_SUBTYPES, required=True)
