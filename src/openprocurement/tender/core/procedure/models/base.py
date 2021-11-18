from schematics.exceptions import ValidationError
from schematics.types import (
    StringType,
    URLType,
    BaseType,
    EmailType,
    FloatType,
)
from schematics.transforms import export_loop
from schematics.types.compound import ModelType as BaseModelType,  ListType as BaseListType
from openprocurement.api.models import Model, DecimalType as BaseDecimalType
from openprocurement.api.utils import get_now
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.api.constants import (
    ORA_CODES,
    SCALE_CODES,
    ORGANIZATION_SCALE_FROM,
    VALIDATE_TELEPHONE_FROM,
    COUNTRIES,
    UA_REGIONS,
    VALIDATE_ADDRESS_FROM,
    VALIDATE_CURRENCY_FROM,
    CURRENCIES,
)
from decimal import Decimal
from logging import getLogger
import re

LOGGER = getLogger(__name__)


class ListType(BaseListType):
    """
    Schematics ListType export_loop returns None instead of the empty list
    if an empty list passed to model.
    So you have to pass serialize_when_none , like
    ListType(ModelType(Parameter, required=True), serialize_when_none=True, ...
    and then converting '[]' to 'None' won't happen.
    1) It's not obvious
    2) If we use model to validate user input data, we do want to know they sending this empty list
    """
    def allow_none(self):
        return True


class ModelType(BaseModelType):

    def __init__(self, model_class, **kwargs):
        name = kwargs.pop("name", None)
        if name:
            model_class.__name__ = name
        super().__init__(model_class, **kwargs)


class NoneAllowedModelType(BaseModelType):
    """
    without overwriting export_loop
    the following data provided to model {'auctionPeriod': {'startDate': None}}
    would result with None as output from .serialize()
    """

    def export_loop(self, model_instance, field_converter,
                    role=None, print_none=False):
        """
        Calls the main `export_loop` implementation because they are both
        supposed to operate on models.
        """
        if isinstance(model_instance, self.model_class):
            model_class = model_instance.__class__
        else:
            model_class = self.model_class

        shaped = export_loop(model_class, model_instance,
                             field_converter,
                             role=role, print_none=True)

        if shaped and len(shaped) == 0 and self.allow_none():
            return shaped
        elif shaped:
            return shaped
        elif print_none:
            return shaped


class DecimalType(BaseDecimalType):
    def to_primitive(self, *args, **kwargs):
        value = super().to_primitive(*args, **kwargs)
        if isinstance(value, Decimal):
            return '{0:f}'.format(value)
        return value


# Patch and Post models differences:
# patch models usually don't have required and default fields,
# patch models assume that the object already valid

class PatchContactPoint(Model):
    name = StringType()
    name_en = StringType()
    name_ru = StringType()
    email = EmailType()
    telephone = StringType()
    faxNumber = StringType()
    url = URLType()

    def validate_telephone(self, _, value):
        tender = get_tender()
        if (
            get_first_revision_date(tender, default=get_now()) >= VALIDATE_TELEPHONE_FROM
            and value
            and re.match("^(\+)?[0-9]{2,}(,( )?(\+)?[0-9]{2,})*$", value) is None
        ):
            raise ValidationError(u"wrong telephone format (could be missed +)")


class PostContactPoint(PatchContactPoint):
    name = StringType(required=True)

    def validate_email(self, data, value):
        if not value and not data.get("telephone"):
            raise ValidationError("telephone or email should be present")


class PatchAddress(Model):
    streetAddress = StringType()
    locality = StringType()
    region = StringType()
    postalCode = StringType()
    countryName = StringType()
    countryName_en = StringType()
    countryName_ru = StringType()


class PostAddress(PatchAddress):
    countryName = StringType(required=True)

    def validate_countryName(self, _, value):
        if not self.skip_address_validation():
            if value not in COUNTRIES:
                raise ValidationError("field address:countryName not exist in countries catalog")

    def validate_region(self, data, value):
        if data["countryName"] == "Україна":
            if not self.skip_address_validation():
                if value and value not in UA_REGIONS:
                    raise ValidationError("field address:region not exist in ua_regions catalog")

    @staticmethod
    def skip_address_validation():
        tender = get_tender()  # TODO add methods for contracts, agreements, etc
        if tender["procurementMethodType"] in ('competitiveDialogueUA.stage2', 'competitiveDialogueEU.stage2',
                                               'closeFrameworkAgreementSelectionUA'):
            return True

        if get_first_revision_date(tender, default=get_now()) < VALIDATE_ADDRESS_FROM:
            return True
        return False


class Address(PostAddress):
    pass


class PatchIdentifier(Model):
    scheme = StringType(
        choices=ORA_CODES
    )  # The scheme that holds the unique identifiers used to identify the item being identified.
    id = BaseType()  # The identifier of the organization in the selected scheme.
    legalName = StringType()  # The legally registered name of the organization.
    legalName_en = StringType()
    legalName_ru = StringType()
    uri = URLType()  # A URI to identify the organization.


class PostIdentifier(PatchIdentifier):
    replace_name = "Identifier"
    scheme = StringType(required=True, choices=ORA_CODES)
    id = BaseType(required=True)


class Identifier(PostIdentifier):
    pass


class PatchOrganization(Model):
    name = StringType()
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(PatchIdentifier, name="Identifier")
    additionalIdentifiers = ListType(ModelType(PatchIdentifier))
    address = ModelType(PatchAddress)
    contactPoint = ModelType(PatchContactPoint)


class PostOrganization(PatchOrganization):
    name = StringType(required=True)
    identifier = ModelType(PostIdentifier, name="Identifier", required=True)
    additionalIdentifiers = ListType(ModelType(PostIdentifier))
    address = ModelType(PostAddress, required=True)
    contactPoint = ModelType(PostContactPoint, required=True)


class Organization(PostOrganization):
    pass


class PatchBusinessOrganization(PatchOrganization):
    scale = StringType(choices=SCALE_CODES)


class PostBusinessOrganization(PostOrganization, PatchBusinessOrganization):
    def validate_scale(self, data, value):
        tender = get_tender()
        validation_date = get_first_revision_date(tender, default=get_now())
        if validation_date >= ORGANIZATION_SCALE_FROM and value is None:
            raise ValidationError(BaseType.MESSAGES["required"])


class BusinessOrganization(PostBusinessOrganization):
    pass


class BaseBid(Model):
    pass


class BaseAward(Model):
    pass


def validate_object_id_uniq(objs, *args):
    if objs:
        obj_name = objs[0].__class__.__name__
        obj_name_multiple = obj_name[0].lower() + obj_name[1:]
        ids = [i.id for i in objs]
        if [i for i in set(ids) if ids.count(i) > 1]:
            raise ValidationError("{} id should be uniq for all {}s".format(obj_name, obj_name_multiple))


class Guarantee(Model):
    amount = FloatType(required=True, min_value=0)  # Amount as a number.
    currency = StringType(required=True, default="UAH", max_length=3, min_length=3)  # 3-letter ISO 4217 format.

    def validate_currency(self, data, value):
        is_valid_date = get_first_revision_date(get_tender(), default=get_now()) >= VALIDATE_CURRENCY_FROM
        if is_valid_date and value not in CURRENCIES:
            raise ValidationError(f"Currency must be only {', '.join(CURRENCIES)}.")
