from openprocurement.api.models import IsoDateTimeType, Value, Period, Model
from openprocurement.tender.core.procedure.models.base import ModelType, ListType
from openprocurement.tender.core.procedure.models.organization import BusinessOrganization
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.item import Item
from schematics.types import StringType, MD5Type, FloatType
from uuid import uuid4


class ContractValue(Value):
    amountNet = FloatType(min_value=0)


class Contract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    buyerID = StringType()
    awardID = StringType(required=True)
    contractID = StringType()
    contractNumber = StringType()
    title = StringType()  # Contract title
    title_en = StringType()
    title_ru = StringType()
    description = StringType()  # Contract description
    description_en = StringType()
    description_ru = StringType()
    status = StringType(choices=["pending", "pending.winner-signing", "terminated", "active", "cancelled"],
                        default="pending")
    period = ModelType(Period)
    value = ModelType(ContractValue)
    dateSigned = IsoDateTimeType()
    documents = ListType(ModelType(Document, required=True), default=list)
    items = ListType(ModelType(Item))
    suppliers = ListType(ModelType(BusinessOrganization), min_size=1, max_size=1)
    date = IsoDateTimeType()
