from typing import Annotated, Any, Literal

from pydantic import Field, field_validator

from openprocurement.api.procedure.models.agreement import (
    AgreementChange,
    ContractModification,
    UnitPriceModification,
    validate_item_price_variation_modifications,
    validate_only_addend_or_only_factor,
    validate_third_party_modifications,
)
from openprocurement.api.procedure.models.base import Model, model_field_validator, validate_uniq_code, validate_uniq_id
from openprocurement.api.procedure.models.milestone import Milestone
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.cfaselectionua.procedure.models.agreement_contract import CFASelectionAgreementContract
from openprocurement.tender.cfaselectionua.procedure.models.feature import CFASelectionFeature
from openprocurement.tender.core.procedure.models.agreement import (
    validate_cfa_selection_modifications_contracts_uniq,
    validate_cfa_selection_modifications_items_uniq,
)
from openprocurement.tender.core.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.parameter import validate_cfa_selection_parameter_contracts


class CFASelectionChangeTaxRate(AgreementChange):
    rationaleType: Literal["taxRate"] = "taxRate"
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_only_addend_or_only_factor(value)
        return value


class CFASelectionChangeItemPriceVariation(AgreementChange):
    rationaleType: Literal["itemPriceVariation"] = "itemPriceVariation"
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_item_price_variation_modifications(value)
        return value


class CFASelectionChangeThirdParty(AgreementChange):
    rationaleType: Literal["thirdParty"] = "thirdParty"
    modifications: list[UnitPriceModification] | None = None

    @field_validator("modifications")
    @classmethod
    def validate_modifications_items(cls, value):
        validate_third_party_modifications(value)
        return value


class CFASelectionChangePartyWithdrawal(AgreementChange):
    rationaleType: Literal["partyWithdrawal"] = "partyWithdrawal"
    modifications: list[ContractModification] | None = None


class CFASelectionPatchAgreement(Model):
    id: MD5 | None = None
    agreementID: str | None = None
    agreementNumber: str | None = None
    date: IsoDateTime | None = None
    dateSigned: IsoDateTime | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    features: list[CFASelectionFeature] | None = None
    items: list[Item] | None = None
    period: Period | None = None
    status: Literal["pending", "active", "cancelled", "terminated"] | None = None
    contracts: list[CFASelectionAgreementContract] | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    milestones: list[Milestone] | None = None
    terminationDetails: str | None = None
    tender_id: MD5 | None = None
    dateModified: IsoDateTime | None = None
    mode: Literal["test"] | None = None
    numberOfContracts: int | None = None
    owner: str | None = None
    procuringEntity: ProcuringEntity | None = None
    changes: (
        list[
            Annotated[
                CFASelectionChangeTaxRate
                | CFASelectionChangeItemPriceVariation
                | CFASelectionChangePartyWithdrawal
                | CFASelectionChangeThirdParty,
                Field(discriminator="rationaleType"),
            ]
        ]
        | None
    ) = None

    @model_field_validator("changes")
    def validate_changes(self, changes):
        validate_cfa_selection_modifications_items_uniq(self.items, changes)
        validate_cfa_selection_modifications_contracts_uniq(self.contracts, changes)

    @model_field_validator("contracts")
    def validate_contracts(self, contracts):
        validate_cfa_selection_parameter_contracts(self.features, contracts)

    @field_validator("features")
    @classmethod
    def validate_features_items(cls, value):
        validate_uniq_code(value)
        return value

    @field_validator("milestones")
    @classmethod
    def validate_milestones_items(cls, value):
        validate_uniq_id(value)
        return value


class CFASelectionAgreement(CFASelectionPatchAgreement):
    id: MD5
    documents: Any = None
