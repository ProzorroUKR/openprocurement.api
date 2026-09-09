from uuid import uuid4

from schematics.types import MD5Type, StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.validation import validate_uniq_code
from openprocurement.tender.cfaselectionua.procedure.models.organization import CFASelectionBusinessOrganization
from openprocurement.tender.cfaselectionua.procedure.models.value import CFASelectionUnitPriceValue
from openprocurement.tender.core.procedure.models.parameter import AgreementContractParameter


class CFASelectionUnitPrice(Model):
    relatedItem = StringType()
    value = ModelType(CFASelectionUnitPriceValue)


class CFASelectionAgreementContract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    parameters = ListType(
        ModelType(AgreementContractParameter, required=True),
        validators=[validate_uniq_code],
    )
    status = StringType(choices=["active", "unsuccessful"], default="active")
    suppliers = ListType(ModelType(CFASelectionBusinessOrganization, required=True))
    unitPrices = ListType(ModelType(CFASelectionUnitPrice, required=True))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
    value = ModelType(Value)
