from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, field_validator

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.procedure.models.base import model_field_validator, validate_uniq_id
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.types import (
    DecimalOf,
)
from openprocurement.tender.core.constants import AwardCriteria
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.period import EnquiryPeriod
from openprocurement.tender.core.procedure.models.tender import (
    PatchTenderFeaturesMixin,
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PostTenderItemsMixin,
    PostTenderPeriodsMixin,
    TenderFeaturesMixin,
    TenderGuaranteeMixin,
    TenderItemsMixin,
    TenderMilestonesMixin,
    TenderPeriodsMixin,
    TenderSubmissionMixin,
    validate_esco_lots_yearly_payments_percentage_range,
    validate_esco_yearly_payments_percentage_range,
)
from openprocurement.tender.core.procedure.models.tender_base import BaseTender, PatchBaseTender, PostBaseTender
from openprocurement.tender.core.procedure.models.value import PostEstimatedValue
from openprocurement.tender.esco.constants import ESCOProcurementMethodType
from openprocurement.tender.esco.procedure.models.lot import ESCOLot, ESCOPatchTenderLot, ESCOPostTenderLot


class ESCOPostTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PostTenderPeriodsMixin,
    PostTenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    PostBaseTender,
):
    awardCriteria: AwardCriteria | None = None
    procurementMethodType: ESCOProcurementMethodType = ProcurementMethodType.ESCO
    minValue: PostEstimatedValue = Field({"currency": "UAH", "valueAddedTaxIncluded": False}, validate_default=True)
    minimalStepPercentage: Annotated[Decimal, DecimalOf(-5)] | None = Field(
        None, ge=Decimal("0.005"), le=Decimal("0.03")
    )
    yearlyPaymentsPercentageRange: Annotated[Decimal, DecimalOf(-5)] | None = Field(
        None, ge=Decimal("0"), le=Decimal("1")
    )
    NBUdiscountRate: Annotated[Decimal, DecimalOf(-5)] = Field(ge=Decimal("0"), le=Decimal("0.99"))
    fundingKind: Literal["budget", "other"] = "other"
    procuringEntity: ProcuringEntity
    lots: list[ESCOPostTenderLot] | None = None

    @model_field_validator("yearlyPaymentsPercentageRange")
    def validate_yearly_payments_percentage_range(self, value):
        validate_esco_yearly_payments_percentage_range(self, value)

    @model_field_validator("lots")
    def validate_lots(self, lots):
        validate_esco_lots_yearly_payments_percentage_range(self, lots)

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value


class ESCOPatchTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PatchTenderItemsMixin,
    PatchTenderFeaturesMixin,
    PatchTenderMilestonesMixin,
    PatchBaseTender,
):
    enquiryPeriod: EnquiryPeriod | None = None
    tenderPeriod: PeriodEndRequired | None = None
    awardCriteria: AwardCriteria | None = None
    procurementMethodType: ESCOProcurementMethodType | None = None
    minimalStepPercentage: Annotated[Decimal, DecimalOf(-5)] | None = Field(
        None, ge=Decimal("0.005"), le=Decimal("0.03")
    )
    yearlyPaymentsPercentageRange: Annotated[Decimal, DecimalOf(-5)] | None = Field(
        None, ge=Decimal("0"), le=Decimal("1")
    )
    NBUdiscountRate: Annotated[Decimal, DecimalOf(-5)] | None = Field(None, ge=Decimal("0"), le=Decimal("0.99"))
    fundingKind: Literal["budget", "other"] | None = None
    procuringEntity: ProcuringEntity | None = None
    lots: list[ESCOPatchTenderLot] | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value


class ESCOTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    TenderPeriodsMixin,
    TenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    BaseTender,
):
    awardCriteria: AwardCriteria
    procurementMethodType: ESCOProcurementMethodType
    minimalStepPercentage: Annotated[Decimal, DecimalOf(-5)] | None = Field(
        None, ge=Decimal("0.005"), le=Decimal("0.03")
    )
    minValue: PostEstimatedValue | None = None
    yearlyPaymentsPercentageRange: Annotated[Decimal, DecimalOf(-5)] | None = Field(
        None, ge=Decimal("0"), le=Decimal("1")
    )
    NBUdiscountRate: Annotated[Decimal, DecimalOf(-5)] = Field(ge=Decimal("0"), le=Decimal("0.99"))
    fundingKind: Literal["budget", "other"]
    procuringEntity: ProcuringEntity
    lots: list[ESCOLot] | None = None

    @model_field_validator("yearlyPaymentsPercentageRange")
    def validate_yearly_payments_percentage_range(self, value):
        validate_esco_yearly_payments_percentage_range(self, value)

    @model_field_validator("lots")
    def validate_lots(self, lots):
        validate_esco_lots_yearly_payments_percentage_range(self, lots)

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value
