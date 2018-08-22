# -*- coding: utf-8 -*-
from uuid import uuid4
from openprocurement.api.roles import RolesFromCsv
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    Organization
)
from openprocurement.tender.core.models import Parameter, validate_parameters_uniq
from openprocurement.tender.cfaselectionua.models.submodels.unitprices import UnitPrice


class AgreementContract(Model):
    class Options:
        roles = RolesFromCsv('AgreementContract.csv', relative_to=__file__)
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    parameters = ListType(ModelType(Parameter), default=list(), validators=[validate_parameters_uniq])
    status = StringType(choices=['active', 'unsuccessful'], default='active')
    suppliers = ListType(ModelType(Organization))
    unitPrices = ListType(ModelType(UnitPrice))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
