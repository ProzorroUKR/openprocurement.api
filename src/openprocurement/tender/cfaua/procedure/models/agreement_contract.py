from schematics.exceptions import ValidationError
from uuid import uuid4
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
)
from openprocurement.tender.core.models import validate_parameters_uniq
from openprocurement.tender.cfaua.procedure.models.unitprice import UnitPrice
from openprocurement.tender.core.procedure.models.parameter import Parameter
from openprocurement.tender.core.procedure.models.organization import BusinessOrganization


class PatchAgreementContract(Model):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    status = StringType(choices=["active", "unsuccessful"])
    unitPrices = ListType(ModelType(UnitPrice, required=True))


class AgreementContract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    status = StringType(choices=["active", "unsuccessful"], default="active")
    suppliers = ListType(ModelType(BusinessOrganization, required=True))
    unitPrices = ListType(ModelType(UnitPrice, required=True))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()

    # TODO: this validation never worked before refactoring ? tests won't work with it
    # def validate_awardID(self, data, value):
    #     agreement = get_request().validated["agreement"]
    #     award_ids = [i["id"] for i in agreement.get("awards", "")]
    #     if value and value not in award_ids:
    #         raise ValidationError("awardID should be one of awards")
