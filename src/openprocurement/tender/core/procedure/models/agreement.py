from openprocurement.api.models import ListType, Model
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.models.agreement_contract import Contract
from schematics.types import StringType, MD5Type
from schematics.types.compound import PolyModelType
from schematics.types.serializable import serializable
from uuid import uuid4


class PostAgreement(Model):
    @serializable
    def id(self):
        return uuid4().hex


class PatchAgreement(Model):
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


class Agreement(Model):
    id = MD5Type(required=True)
    agreementID = StringType()
    agreementNumber = StringType()

