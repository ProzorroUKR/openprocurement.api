from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.transforms import whitelist
from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import (
    Item as BaseItem,
    ListType,
    CPVClassification,
    Model,
    AdditionalClassification,
    Unit,
    Address,
    PeriodEndRequired,
    schematics_default_role,
    schematics_embedded_role
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