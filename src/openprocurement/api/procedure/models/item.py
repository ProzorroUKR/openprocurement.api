from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, FloatType, MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.constants import (
    ADDITIONAL_CLASSIFICATIONS_SCHEMES,
    CCCE_UA,
    CCCE_UA_SCHEME,
    CPV_CODES,
    CPV_NOT_CPV,
    DK_CODES,
    GMDN_2019,
    GMDN_2019_SCHEME,
    GMDN_2023,
    GMDN_2023_SCHEME,
    UA_ROAD,
    UA_ROAD_SCHEME,
)
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType, URLType


class Classification(Model):
    scheme = StringType(required=True)  # The classification scheme for the goods
    id = StringType(required=True)  # The classification ID from the Scheme used
    description = StringType(required=True)  # A description of the goods, services to be provided.
    description_en = StringType()
    description_ru = StringType()
    uri = URLType()


class CPVClassification(Classification):
    scheme = StringType(required=True, default="CPV", choices=["CPV", "ДК021"])
    id = StringType(required=True)

    def validate_id(self, data, code):
        if data.get("scheme") == "CPV" and code not in CPV_CODES:
            raise ValidationError("Value must be one of CPV codes")
        elif data.get("scheme") == "ДК021" and code not in DK_CODES:
            raise ValidationError("Value must be one of ДК021 codes")


class AdditionalClassification(Classification):
    def validate_id(self, data, value):
        if data["scheme"] == UA_ROAD_SCHEME and value not in UA_ROAD:
            raise ValidationError(f"{UA_ROAD_SCHEME} id not found in standards")
        if data["scheme"] == GMDN_2019_SCHEME and value not in GMDN_2019:
            raise ValidationError(f"{GMDN_2019_SCHEME} id not found in standards")
        if data["scheme"] == GMDN_2023_SCHEME and value not in GMDN_2023:
            raise ValidationError(f"{GMDN_2023_SCHEME} id not found in standards")
        if data["scheme"] == CCCE_UA_SCHEME and value not in CCCE_UA:
            raise ValidationError(f"{CCCE_UA_SCHEME} id not found in standards")

    def validate_description(self, data, value):
        if data["scheme"] == UA_ROAD_SCHEME and UA_ROAD.get(data["id"]) != value:
            raise ValidationError("{} description invalid".format(UA_ROAD_SCHEME))


def validate_scheme(obj, scheme):
    if scheme != "ДК021":
        raise ValidationError(BaseType.MESSAGES["choices"].format(["ДК021"]))


def validate_additional_classifications(obj, data, items):
    if (
        data["classification"]["id"] == CPV_NOT_CPV
        and items
        and not any(i.scheme in ADDITIONAL_CLASSIFICATIONS_SCHEMES for i in items or [])
    ):
        raise ValidationError(
            "One of additional classifications should be one of [{}].".format(
                ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES)
            )
        )


def validate_items_uniq(items, *args):
    if items:
        ids = [i.id for i in items]
        if len(ids) > len(set(ids)):
            raise ValidationError("Item id should be uniq for all items")


class Location(Model):
    latitude = BaseType(required=True)
    longitude = BaseType(required=True)
    elevation = BaseType()


class Item(Model):
    """A good, service, or work to be contracted."""

    id = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    description = StringType(required=True)  # A description of the goods, services to be provided.
    description_en = StringType()
    description_ru = StringType()
    classification = ModelType(CPVClassification)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True), default=[])
    quantity = FloatType(min_value=0)  # The number of units required
    deliveryLocation = ModelType(Location)
    relatedLot = MD5Type()
    relatedBuyer = MD5Type()


class TechFeatureItemMixin(Model):
    profile = StringType()
    category = StringType()

    def validate_profile(self, data, value):
        category = data.get("category")
        if value and not category:
            raise ValidationError("profile should be provided together only with category")
