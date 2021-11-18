from openprocurement.api.models import ValidationError, Value, Period, UNIT_CODES
from openprocurement.tender.core.procedure.models.base import (
    Model, ModelType, ListType, Address,
)
from openprocurement.tender.core.procedure.context import get_tender, get_now
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from schematics.types import StringType, MD5Type, FloatType, BaseType, URLType
from openprocurement.api.constants import (
    CPV_CODES,
    DK_CODES,
    CPV_BLOCK_FROM,
    UA_ROAD_SCHEME,
    UA_ROAD,
    GMDN_SCHEME,
    GMDN,
    UNIT_PRICE_REQUIRED_FROM,
    MULTI_CONTRACTS_REQUIRED_FROM,
)
from uuid import uuid4


class Location(Model):
    latitude = BaseType(required=True)
    longitude = BaseType(required=True)
    elevation = BaseType()


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
            raise ValidationError(BaseType.MESSAGES["choices"].format(CPV_CODES))
        elif data.get("scheme") == "ДК021" and code not in DK_CODES:
            raise ValidationError(BaseType.MESSAGES["choices"].format(DK_CODES))

    def validate_scheme(self, data, scheme):
        date = get_first_revision_date(get_tender(), default=get_now())
        if date > CPV_BLOCK_FROM and scheme != "ДК021":
            raise ValidationError(BaseType.MESSAGES["choices"].format(["ДК021"]))


class AdditionalClassification(Classification):
    def validate_id(self, data, value):
        if data["scheme"] == UA_ROAD_SCHEME and value not in UA_ROAD:
            raise ValidationError("{} id not found in standards".format(UA_ROAD_SCHEME))
        if data["scheme"] == GMDN_SCHEME and value not in GMDN:
            raise ValidationError("{} id not found in standards".format(GMDN_SCHEME))

    def validate_description(self, data, value):
        if data["scheme"] == UA_ROAD_SCHEME and UA_ROAD.get(data["id"]) != value:
            raise ValidationError("{} description invalid".format(UA_ROAD_SCHEME))


class Unit(Model):
    """Description of the unit which the good comes in e.g. hours, kilograms. Made up of a unit name, and the value of a single unit."""

    name = StringType()
    name_en = StringType()
    name_ru = StringType()
    value = ModelType(Value)
    code = StringType(required=True)

    def validate_code(self, data, value):
        validation_date = get_first_revision_date(get_tender(), default=get_now())
        if validation_date >= UNIT_PRICE_REQUIRED_FROM:
            if value not in UNIT_CODES:
                raise ValidationError(u"Code should be one of valid unit codes.")


class Item(Model):
    id = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    description = StringType(required=True)  # A description of the goods, services to be provided.
    description_en = StringType()
    description_ru = StringType()
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification), default=list)
    unit = ModelType(Unit)  # Description of the unit which the good comes in e.g. hours, kilograms
    quantity = FloatType()  # The number of units required
    deliveryDate = ModelType(Period)
    deliveryAddress = ModelType(Address)
    deliveryLocation = ModelType(Location)
    relatedLot = MD5Type()
    relatedBuyer = MD5Type()

    def validate_relatedBuyer(self, data, related_buyer):
        if not related_buyer:
            tender = get_tender()
            if (
                tender.get("buyers")
                and tender.get("status") != "draft"
                and get_first_revision_date(tender, default=get_now()) >= MULTI_CONTRACTS_REQUIRED_FROM
            ):
                raise ValidationError(BaseType.MESSAGES["required"])

    def validate_unit(self, data, value):
        if not value:
            tender = get_tender()
            validation_date = get_first_revision_date(tender, default=get_now())
            if validation_date >= UNIT_PRICE_REQUIRED_FROM:
                raise ValidationError(BaseType.MESSAGES["required"])

    def validate_quantity(self, data, value):
        if value is None:
            tender = get_tender()
            validation_date = get_first_revision_date(tender, default=get_now())
            if validation_date >= UNIT_PRICE_REQUIRED_FROM:
                raise ValidationError(BaseType.MESSAGES["required"])
