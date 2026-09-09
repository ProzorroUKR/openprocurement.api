from uuid import uuid4

from schematics.types import MD5Type, StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.validation import validate_uniq_code
from openprocurement.tender.cfaua.procedure.models.value import CFAUnitPriceValue
from openprocurement.tender.core.procedure.models.organization import BusinessOrganization
from openprocurement.tender.core.procedure.models.parameter import Parameter


class CFAUnitPrice(Model):
    relatedItem = StringType(required=True)
    value = ModelType(CFAUnitPriceValue)


class CFAPatchAgreementContract(Model):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_uniq_code])
    status = StringType(choices=["active", "unsuccessful"])
    unitPrices = ListType(ModelType(CFAUnitPrice, required=True))


class CFAAgreementContract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_uniq_code])
    status = StringType(choices=["active", "unsuccessful"], default="active")
    suppliers = ListType(ModelType(BusinessOrganization, required=True))
    unitPrices = ListType(ModelType(CFAUnitPrice, required=True))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
