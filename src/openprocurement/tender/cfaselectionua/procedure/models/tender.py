from typing import Any

from pydantic import Field, field_serializer, field_validator

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.procedure.models.base import validate_uniq_code, validate_uniq_id
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.models.value import BasicValue, Value
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.tender.cfaselectionua.constants import CFASelectionUAProcurementMethodType
from openprocurement.tender.cfaselectionua.procedure.models.agreement import CFASelectionAgreement
from openprocurement.tender.cfaselectionua.procedure.models.feature import CFASelectionFeature
from openprocurement.tender.cfaselectionua.procedure.models.lot import (
    CFASelectionLot,
    CFASelectionPatchTenderLot,
    CFASelectionPostTenderLot,
)
from openprocurement.tender.core.constants import AwardCriteria
from openprocurement.tender.core.procedure.models.agreement import AgreementUUID
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.tender import (
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PostTenderItemsMixin,
    TenderFeaturesMixin,
    TenderGuaranteeMixin,
    TenderItemsMixin,
    TenderMilestonesMixin,
    TenderSubmissionMixin,
)
from openprocurement.tender.core.procedure.models.tender_base import BaseTender, PatchBaseTender, PostBaseTender


class CFASelectionPostTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PostTenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    PostBaseTender,
):
    procurementMethodType: CFASelectionUAProcurementMethodType = (
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA
    )
    awardCriteria: AwardCriteria | None = None
    procuringEntity: ProcuringEntity
    agreements: list[AgreementUUID] = Field(min_length=1, max_length=1)
    lots: list[CFASelectionPostTenderLot] = Field(min_length=1, max_length=1)
    features: list[CFASelectionFeature] | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("features")
    @classmethod
    def validate_features_items(cls, value):
        validate_uniq_code(value)
        return value


class CFASelectionPatchTender(
    TenderSubmissionMixin, TenderGuaranteeMixin, PatchTenderItemsMixin, PatchTenderMilestonesMixin, PatchBaseTender
):
    procurementMethodType: CFASelectionUAProcurementMethodType | None = None
    awardCriteria: AwardCriteria | None = None
    procuringEntity: ProcuringEntity | None = None
    lots: list[CFASelectionPatchTenderLot] | None = Field(None, min_length=1, max_length=1)
    features: list[CFASelectionFeature] | None = None
    unsuccessfulReason: list[str] | None = None
    tenderPeriod: PeriodEndRequired | None = None
    minimalStep: Value | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("features")
    @classmethod
    def validate_features_items(cls, value):
        validate_uniq_code(value)
        return value


class CFASelectionTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    TenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    BaseTender,
):
    procurementMethodType: CFASelectionUAProcurementMethodType
    awardCriteria: AwardCriteria
    procuringEntity: ProcuringEntity
    agreements: list[CFASelectionAgreement] = Field(min_length=1, max_length=1)
    lots: list[CFASelectionLot] = Field(min_length=1, max_length=1)
    features: list[CFASelectionFeature] | None = None
    unsuccessfulReason: list[str] | None = None
    tenderPeriod: PeriodEndRequired | None = None
    enquiryPeriod: PeriodEndRequired | None = None
    minimalStep: Value | None = None
    value: Value | None = None

    @field_serializer("guarantee")
    def serialize_guarantee(self, value: Any) -> Any:
        if self.lots:
            lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
            if not lots_amount:
                return value
            guarantee = {"amount": float(sum((to_decimal(i) for i in lots_amount)))}
            lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
            guarantee["currency"] = lots_currency[0] if lots_currency else None
            if value:
                guarantee["currency"] = value.currency
            return BasicValue.model_validate(guarantee)
        else:
            return value

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("features")
    @classmethod
    def validate_features_items(cls, value):
        validate_uniq_code(value)
        return value
