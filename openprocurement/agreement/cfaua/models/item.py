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

    class Options:
        roles = {
            'edit_active': whitelist(
            'description', 'description_en', 'description_ru', 'unit', 'deliveryDate',
            'deliveryAddress', 'deliveryLocation', 'quantity', 'id'),
            'view': schematics_default_role,
            'embedded': schematics_embedded_role,
        }

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