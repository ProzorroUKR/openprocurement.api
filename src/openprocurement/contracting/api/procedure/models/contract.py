from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType, IsoDateTimeType

from openprocurement.contracting.core.procedure.models.contract import (
    BaseContract,
    BasePatchContract,
    BasePostContract,
)
from openprocurement.contracting.core.procedure.models.value import AmountPaid
from openprocurement.contracting.core.procedure.models.organization import BusinessOrganization, ProcuringEntity


class PostContract(BasePostContract):
    status = StringType(choices=["terminated", "active"], default="active")
    dateSigned = IsoDateTimeType()
    procuringEntity = ModelType(ProcuringEntity, required=True)


class PatchContract(BasePatchContract):
    terminationDetails = StringType()
    amountPaid = ModelType(AmountPaid)


class AdministratorPatchContract(Model):
    status = StringType(choices=["terminated", "active"])
    suppliers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    procuringEntity = ModelType(ProcuringEntity)
    mode = StringType(choices=["test"])


class Contract(BaseContract):
    """Contract"""

    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
