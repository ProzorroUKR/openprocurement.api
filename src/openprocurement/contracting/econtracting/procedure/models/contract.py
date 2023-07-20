from uuid import uuid4

from schematics.types import StringType, BaseType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.constants import SCALE_CODES
from openprocurement.api.models import Period, BaseContract
from openprocurement.api.models import Organization as BaseOrganization
from openprocurement.api.models import ContactPoint as BaseContactPoint
from openprocurement.api.models import CPVClassification as BaseCPVClassification
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import Address as BaseAddress
from openprocurement.api.models import AdditionalClassification as BaseAdditionalClassification
from openprocurement.api.models import Model, ListType, IsoDateTimeType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.models import Tender, ContractValue, PROCURING_ENTITY_KINDS
from openprocurement.api.models import Unit as BaseUnit

from openprocurement.contracting.api.procedure.models.transaction import Transaction
from openprocurement.contracting.api.procedure.models.document import Document
from openprocurement.contracting.api.procedure.models.change import Change
from openprocurement.contracting.api.procedure.models.contract import Organization, ContactPoint, Item, AmountPaid


class BusinessOrganization(Organization):
    """An organization."""
    scale = StringType(choices=SCALE_CODES)
    kind = StringType(choices=PROCURING_ENTITY_KINDS)
    contactPoint = ModelType(ContactPoint)


class PostContract(Model):
    """
    Model only for auto-creating contract
    """
    @serializable
    def owner_token(self):
        return uuid4().hex

    @serializable
    def transfer_token(self):
        return uuid4().hex

    @serializable
    def status(self):
        return "pending"

    id = StringType()
    _id = StringType(deserialize_from=['id', 'doc_id'])
    awardID = StringType()
    contractID = StringType()
    contractNumber = StringType()
    period = ModelType(Period)
    value = ModelType(ContractValue)
    amountPaid = ModelType(AmountPaid)
    items = ListType(ModelType(Item, required=True))
    documents = ListType(ModelType(Document, required=True))
    suppliers = ListType(ModelType(BusinessOrganization), min_size=1, max_size=1)
    buyer = ModelType(
        BusinessOrganization, required=True
    )
    owner = StringType()
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)
    mode = StringType(choices=["test"])
