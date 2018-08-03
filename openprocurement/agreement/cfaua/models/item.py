from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    Item as BaseItem,
    ListType,
    CPVClassification,
    AdditionalClassification,
    Address,
    PeriodEndRequired,
    )


class Item(BaseItem):

    classification = ModelType(
        CPVClassification, required=True
    )
    additionalClassifications = ListType(
        ModelType(
            AdditionalClassification,
            default=list()
        )
    )
    description_en = StringType(
        required=True, min_length=1)
    deliveryDate = ModelType(
        PeriodEndRequired, required=True)
    deliveryAddress = ModelType(
        Address, required=True)