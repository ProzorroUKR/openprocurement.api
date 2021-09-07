from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from uuid import uuid4
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    Period,
)
from openprocurement.tender.core.models import Feature, validate_features_uniq
from openprocurement.tender.cfaua.models.submodels.contract import Contract
from openprocurement.tender.cfaua.models.submodels.item import Item


class Agreement(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    agreementID = StringType()
    agreementNumber = StringType()
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    items = ListType(ModelType(Item, required=True))
    period = ModelType(Period)
    status = StringType(choices=["pending", "active", "cancelled", "unsuccessful"], default="pending")
    contracts = ListType(ModelType(Contract, required=True))
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
