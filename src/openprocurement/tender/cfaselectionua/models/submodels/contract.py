from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from schematics.types import StringType
from openprocurement.tender.core.models import ContractValue
from openprocurement.tender.core.models import Contract as BaseContract
from openprocurement.api.utils import get_now
from openprocurement.api.models import Model, ListType, Document
from openprocurement.tender.cfaselectionua.models.submodels.item import Item


class Contract(BaseContract):
    value = ModelType(ContractValue)
    awardID = StringType(required=True)
    documents = ListType(ModelType(Document, required=True), default=list)
    items = ListType(ModelType(Item))

    def validate_dateSigned(self, data, value):
        parent = data["__parent__"]
        if value and isinstance(parent, Model) and value > get_now():
            raise ValidationError("Contract signature date can't be in the future")
