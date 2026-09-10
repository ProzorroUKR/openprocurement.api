from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    IsoDateTimeType,
    ListType,
    ModelType,
)
from openprocurement.framework.cfaua.procedure.validation import (
    validate_modifications_contracts_uniq,
    validate_modifications_items_uniq,
)
from openprocurement.tender.core.procedure.models.agreement import AgreementChange as Change
from openprocurement.tender.core.procedure.models.agreement import (
    ContractModification,
    UnitPriceModification,
    validate_item_price_variation_modifications,
    validate_only_addend_or_only_factor,
    validate_third_party_modifications,
)


class PatchChange(Model):
    status = StringType(choices=["pending", "active", "cancelled"])
    rationale = StringType(min_length=1)
    rationale_en = StringType()
    rationale_ru = StringType()
    dateSigned = IsoDateTimeType()
    agreementNumber = StringType()

    def validate_dateSigned(self, data, value):
        if value and value > get_request_now():
            raise ValidationError("Agreement signature date can't be in the future")


class PostChange(Model):
    @serializable
    def id(self):
        return uuid4().hex

    status = StringType(choices=["pending"], default="pending")
    rationale = StringType(required=True, min_length=1)
    rationale_en = StringType()
    rationale_ru = StringType()
    dateSigned = IsoDateTimeType()
    agreementNumber = StringType()
    date = IsoDateTimeType(default=get_request_now)

    def validate_dateSigned(self, data, value):
        if value and value > get_request_now():
            raise ValidationError("Agreement signature date can't be in the future")


class ChangeTaxRate(Change):
    rationaleType = StringType(default="taxRate")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[
            validate_modifications_items_uniq,
            validate_only_addend_or_only_factor,
        ],
    )


class PostChangeTaxRate(PostChange):
    rationaleType = StringType(default="taxRate")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[
            validate_modifications_items_uniq,
            validate_only_addend_or_only_factor,
        ],
    )


class PatchChangeTaxRate(PatchChange):
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[
            validate_modifications_items_uniq,
            validate_only_addend_or_only_factor,
        ],
    )


class ChangeItemPriceVariation(Change):
    rationaleType = StringType(default="itemPriceVariation")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[
            validate_item_price_variation_modifications,
            validate_modifications_items_uniq,
        ],
    )


class PostChangeItemPriceVariation(PostChange):
    rationaleType = StringType(default="itemPriceVariation")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[
            validate_item_price_variation_modifications,
            validate_modifications_items_uniq,
        ],
    )


class PatchChangeItemPriceVariation(PatchChange):
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[
            validate_item_price_variation_modifications,
            validate_modifications_items_uniq,
        ],
    )


class ChangeThirdParty(Change):
    rationaleType = StringType(default="thirdParty")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[
            validate_third_party_modifications,
            validate_modifications_items_uniq,
        ],
    )


class PostChangeThirdParty(PostChange):
    rationaleType = StringType(default="thirdParty")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[
            validate_third_party_modifications,
            validate_modifications_items_uniq,
        ],
    )


class PatchChangeThirdParty(PatchChange):
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[
            validate_third_party_modifications,
            validate_modifications_items_uniq,
        ],
    )


class ChangePartyWithdrawal(Change):
    rationaleType = StringType(default="partyWithdrawal")
    modifications = ListType(
        ModelType(ContractModification, required=True),
        validators=[validate_modifications_contracts_uniq],
    )


class PostChangePartyWithdrawal(PostChange):
    rationaleType = StringType(default="partyWithdrawal")
    modifications = ListType(
        ModelType(ContractModification, required=True),
        validators=[validate_modifications_contracts_uniq],
    )


class PatchChangePartyWithdrawal(PatchChange):
    modifications = ListType(
        ModelType(ContractModification, required=True),
        validators=[validate_modifications_contracts_uniq],
    )
