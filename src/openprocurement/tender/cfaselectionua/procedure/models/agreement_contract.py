from uuid import uuid4
from openprocurement.tender.cfaselectionua.procedure.models.organization import BusinessOrganization
from openprocurement.tender.cfaselectionua.procedure.models.parameter_contract import ParameterContract
from openprocurement.tender.cfaselectionua.procedure.models.unitprices import UnitPrice
from openprocurement.tender.core.models import validate_parameters_uniq
from schematics.types import MD5Type, StringType
from openprocurement.api.models import IsoDateTimeType, ListType, Model, ModelType, Value


class AgreementContract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    parameters = ListType(
        ModelType(ParameterContract, required=True),
        validators=[validate_parameters_uniq]
    )
    status = StringType(choices=["active", "unsuccessful"], default="active")
    suppliers = ListType(ModelType(BusinessOrganization, required=True))
    unitPrices = ListType(ModelType(UnitPrice, required=True))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
    value = ModelType(Value)
