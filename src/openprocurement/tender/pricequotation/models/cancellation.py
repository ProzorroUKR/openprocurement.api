from uuid import uuid4
from schematics.types import MD5Type, StringType
from schematics.transforms import whitelist
from schematics.types.compound import ModelType

from openprocurement.api.utils import get_now
from openprocurement.api.models import IsoDateTimeType, ListType
from openprocurement.tender.core.models import Model
from openprocurement.api.models import\
    schematics_default_role, schematics_embedded_role
from openprocurement.tender.pricequotation.models.document import\
    Document


class Cancellation(Model):
    class Options:
        roles = {
            "create": whitelist(
                "reason",
                "reasonType",
                "cancellationOf",
            ),
            "edit": whitelist("status", "reasonType"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    reason = StringType(required=True)
    reason_en = StringType()
    reason_ru = StringType()
    date = IsoDateTimeType(default=get_now)
    status = StringType(
        choices=["draft", "unsuccessful", "active"],
        default='draft'
    )
    documents = ListType(ModelType(Document, required=True), default=list())
    cancellationOf = StringType(
        required=True,
        choices=["tender"],
        default="tender"
        )
    reasonType = StringType(
        choices=["noDemand", "unFixable", "forceMajeure", "expensesCut"],
        )
