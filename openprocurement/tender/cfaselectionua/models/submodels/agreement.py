# -*- coding: utf-8 -*-
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    Period,
)
from openprocurement.tender.core.models import Feature, validate_features_uniq
from openprocurement.tender.cfaselectionua.models.submodels.document import AgreementDocument as Document
from openprocurement.tender.cfaselectionua.models.submodels.item import Item
from openprocurement.tender.cfaselectionua.models.submodels.agreement_contract import AgreementContract as Contract


class Agreement(Model):
    class Options:
        roles = RolesFromCsv('Agreement.csv', relative_to=__file__)
    id = MD5Type(required=True)
    agreementID = StringType()
    agreementNumber = StringType()
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    documents = ListType(ModelType(Document), default=list())
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    items = ListType(ModelType(Item))
    period = ModelType(Period)
    status = StringType(choices=['pending', 'active', 'cancelled'], default='active')
    contracts = ListType(ModelType(Contract))
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
