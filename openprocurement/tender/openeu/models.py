from zope.interface import implementer
from schematics.types import StringType
from schematics.types.compound import ModelType, ListType
from schematics.exceptions import ValidationError
from openprocurement.api.models import ITender
from openprocurement.api.models import Tender as BaseTender
from openprocurement.api.models import Organization as BaseOrganization
from openprocurement.api.models import Identifier as BaseIdentifier
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import Award as BaseAward
from openprocurement.api.models import ContactPoint as BaseContactPoint
from openprocurement.api.models import validate_cpv_group, validate_items_uniq


class Item(BaseItem):
    """A good, service, or work to be contracted."""

    description_en = StringType(required=True, min_length=1)


class Identifier(BaseIdentifier):

    legalName_en = StringType(required=True, min_length=1)


class ContactPoint(BaseContactPoint):

    name_en = StringType(required=True, min_length=1)
    availableLanguage = StringType(required=True, min_length=1)


class Organization(BaseOrganization):
    """An organization."""

    name = StringType(required=True)
    name_en = StringType(required=True, min_length=1)
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    contactPoint = ListType(ModelType(ContactPoint, required=True), required=True)


class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """
    items = ListType(ModelType(Item))


@implementer(ITender)
class Tender(BaseTender):
    """ OpenEU tender model """

    procurementMethodType = StringType(default="aboveThresholdEU")
    title_en = StringType(required=True, min_length=1)

    items = ListType(ModelType(Item), required=True, min_size=1, validators=[validate_cpv_group, validate_items_uniq])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    awards = ListType(ModelType(Award), default=list())
    procuringEntity = ModelType(Organization, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
