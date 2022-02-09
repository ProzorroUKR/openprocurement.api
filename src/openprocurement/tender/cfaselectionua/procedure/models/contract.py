from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from schematics.types import StringType
from openprocurement.tender.core.procedure.models.contract import Contract as BaseContract, ContractValue
from openprocurement.tender.core.procedure.context import get_now
from openprocurement.api.models import Model, ListType, Document
from openprocurement.tender.core.procedure.models.item import Item


class Contract(BaseContract):
    value = ModelType(ContractValue)
    awardID = StringType(required=True)
    documents = ListType(ModelType(Document, required=True))
    items = ListType(ModelType(Item))

    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError("Contract signature date can't be in the future")
