from uuid import uuid4

from pydantic import Field

from openprocurement.api.constants import (
    ATC_SCHEME,
    CPV_PHARM_PREFIX,
    CPV_PHARM_PRODUCTS,
    GMDN_2019_SCHEME,
    GMDN_2023_SCHEME,
    GMDN_CPV_PREFIXES,
    INN_SCHEME,
    UA_ROAD_CPV_PREFIXES,
    UA_ROAD_SCHEME,
)
from openprocurement.api.constants_env import (
    MULTI_CONTRACTS_REQUIRED_FROM,
)
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.models.item import (
    AdditionalClassification,
    CPVClassification,
    Location,
    validate_additional_classifications,
    validate_ccce_ua,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.unit import Unit
from openprocurement.api.procedure.types import (
    MD5,
)
from openprocurement.api.procedure.utils import is_obj_const_active
from openprocurement.api.utils import is_gmdn_classification, is_ua_road_classification


class BaseItem(Model):
    id: str = Field(default_factory=lambda: uuid4().hex, min_length=1)
    description: str
    description_en: str | None = None
    description_ru: str | None = None
    unit: Unit | None = None
    quantity: float | None = Field(None, ge=0)
    relatedLot: MD5 | None = None


class Item(BaseItem):
    """
    Tender / award / agreement item. Procedure-specific rules (required delivery, unit, quantity,
    relatedLot being allowed, profile/category being required) live in the state classes.
    """

    classification: CPVClassification
    additionalClassifications: list[AdditionalClassification] | None = None
    deliveryDate: Period | None = None
    deliveryAddress: Address | None = None
    deliveryLocation: Location | None = None
    relatedLot: MD5 | None = None
    relatedBuyer: MD5 | None = None
    profile: str | None = None
    category: str | None = None
    product: str | None = None

    @model_field_validator("additionalClassifications")
    def validate_additional_classifications(self, items):
        validate_additional_classifications(self.classification, items)
        if items is not None:
            classification_id = self.classification.id
            validate_ua_road(classification_id, items)
            validate_gmdn(classification_id, items)
            validate_ccce_ua(items)

    @model_field_validator("profile")
    def validate_profile(self, value):
        category = self.category
        if value and (not category):
            raise ValidationError("profile should be provided together only with category")


def validate_related_buyer_in_items(tender, items):
    if (
        tender.status != "draft"
        and getattr(tender, "buyers", None)  # not a field of all the tenders
        and is_obj_const_active(get_tender(), MULTI_CONTRACTS_REQUIRED_FROM)
    ):
        for i in items or []:
            if not i.relatedBuyer:
                raise ValidationError([{"relatedBuyer": ["This field is required."]}])


def validate_classification_id(items, *args):
    for item in items:
        schemes = [x.scheme for x in item.additionalClassifications or []]
        schemes_inn_count = schemes.count(INN_SCHEME)
        if item.classification.id == CPV_PHARM_PRODUCTS and schemes_inn_count != 1:
            raise ValidationError(
                "Item with classification.id={} have to contain exactly one additionalClassifications "
                "with scheme={}".format(CPV_PHARM_PRODUCTS, INN_SCHEME)
            )
        if item.classification.id.startswith(CPV_PHARM_PREFIX) and schemes_inn_count > 1:
            raise ValidationError(
                "Item with classification.id that starts with {} and contains additionalClassification "
                "objects have to contain no more than one additionalClassifications "
                "with scheme={}".format(CPV_PHARM_PREFIX, INN_SCHEME)
            )


class LocalizationItem(BaseItem):
    product: str | None = None


def validate_gmdn(classification_id, additional_classifications):
    gmdn_count = sum(1 for i in additional_classifications if i.scheme in (GMDN_2023_SCHEME, GMDN_2019_SCHEME))
    if is_gmdn_classification(classification_id):
        inn_anc_count = sum(1 for i in additional_classifications if i.scheme in [INN_SCHEME, ATC_SCHEME])
        if 0 not in [inn_anc_count, gmdn_count]:
            raise ValidationError(
                "Item shouldn't have additionalClassifications with both schemes {}/{} and {}".format(
                    INN_SCHEME, ATC_SCHEME, GMDN_2019_SCHEME
                )
            )
        if gmdn_count > 1:
            raise ValidationError(
                "Item shouldn't have more than 1 additionalClassification with scheme {}".format(GMDN_2019_SCHEME)
            )
    elif gmdn_count != 0:
        raise ValidationError(
            "Item shouldn't have additionalClassification with scheme {} for cpv not starts with {}".format(
                GMDN_2019_SCHEME, ", ".join(GMDN_CPV_PREFIXES)
            )
        )


def validate_ua_road(classification_id, additional_classifications):
    road_count = sum(1 for i in additional_classifications if i.scheme == UA_ROAD_SCHEME)
    if is_ua_road_classification(classification_id):
        if road_count > 1:
            raise ValidationError(
                "Item shouldn't have more than 1 additionalClassification with scheme {}".format(UA_ROAD_SCHEME)
            )
    elif road_count != 0:
        raise ValidationError(
            "Item shouldn't have additionalClassification with scheme {} for cpv not starts with {}".format(
                UA_ROAD_SCHEME, ", ".join(UA_ROAD_CPV_PREFIXES)
            )
        )
