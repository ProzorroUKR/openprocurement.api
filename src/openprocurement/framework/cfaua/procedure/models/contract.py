from uuid import uuid4

from schematics.types import MD5Type, StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.procedure.validation import validate_parameters_uniq
from openprocurement.framework.cfaua.procedure.models.organization import (
    ContractBusinessOrganization,
)
from openprocurement.framework.cfaua.procedure.models.parameter import Parameter
from openprocurement.framework.cfaua.procedure.models.unitprice import UnitPrice


class Contract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["active", "unsuccessful"])
    suppliers = ListType(ModelType(ContractBusinessOrganization, required=True))
    unitPrices = ListType(ModelType(UnitPrice, required=True))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
    parameters = ListType(ModelType(Parameter, required=True), default=list(), validators=[validate_parameters_uniq])
