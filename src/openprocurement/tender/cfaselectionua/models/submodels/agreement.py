# -*- coding: utf-8 -*-
from openprocurement.tender.cfaselectionua.models.submodels.feature import Feature
from schematics.types import MD5Type, StringType, IntType
from schematics.types.compound import ModelType, PolyModelType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import IsoDateTimeType, ListType, Model, Period

# TODO: move Document and ProcuringEntity to api plugin
from openprocurement.framework.cfaua.models.agreement import Document
from openprocurement.framework.cfaua.models.agreement import ProcuringEntity
from openprocurement.tender.core.models import validate_features_uniq
from openprocurement.tender.cfaselectionua.models.submodels.agreement_item import AgreementItem as Item
from openprocurement.tender.cfaselectionua.models.submodels.agreement_contract import AgreementContract as Contract
from openprocurement.tender.cfaselectionua.models.submodels.change import (
    ChangeTaxRate,
    ChangeItemPriceVariation,
    ChangePartyWithdrawal,
    ChangeThirdParty,
)
from openprocurement.api.utils import get_change_class


class Agreement(Model):
    class Options:
        roles = RolesFromCsv("Agreement.csv", relative_to=__file__)

    id = MD5Type(required=True)
    agreementID = StringType()
    agreementNumber = StringType()
    contracts = ListType(ModelType(Contract, required=True))
    changes = ListType(
        PolyModelType(
            (ChangeTaxRate, ChangeItemPriceVariation, ChangePartyWithdrawal, ChangeThirdParty),
            claim_function=get_change_class,
        ),
        default=list(),
    )
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    documents = ListType(ModelType(Document, required=True), default=list())
    items = ListType(ModelType(Item, required=True))
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    mode = StringType(choices=["test"])
    owner = StringType()
    period = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity)
    status = StringType(choices=["pending", "active", "cancelled", "terminated"])
    tender_id = MD5Type()
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    terminationDetails = StringType()
    numberOfContracts = IntType()
