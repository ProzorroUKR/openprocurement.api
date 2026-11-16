from typing import Literal

from pydantic import field_validator

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.procedure.models.base import validate_object_id_uniq, validate_uniq_id
from openprocurement.api.procedure.models.value import Value
from openprocurement.tender.core.procedure.models.criterion import Criterion
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.tender import (
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PostTenderItemsMixin,
    TenderItemsMixin,
    TenderMilestonesMixin,
    validate_negotiation_cause,
    validate_negotiation_quick_cause,
    validate_reporting_cause,
)
from openprocurement.tender.core.procedure.models.tender_base import (
    BaseTender,
    CommonBaseTender,
    PostBaseTender,
    validate_funders_ids,
)
from openprocurement.tender.limited.procedure.models.lot import LimitedLot, LimitedPatchTenderLot, LimitedPostTenderLot
from openprocurement.tender.limited.procedure.models.organization import ReportingFundOrganization
from openprocurement.tender.limited.procedure.models.tender_base import LimitedCauseDetails


class ReportingPostTender(PostTenderItemsMixin, TenderMilestonesMixin, PostBaseTender):
    procurementMethodType: Literal[ProcurementMethodType.REPORTING] = ProcurementMethodType.REPORTING  # type: ignore[valid-type]
    procuringEntity: ProcuringEntity
    value: Value | None = None
    funders: list[ReportingFundOrganization] | None = None
    cause: str | None = None
    causeDescription: str | None = None
    causeDescription_en: str | None = None
    causeDetails: LimitedCauseDetails | None = None

    @field_validator("cause")
    @classmethod
    def validate_cause(cls, value):
        validate_reporting_cause(value)
        return value

    @field_validator("funders")
    @classmethod
    def validate_funders_items(cls, value):
        validate_funders_ids(value)
        return value


class ReportingPatchTender(PatchTenderItemsMixin, PatchTenderMilestonesMixin, CommonBaseTender):
    procurementMethodType: Literal[ProcurementMethodType.REPORTING] | None = None  # type: ignore[valid-type]
    procuringEntity: ProcuringEntity | None = None
    value: Value | None = None
    funders: list[ReportingFundOrganization] | None = None
    cause: str | None = None
    causeDescription: str | None = None
    causeDescription_en: str | None = None
    causeDetails: LimitedCauseDetails | None = None
    criteria: list[Criterion] | None = None

    @field_validator("funders")
    @classmethod
    def validate_funders_items(cls, value):
        validate_funders_ids(value)
        return value

    @field_validator("criteria")
    @classmethod
    def validate_criteria_items(cls, value):
        validate_object_id_uniq(value)
        return value


class ReportingTender(TenderItemsMixin, TenderMilestonesMixin, BaseTender):
    procurementMethodType: Literal[ProcurementMethodType.REPORTING]  # type: ignore[valid-type]
    procuringEntity: ProcuringEntity
    value: Value | None = None
    funders: list[ReportingFundOrganization] | None = None
    cause: str | None = None
    causeDescription: str | None = None
    causeDescription_en: str | None = None
    causeDetails: LimitedCauseDetails | None = None

    @field_validator("cause")
    @classmethod
    def validate_cause(cls, value):
        validate_reporting_cause(value)
        return value

    @field_validator("funders")
    @classmethod
    def validate_funders_items(cls, value):
        validate_funders_ids(value)
        return value


class NegotiationPostTender(PostTenderItemsMixin, TenderMilestonesMixin, PostBaseTender):
    procurementMethodType: Literal[ProcurementMethodType.NEGOTIATION] = ProcurementMethodType.NEGOTIATION  # type: ignore[valid-type]
    procuringEntity: ProcuringEntity
    value: Value
    cause: str | None = None
    causeDescription: str | None = None
    causeDescription_en: str | None = None
    causeDescription_ru: str | None = None
    causeDetails: LimitedCauseDetails | None = None
    lots: list[LimitedPostTenderLot] | None = None

    @field_validator("cause")
    @classmethod
    def validate_cause(cls, value):
        validate_negotiation_cause(value)
        return value

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value


class NegotiationPatchTender(PatchTenderItemsMixin, PatchTenderMilestonesMixin, CommonBaseTender):
    procurementMethodType: Literal[ProcurementMethodType.NEGOTIATION] | None = None  # type: ignore[valid-type]
    procuringEntity: ProcuringEntity | None = None
    value: Value | None = None
    cause: str | None = None
    causeDescription: str | None = None
    causeDescription_en: str | None = None
    causeDescription_ru: str | None = None
    causeDetails: LimitedCauseDetails | None = None
    lots: list[LimitedPatchTenderLot] | None = None
    criteria: list[Criterion] | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("criteria")
    @classmethod
    def validate_criteria_items(cls, value):
        validate_object_id_uniq(value)
        return value


class NegotiationTender(TenderItemsMixin, TenderMilestonesMixin, BaseTender):
    procurementMethodType: Literal[ProcurementMethodType.NEGOTIATION]  # type: ignore[valid-type]
    procuringEntity: ProcuringEntity
    value: Value
    cause: str | None = None
    causeDescription: str | None = None
    causeDescription_en: str | None = None
    causeDescription_ru: str | None = None
    causeDetails: LimitedCauseDetails | None = None
    lots: list[LimitedLot] | None = None

    @field_validator("cause")
    @classmethod
    def validate_cause(cls, value):
        validate_negotiation_cause(value)
        return value

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value


class NegotiationQuickPostTender(NegotiationPostTender):
    procurementMethodType: Literal[ProcurementMethodType.NEGOTIATION_QUICK] = (  # type: ignore[valid-type]
        ProcurementMethodType.NEGOTIATION_QUICK
    )
    cause: str | None = None
    causeDetails: LimitedCauseDetails | None = None

    @field_validator("cause")
    @classmethod
    def validate_cause(cls, value):
        validate_negotiation_quick_cause(value)
        return value


class NegotiationQuickPatchTender(NegotiationPatchTender):
    procurementMethodType: Literal[ProcurementMethodType.NEGOTIATION_QUICK] | None = None  # type: ignore[valid-type]
    causeDetails: LimitedCauseDetails | None = None


class NegotiationQuickTender(NegotiationTender):
    procurementMethodType: Literal[ProcurementMethodType.NEGOTIATION_QUICK]  # type: ignore[valid-type]
    cause: str | None = None
    causeDetails: LimitedCauseDetails | None = None

    @field_validator("cause")
    @classmethod
    def validate_cause(cls, value):
        validate_negotiation_quick_cause(value)
        return value
