from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import Discriminator, Field, Tag, computed_field, field_validator, model_validator

from openprocurement.api.procedure.models.base import Model, RootModel, validate_uniq_id
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import (
    AmountPercentageValue,
    ContractValue,
)
from openprocurement.api.procedure.types import IsoDateTime
from openprocurement.contracting.core.procedure.models.access import AccessDetails
from openprocurement.contracting.core.procedure.models.change import Change
from openprocurement.contracting.core.procedure.models.document import Document
from openprocurement.contracting.core.procedure.models.implementation import (
    Implementation,
)
from openprocurement.contracting.core.procedure.models.item import Item
from openprocurement.contracting.core.procedure.models.milestone import (
    ContractMilestone,
)
from openprocurement.contracting.core.procedure.models.organization import (
    Buyer,
    Supplier,
)
from openprocurement.contracting.core.procedure.models.value import AmountPaid


def contract_value_kind(value: Any) -> str | None:
    """the value of a contract is either a percentage of the amount or a regular one"""
    if isinstance(value, Model):
        return type(value).__name__
    if isinstance(value, dict):
        return "AmountPercentageValue" if "amountPercentage" in value else "ContractValue"
    return None


ContractValueField = Annotated[
    Annotated[AmountPercentageValue, Tag("AmountPercentageValue")] | Annotated[ContractValue, Tag("ContractValue")],
    Discriminator(contract_value_kind),
]


class PostContract(Model):
    """
    Model only for auto-creating contract
    """

    @computed_field
    def transfer_token(self) -> Any:
        return uuid4().hex

    @computed_field
    def status(self) -> Any:
        return "pending"

    @computed_field(alias="_id")
    def doc_id(self) -> str | None:
        """the database document of the contract has the id of the contract"""
        return self.id

    id: str | None = None
    awardID: str | None = None
    contractID: str | None = None
    buyerID: str | None = None
    contractNumber: str | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    period: Period | None = None
    value: ContractValueField | None = None
    items: list[Item] | None = None
    buyer: Buyer
    suppliers: list[Supplier] | None = Field(None, min_length=1, max_length=1)
    owner: str | None = None
    access: list[AccessDetails] | None = None
    tender_id: str
    tenderID: str | None = None
    mainProcurementCategory: str | None = None
    mode: Literal["test"] | None = None
    amountPaid: AmountPaid | None = None
    contractTemplateName: str | None = None
    milestones: list[ContractMilestone] | None = None
    contractChangeRationaleTypes: Any = None

    @field_validator("milestones")
    @classmethod
    def validate_milestones_items(cls, value):
        validate_uniq_id(value)
        return value


class BasePatchContract(Model):
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    implementation: Implementation | None = None
    status: Literal["active", "terminated"] | None = None
    period: Period | None = None
    value: ContractValueField | None = None
    items: list[Item] | None = Field(None, min_length=1)
    milestones: list[ContractMilestone] | None = None

    @field_validator("milestones")
    @classmethod
    def validate_milestones_items(cls, value):
        validate_uniq_id(value)
        return value


class Contract(RootModel):
    """Contract"""

    buyerID: str | None = None
    awardID: str | None = None
    contractID: str | None = None
    contractNumber: str | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    dateSigned: IsoDateTime | None = None
    date: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None
    dateCreated: IsoDateTime | None = None
    items: list[Item] | None = Field(None, min_length=1)
    tender_token: str | None = None
    tender_id: str
    tenderID: str | None = None
    mainProcurementCategory: str | None = None
    owner_token: str | None = None
    transfer_token: str = Field(default_factory=lambda: uuid4().hex)
    owner: str | None = None
    mode: Literal["test"] | None = None
    status: Literal["pending", "pending.winner-signing", "terminated", "active", "cancelled"] | None = None
    period: Period | None = None
    buyer: Buyer
    suppliers: list[Supplier] | None = Field(None, min_length=1, max_length=1)
    contractTemplateName: str | None = None
    changes: list[Change] | None = None
    terminationDetails: str | None = None
    implementation: Implementation | None = None
    is_masked: bool | None = None
    documents: list[Document] | None = None
    amountPaid: AmountPaid | None = None
    value: ContractValueField | None = None
    contractChangeRationaleTypes: Any = None
    bid_owner: str | None = None
    bid_token: str | None = None
    access: list[AccessDetails] | None = None
    config: Any = None
    attachments_: Any = Field(None, alias="_attachments")
    milestones: list[ContractMilestone] | None = None

    @model_validator(mode="after")
    def set_amount_paid_defaults(self):
        # amountPaid takes currency and valueAddedTaxIncluded of the value
        if self.amountPaid and isinstance(self.value, ContractValue):
            self.amountPaid.currency = self.value.currency
            if self.amountPaid.valueAddedTaxIncluded is None:
                self.amountPaid.valueAddedTaxIncluded = self.value.valueAddedTaxIncluded
        return self

    @field_validator("items")
    @classmethod
    def validate_items_items(cls, value):
        validate_uniq_id(value)
        return value


class PatchContract(BasePatchContract):
    status: Literal["pending", "active", "cancelled", "terminated"] | None = None
    items: list[Item] | None = Field(None, min_length=1)
    terminationDetails: str | None = None
    amountPaid: AmountPaid | None = None
    value: ContractValueField | None = None


class PatchContractPending(BasePatchContract):
    status: Literal["pending", "active", "cancelled", "terminated"] | None = None
    items: list[Item] | None = Field(None, min_length=1)
    dateSigned: IsoDateTime | None = None
    contractNumber: str | None = None
    value: ContractValueField | None = None


class AdministratorPatchContract(Model):
    contractNumber: str | None = None
    status: Literal["pending", "pending.winner-signing", "terminated", "active", "cancelled"] | None = None
    suppliers: list[Supplier] | None = Field(None, min_length=1, max_length=1)
    buyer: Buyer | None = None
    mode: Literal["test"] | None = None
