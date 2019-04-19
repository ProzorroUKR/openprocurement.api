# -*- coding: utf-8 -*-
from uuid import uuid4
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaselectionua.models.submodels.parameter_contract import ParameterContract
from openprocurement.tender.cfaselectionua.models.submodels.unitprices import UnitPrice
from openprocurement.tender.core.models import validate_parameters_uniq
from schematics.types import MD5Type, StringType
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    ModelType,
    BusinessOrganization,
    Value
)


class AgreementContract(Model):
    class Options:
        roles = RolesFromCsv('AgreementContract.csv', relative_to=__file__)
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    parameters = ListType(ModelType(ParameterContract), default=list(), validators=[validate_parameters_uniq])
    status = StringType(choices=['active', 'unsuccessful'], default='active')
    suppliers = ListType(ModelType(BusinessOrganization))
    unitPrices = ListType(ModelType(UnitPrice))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
    value = ModelType(Value)
