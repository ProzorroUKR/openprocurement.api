from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.models import Model, ListType, IsoDateTimeType

from openprocurement.contracting.core.procedure.models.contract_base import (
    ProcuringEntity,
    BusinessOrganization,
    BaseContract,
    BasePatchContract,
    BasePostContract,
)


class PostContract(BasePostContract):
    status = StringType(choices=["terminated", "active"], default="active")
    dateSigned = IsoDateTimeType()
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )


class PatchContract(BasePatchContract):
    pass


class AdministratorPatchContract(Model):
    status = StringType(choices=["terminated", "active"])
    suppliers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    procuringEntity = ModelType(ProcuringEntity)
    mode = StringType(choices=["test"])


class Contract(BaseContract):
    """ Contract """

    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.

