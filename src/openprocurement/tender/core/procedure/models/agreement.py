from openprocurement.api.models import IsoDateTimeType, ValidationError, Value, Period, ListType, Model
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.models.base import BaseAward
from openprocurement.tender.core.procedure.models.organization import PostBusinessOrganization
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.agreement_contract import Contract
from openprocurement.tender.core.procedure.models.req_response import (
    RequirementResponse,
    validate_response_requirement_uniq,
)
from openprocurement.tender.core.procedure.context import get_tender, get_now
from schematics.types import StringType, MD5Type, BooleanType, BaseType
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

