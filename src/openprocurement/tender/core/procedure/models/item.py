from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, FloatType, MD5Type, StringType

from openprocurement.api.constants import (
    CPV_PHARM_PRODUCTS,
    INN_SCHEME,
    MULTI_CONTRACTS_REQUIRED_FROM,
    UNIT_CODE_REQUIRED_FROM,
    UNIT_PRICE_REQUIRED_FROM,
)
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.item import AdditionalClassification
from openprocurement.api.procedure.models.item import (
    CPVClassification as BaseCPVClassification,
)
from openprocurement.api.procedure.models.item import (
    Location,
    validate_additional_classifications,
    validate_scheme,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.api.procedure.utils import is_obj_const_active
from openprocurement.tender.core.procedure.models.address import Address
from openprocurement.tender.core.procedure.models.unit import Unit
from openprocurement.tender.core.procedure.validation import (
    validate_gmdn,
    validate_ua_road,
)


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, data, scheme):
        validate_scheme(get_tender(), scheme)


class BaseItem(Model):
    id = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    description = StringType(required=True)  # A description of the goods, services to be provided.
    description_en = StringType()
    description_ru = StringType()
    unit = ModelType(Unit)  # Description of the unit which the good comes in e.g. hours, kilograms
    quantity = FloatType(min_value=0)  # The number of units required
    relatedLot = MD5Type()

    def validate_quantity(self, data, value):
        if value is None:
            if is_obj_const_active(get_tender(), UNIT_PRICE_REQUIRED_FROM):
                raise ValidationError(BaseType.MESSAGES["required"])


class Item(BaseItem):
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification))
    deliveryDate = ModelType(Period)
    deliveryAddress = ModelType(Address)
    deliveryLocation = ModelType(Location)
    relatedLot = MD5Type()
    relatedBuyer = MD5Type()

    def validate_unit(self, data, value):
        if not value:
            if is_obj_const_active(get_tender(), UNIT_CODE_REQUIRED_FROM):
                raise ValidationError(BaseType.MESSAGES["required"])

    def validate_additionalClassifications(self, data, items):
        validate_additional_classifications(get_tender(), data, items)
        if items is not None:
            classification_id = data["classification"]["id"]
            validate_ua_road(classification_id, items)
            validate_gmdn(classification_id, items)


class RelatedBuyerMixing:
    """
    Add this mixing to tender or contract
    """

    def validate_items(self, data, items):
        tender_data = get_tender() or data
        if (
            data.get("status", tender_data.get("status")) != "draft"
            and data.get("buyers", tender_data.get("buyers"))
            and is_obj_const_active(tender_data, MULTI_CONTRACTS_REQUIRED_FROM)
        ):
            for i in items or []:
                if not i.relatedBuyer:
                    raise ValidationError(BaseType.MESSAGES["required"])


def validate_related_buyer_in_items(data, items):
    if (
        data["status"] != "draft"
        and data.get("buyers")
        and is_obj_const_active(get_tender(), MULTI_CONTRACTS_REQUIRED_FROM)
    ):
        for i in items or []:
            if not i.relatedBuyer:
                raise ValidationError([{'relatedBuyer': ['This field is required.']}])


def validate_classification_id(items, *args):
    for item in items:
        schemes = [x.scheme for x in item.additionalClassifications or []]
        schemes_inn_count = schemes.count(INN_SCHEME)
        if item.classification.id == CPV_PHARM_PRODUCTS and schemes_inn_count != 1:
            raise ValidationError(
                "Item with classification.id={} have to contain exactly one additionalClassifications "
                "with scheme={}".format(CPV_PHARM_PRODUCTS, INN_SCHEME)
            )
        if item.classification.id.startswith(CPV_PHARM_PRODUCTS[:3]) and schemes_inn_count > 1:
            raise ValidationError(
                "Item with classification.id that starts with {} and contains additionalClassification "
                "objects have to contain no more than one additionalClassifications "
                "with scheme={}".format(CPV_PHARM_PRODUCTS[:3], INN_SCHEME)
            )


def validate_items_uniq(items, *args):
    if items:
        ids = [i.id for i in items]
        if len(ids) > len(set(ids)):
            raise ValidationError("Item id should be uniq for all items")
