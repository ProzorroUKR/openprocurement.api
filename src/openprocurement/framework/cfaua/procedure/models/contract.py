from decimal import Decimal
from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from openprocurement.api.models import (
    BaseAddress,
    BusinessOrganization as BaseBusinessOrganization,
    DecimalType,
    Model,
    ModelType,
    IsoDateTimeType,
    ListType,
    Value as BaseValue,
)
from openprocurement.api.procedure.validation import validate_parameters_uniq


class BusinessOrganization(BaseBusinessOrganization):
    address = ModelType(BaseAddress, required=True)

    def validate_scale(self, data, value):
        pass


class Value(BaseValue):
    amount = DecimalType(required=True, precision=-2, min_value=Decimal("0.0"))


class UnitPrice(Model):
    class Options:
        roles = Model.Options.roles

    # TODO: validate relatedItem? (quintagroup)
    relatedItem = StringType()
    value = ModelType(Value)


class Parameter(Model):
    class Options:
        serialize_when_none = False
        roles = Model.Options.roles

    code = StringType(required=True)
    value = DecimalType(required=True)

    def validate_code(self, data, code):
        contract = data["__parent__"]
        if isinstance(contract, Model) and code not in [
            i.code for i in (contract["__parent__"].features or [])
        ]:
            raise ValidationError(u"code should be one of feature code.")

    def validate_value(self, data, value):
        if isinstance(data["__parent__"], Model):
            agreement = data["__parent__"]["__parent__"]
            codes = dict([(i.code, [x.value for x in i.enum]) for i in (agreement.features or [])])
            if data["code"] in codes and value not in codes[data["code"]]:
                raise ValidationError(u"value should be one of feature value.")


class Contract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)

    # TODO: validate me (quintagroup)
    status = StringType(choices=["active", "unsuccessful"])
    suppliers = ListType(ModelType(BusinessOrganization, required=True))
    unitPrices = ListType(ModelType(UnitPrice, required=True))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
    parameters = ListType(
        ModelType(Parameter, required=True), default=list(), validators=[validate_parameters_uniq]
    )
