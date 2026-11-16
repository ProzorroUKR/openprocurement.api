from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field, field_validator

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.agreement import AgreementChange as Change
from openprocurement.api.procedure.models.agreement import (
    ContractModification,
    UnitPriceModification,
    validate_item_price_variation_modifications,
    validate_only_addend_or_only_factor,
    validate_third_party_modifications,
)
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    IsoDateTime,
)


class PatchChange(Model):
    status: Literal["pending", "active", "cancelled"] | None = None
    rationale: str | None = Field(None, min_length=1)
    rationale_en: str | None = None
    rationale_ru: str | None = None
    dateSigned: IsoDateTime | None = None
    agreementNumber: str | None = None


class PostChange(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    status: Literal["pending"] = "pending"
    rationale: str = Field(min_length=1)
    rationale_en: str | None = None
    rationale_ru: str | None = None
    dateSigned: IsoDateTime | None = None
    agreementNumber: str | None = None
    date: IsoDateTime = Field(default_factory=get_request_now)


class ChangeTaxRate(Change):
    rationaleType: Literal["taxRate"] = "taxRate"
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_modifications_items_uniq(value)
        validate_only_addend_or_only_factor(value)
        return value


class PostChangeTaxRate(PostChange):
    rationaleType: Literal["taxRate"] = "taxRate"
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_modifications_items_uniq(value)
        validate_only_addend_or_only_factor(value)
        return value


class PatchChangeTaxRate(PatchChange):
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_modifications_items_uniq(value)
        validate_only_addend_or_only_factor(value)
        return value


class ChangeItemPriceVariation(Change):
    rationaleType: Literal["itemPriceVariation"] = "itemPriceVariation"
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_item_price_variation_modifications(value)
        validate_modifications_items_uniq(value)
        return value


class PostChangeItemPriceVariation(PostChange):
    rationaleType: Literal["itemPriceVariation"] = "itemPriceVariation"
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_item_price_variation_modifications(value)
        validate_modifications_items_uniq(value)
        return value


class PatchChangeItemPriceVariation(PatchChange):
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_item_price_variation_modifications(value)
        validate_modifications_items_uniq(value)
        return value


class ChangeThirdParty(Change):
    rationaleType: Literal["thirdParty"] = "thirdParty"
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_third_party_modifications(value)
        validate_modifications_items_uniq(value)
        return value


class PostChangeThirdParty(PostChange):
    rationaleType: Literal["thirdParty"] = "thirdParty"
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_third_party_modifications(value)
        validate_modifications_items_uniq(value)
        return value


class PatchChangeThirdParty(PatchChange):
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_third_party_modifications(value)
        validate_modifications_items_uniq(value)
        return value


class ChangePartyWithdrawal(Change):
    rationaleType: Literal["partyWithdrawal"] = "partyWithdrawal"
    modifications: list[ContractModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_modifications_contracts_uniq(value)
        return value


class PostChangePartyWithdrawal(PostChange):
    rationaleType: Literal["partyWithdrawal"] = "partyWithdrawal"
    modifications: list[ContractModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_modifications_contracts_uniq(value)
        return value


class PatchChangePartyWithdrawal(PatchChange):
    modifications: list[ContractModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_modifications_contracts_uniq(value)
        return value


def validate_modifications_items_uniq(modifications):
    agreement = get_request().validated["agreement"]
    if modifications:
        agreement_items_id = {item["id"] for item in agreement.get("items", [])}
        item_ids = {m.itemId for m in modifications if m.itemId in agreement_items_id}
        if len(item_ids) != len(modifications):
            raise ValidationError("Item id should be uniq for all modifications and one of agreement:items")


def validate_modifications_contracts_uniq(modifications):
    agreement = get_request().validated["agreement"]
    if modifications:
        agreement_contracts_id = {contract["id"] for contract in agreement.get("contracts")}
        contracts_ids = {mod.contractId for mod in modifications if mod.contractId in agreement_contracts_id}
        if len(contracts_ids) != len(modifications):
            raise ValidationError("Contract id should be uniq for all modifications and one of agreement:contracts")
