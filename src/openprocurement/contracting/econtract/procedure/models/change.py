from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import ContractValue
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.utils import get_now
from openprocurement.api.validation import validate_items_uniq
from openprocurement.contracting.core.procedure.models.change import BaseChange
from openprocurement.contracting.core.procedure.models.item import Item
from openprocurement.contracting.core.procedure.models.milestone import (
    ContractMilestone,
)
from openprocurement.contracting.econtract.procedure.models.cancellation import (
    Cancellation,
)
from openprocurement.contracting.econtract.procedure.models.document import Document


class Modifications(Model):
    title = StringType()
    title_en = StringType()
    description = StringType()
    description_en = StringType()

    period = ModelType(Period)
    value = ModelType(ContractValue)

    items = ListType(ModelType(Item, required=True))
    contractNumber = StringType()
    # amountPaid ???
    milestones = ListType(ModelType(ContractMilestone, required=True), validators=[validate_items_uniq])


class PostChange(BaseChange):
    modifications = ModelType(Modifications, required=True)

    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def status(self):
        return "pending"

    @serializable
    def date(self):
        return get_now().isoformat()


class Change(BaseChange):
    id = MD5Type(required=True)
    status = StringType(choices=["pending", "active", "cancelled"])
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    modifications = ModelType(Modifications, required=True)
    documents = ListType(ModelType(Document, required=True))
    cancellations = ListType(ModelType(Cancellation, required=True))
    author = StringType()
