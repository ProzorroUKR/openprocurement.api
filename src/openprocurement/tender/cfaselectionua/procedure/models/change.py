from schematics.exceptions import ValidationError
from uuid import uuid4
from decimal import Decimal
from schematics.types import StringType, MD5Type
from openprocurement.api.models import IsoDateTimeType, DecimalType, Model, ModelType, ListType
from openprocurement.api.context import get_now


def validate_only_addend_or_only_factor(modifications):
    if modifications:
        changes_with_addend_and_factor = [m for m in modifications if m.addend and m.factor]
        if changes_with_addend_and_factor:
            raise ValidationError("Change with taxRate rationaleType, can have only factor or only addend")


def validate_modifications_items_uniq(items, changes):
    for change in changes or []:
        modifications = change.modifications
        if modifications and change.rationaleType in ("taxRate", "itemPriceVariation", "thirdParty"):
            agreement_items_id = {i.id for i in items or []}
            item_ids = {m.itemId for m in modifications if m.itemId in agreement_items_id}
            if len(item_ids) != len(modifications):
                raise ValidationError("Item id should be uniq for all modifications and one of agreement:items")


class Change(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["pending", "active", "cancelled"], default="pending")
    date = IsoDateTimeType(default=get_now)
    rationale = StringType(required=True, min_length=1)
    rationale_en = StringType()
    rationale_ru = StringType()
    dateSigned = IsoDateTimeType()
    agreementNumber = StringType()

    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError(u"Agreement signature date can't be in the future")


class UnitPriceModification(Model):
    itemId = StringType()
    factor = DecimalType(required=False, precision=-4, min_value=Decimal("0.0"))
    addend = DecimalType(required=False, precision=-2)


class ChangeTaxRate(Change):
    rationaleType = StringType(default="taxRate")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[validate_only_addend_or_only_factor],
    )


def validate_item_price_variation_modifications(modifications):
    for modification in modifications:
        if modification.addend:
            raise ValidationError("Only factor is allowed for itemPriceVariation type of change")
        if not Decimal("0.9") <= modification.factor <= Decimal("1.1"):
            raise ValidationError("Modification factor should be in range 0.9 - 1.1")


class ChangeItemPriceVariation(Change):
    rationaleType = StringType(default="itemPriceVariation")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[validate_item_price_variation_modifications],
    )


def validate_third_party_modifications(modifications):
    for modification in modifications:
        if modification.addend:
            raise ValidationError("Only factor is allowed for thirdParty type of change")


class ChangeThirdParty(Change):
    rationaleType = StringType(default="thirdParty")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[validate_third_party_modifications],
    )


def validate_modifications_contracts_uniq(contracts, changes):
    for change in changes or []:
        modifications = change.modifications
        if modifications and change.rationaleType == "partyWithdrawal":
            agreement_contracts_id = {i.id for i in contracts or []}
            contracts_ids = {c.contractId for c in modifications if c.contractId in agreement_contracts_id}
            if len(contracts_ids) != len(modifications):
                raise ValidationError("Contract id should be uniq for all modifications and one of agreement:contracts")


class ContractModification(Model):
    itemId = StringType()
    contractId = StringType(required=True)


class ChangePartyWithdrawal(Change):
    rationaleType = StringType(default="partyWithdrawal")
    modifications = ListType(
        ModelType(ContractModification, required=True),
    )

