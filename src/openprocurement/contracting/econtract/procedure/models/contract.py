from schematics.types import StringType, EmailType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.models import Model, ListType, IsoDateTimeType
from openprocurement.api.constants import SCALE_CODES
from openprocurement.tender.core.models import PROCURING_ENTITY_KINDS

from openprocurement.contracting.core.procedure.models.contract_base import (
    Organization,
    BusinessOrganization as BaseBusinessOrganization,
    ContactPoint,
    AmountPaid,
    BasePostContract,
    BasePatchContract,
    BaseContract,
)


class SignerInfo(Model):
    name = StringType(required=True)
    email = EmailType(required=True)
    telephone = StringType(required=True)
    iban = StringType(min_length=15, max_length=33)
    signerDocument = StringType(required=True)
    organization_status = StringType(required=True)


class Buyer(Organization):
    """An organization."""
    scale = StringType(choices=SCALE_CODES)
    kind = StringType(choices=PROCURING_ENTITY_KINDS)
    contactPoint = ModelType(ContactPoint)
    signerInfo = ModelType(SignerInfo)


class BusinessOrganization(BaseBusinessOrganization):
    signerInfo = ModelType(SignerInfo)


class PostContract(BasePostContract):
    """
    Model only for auto-creating contract
    """

    @serializable
    def status(self):
        return "pending"

    amountPaid = ModelType(AmountPaid)
    buyer = ModelType(
        Buyer, required=True
    )
    bid_owner = StringType(required=True)
    bid_token = StringType(required=True)


class PatchContract(BasePatchContract):
    status = StringType(choices=["pending",  "terminated", "active", "cancelled"])
    dateSigned = IsoDateTimeType()
    buyer = ModelType(Buyer)


class PatchSupplierContract(Model):
    suppliers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)


class AdministratorPatchContract(Model):
    status = StringType(choices=["pending", "terminated", "active", "cancelled"])
    suppliers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    buyer = ModelType(Buyer)
    mode = StringType(choices=["test"])


class Contract(BaseContract):
    status = StringType(choices=["pending", "terminated", "active", "cancelled"])
    buyer = ModelType(
        Buyer, required=True
    )
    suppliers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)

    bid_owner = StringType(required=True)
    bid_token = StringType(required=True)
