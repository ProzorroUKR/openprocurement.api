"""Agreement changes: shared by closeFrameworkAgreementSelectionUA tenders and cfaua agreements (framework)"""

from decimal import Decimal
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import Field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import MD5, DecimalOf, IsoDateTime


class AgreementChange(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    status: Literal["pending", "active", "cancelled"] = "pending"
    date: IsoDateTime = Field(default_factory=get_request_now)
    rationale: str = Field(min_length=1)
    rationale_en: str | None = None
    rationale_ru: str | None = None
    dateSigned: IsoDateTime | None = None
    agreementNumber: str | None = None


class UnitPriceModification(Model):
    itemId: str | None = None
    factor: Annotated[Decimal, DecimalOf(-4)] | None = Field(None, ge=Decimal("0.0"))
    addend: Annotated[Decimal, DecimalOf(-2)] | None = None


class ContractModification(Model):
    itemId: str | None = None
    contractId: str


def validate_only_addend_or_only_factor(modifications: list[UnitPriceModification] | None) -> None:
    if modifications:
        changes_with_addend_and_factor = [m for m in modifications if m.addend and m.factor]
        if changes_with_addend_and_factor:
            raise ValueError("Change with taxRate rationaleType, can have only factor or only addend")


def validate_item_price_variation_modifications(modifications: list[UnitPriceModification]) -> None:
    for modification in modifications:
        if modification.addend:
            raise ValueError("Only factor is allowed for itemPriceVariation type of change")
        if modification.factor is None or not Decimal("0.9") <= modification.factor <= Decimal("1.1"):
            raise ValueError("Modification factor should be in range 0.9 - 1.1")


def validate_third_party_modifications(modifications: list[UnitPriceModification]) -> None:
    for modification in modifications:
        if modification.addend:
            raise ValueError("Only factor is allowed for thirdParty type of change")
