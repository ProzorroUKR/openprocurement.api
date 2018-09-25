# -*- coding: utf-8 -*-
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType, PolyModelType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    Period,
)
from openprocurement.agreement.cfaua.models.change import (
    ChangeTaxRate, ChangeItemPriceVariation, ChangeThirdParty, ChangePartyWithdrawal
)
from openprocurement.agreement.cfaua.models.document import Document
from openprocurement.agreement.cfaua.models.procuringentity import ProcuringEntity
from openprocurement.agreement.cfaua.utils import get_change_class
from openprocurement.tender.core.models import Feature, validate_features_uniq
from openprocurement.tender.cfaselectionua.models.submodels.agreement_item import AgreementItem as Item
from openprocurement.tender.cfaselectionua.models.submodels.agreement_contract import AgreementContract as Contract


class Agreement(Model):
    class Options:
        roles = RolesFromCsv('Agreement.csv', relative_to=__file__)
    id = MD5Type(required=True)
    agreementID = StringType()
    agreementNumber = StringType()
    contracts = ListType(ModelType(Contract))
    changes = ListType(PolyModelType((ChangeTaxRate, ChangeItemPriceVariation, ChangePartyWithdrawal, ChangeThirdParty),
                       claim_function=get_change_class), default=list())
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    mode = StringType(choices=['test'])
    owner = StringType()
    period = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity)
    status = StringType(choices=['pending', 'active', 'cancelled'])
    tender_id = MD5Type()
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
