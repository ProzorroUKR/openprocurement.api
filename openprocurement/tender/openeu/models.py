from uuid import uuid4
from zope.interface import implementer
from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType, ListType
from schematics.transforms import blacklist
from schematics.exceptions import ValidationError
from openprocurement.api.models import ITender
from openprocurement.api.models import (Document, Model, Address, Period,
                                        IsoDateTimeType)
from openprocurement.api.models import Tender as BaseTender
from openprocurement.api.models import Identifier as BaseIdentifier
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import Bid as BaseBid
from openprocurement.api.models import Award as BaseAward
from openprocurement.api.models import ContactPoint as BaseContactPoint
from openprocurement.api.models import (validate_cpv_group, validate_items_uniq,
                                        schematics_embedded_role,
                                        schematics_default_role)


class Item(BaseItem):
    """A good, service, or work to be contracted."""

    description_en = StringType(required=True, min_length=1)


class Identifier(BaseIdentifier):

    legalName_en = StringType(required=True, min_length=1)


class ContactPoint(BaseContactPoint):

    name_en = StringType(required=True, min_length=1)
    availableLanguage = StringType(required=True, min_length=1)


class Organization(Model):
    """An organization."""
    class Options:
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    name = StringType(required=True)
    name_en = StringType(required=True, min_length=1)
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(Address, required=True)
    contactPoints = ListType(ModelType(ContactPoint, required=True),
                             required=True)


class Bid(BaseBid):
    status = StringType(choices=['pending', 'active', 'invalid', 'deleted'],
                        default='pending')


class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """
    items = ListType(ModelType(Item))


class Qualification(Model):
    """ Pre-Qualification """

    class Options:
        roles = {
            'create': blacklist('id', 'status', 'documents', 'date'),
            'edit': blacklist('id', 'documents'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    awardID = StringType(required=True)
    status = StringType(choices=['pending', 'active', 'cancelled'], default='pending')
    period = ModelType(Period)
    date = IsoDateTimeType()
    documents = ListType(ModelType(Document), default=list())


@implementer(ITender)
class Tender(BaseTender):
    """ OpenEU tender model """

    procurementMethodType = StringType(default="aboveThresholdEU")
    title_en = StringType(required=True, min_length=1)

    items = ListType(ModelType(Item), required=True, min_size=1, validators=[validate_cpv_group, validate_items_uniq])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    awards = ListType(ModelType(Award), default=list())
    procuringEntity = ModelType(Organization, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the tender.
    qualifications = ListType(ModelType(Qualification), default=list())
    qualificationPeriod = ModelType(Period)
    # status = StringType(choices=['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction',
                                  # 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')

