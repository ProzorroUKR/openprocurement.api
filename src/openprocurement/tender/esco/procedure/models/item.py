from openprocurement.api.models import ValidationError, Model
from openprocurement.tender.core.validation import validate_ua_road, validate_gmdn
from openprocurement.tender.core.procedure.models.address import Address
from openprocurement.tender.core.procedure.models.base import ModelType, ListType
from openprocurement.tender.core.procedure.models.period import Period
from openprocurement.tender.core.procedure.models.item import CPVClassification, AdditionalClassification, Location
from openprocurement.tender.core.procedure.context import get_tender, get_now
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from schematics.types import StringType, MD5Type
from openprocurement.api.constants import (
    CPV_ITEMS_CLASS_FROM,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017,
    ADDITIONAL_CLASSIFICATIONS_SCHEMES,
)
from uuid import uuid4


class Item(Model):
    id = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    description = StringType(required=True)  # A description of the goods, services to be provided.
    description_en = StringType()
    description_ru = StringType()
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification))
    deliveryAddress = ModelType(Address)
    deliveryLocation = ModelType(Location)
    relatedLot = MD5Type()
    relatedBuyer = MD5Type()

    def validate_additionalClassifications(self, data, items):
        tender = get_tender()
        tender_date = get_first_revision_date(tender, default=get_now())
        tender_from_2017 = tender_date > CPV_ITEMS_CLASS_FROM
        classification_id = data["classification"]["id"]
        not_cpv = classification_id == "99999999-9"
        required = tender_date < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM and not_cpv
        if not items and (not tender_from_2017 or tender_from_2017 and not_cpv and required):
            raise ValidationError("This field is required.")
        elif (
            tender_from_2017
            and not_cpv
            and items
            and not any(i["scheme"] in ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017 for i in items)
        ):
            raise ValidationError(
                "One of additional classifications should be one of [{0}].".format(
                    ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES_2017)
                )
            )
        elif (
            not tender_from_2017
            and items
            and not any(i["scheme"] in ADDITIONAL_CLASSIFICATIONS_SCHEMES for i in items)
        ):
            raise ValidationError(
                "One of additional classifications should be one of [{0}].".format(
                    ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES)
                )
            )
        if items is not None:
            validate_ua_road(classification_id, items)
            validate_gmdn(classification_id, items)

