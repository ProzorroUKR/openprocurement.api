from typing import Literal

from pydantic import field_validator

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import validate_uniq_id
from openprocurement.tender.arma.procedure.models.lot import ARMALot, ARMAPatchTenderLot, ARMAPostTenderLot
from openprocurement.tender.core.constants import AwardCriteria
from openprocurement.tender.core.procedure.models.agreement import AgreementUUID
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.tender import (
    PatchTenderFeaturesMixin,
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PatchTenderPeriodsMixin,
    PostTenderItemsMixin,
    PostTenderPeriodsMixin,
    TenderFeaturesMixin,
    TenderGuaranteeMixin,
    TenderItemsMixin,
    TenderMilestonesMixin,
    TenderPeriodsMixin,
    TenderSubmissionMixin,
)
from openprocurement.tender.core.procedure.models.tender_base import BaseTender, PatchBaseTender, PostBaseTender


class ARMAPostTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PostTenderPeriodsMixin,
    PostTenderItemsMixin,
    TenderMilestonesMixin,
    PostBaseTender,
):
    awardCriteria: AwardCriteria | None = None
    procuringEntity: ProcuringEntity
    lots: list[ARMAPostTenderLot] | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots(cls, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")
        return value

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value


class ComplexAssetPostTender(ARMAPostTender):
    procurementMethodType: Literal[ProcurementMethodType.COMPLEX_ASSET_ARMA] = (  # type: ignore[valid-type]
        ProcurementMethodType.COMPLEX_ASSET_ARMA
    )


class SimpleAssetPostTender(TenderFeaturesMixin, ARMAPostTender):
    procurementMethodType: Literal[ProcurementMethodType.SIMPLE_ASSET_ARMA] = (  # type: ignore[valid-type]
        ProcurementMethodType.SIMPLE_ASSET_ARMA
    )
    agreement: AgreementUUID


class ARMAPatchTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PatchTenderPeriodsMixin,
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PatchBaseTender,
):
    awardCriteria: AwardCriteria | None = None
    procuringEntity: ProcuringEntity | None = None
    lots: list[ARMAPatchTenderLot] | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots(cls, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")
        return value

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value


class SimpleAssetPatchTender(PatchTenderFeaturesMixin, ARMAPatchTender):
    agreement: AgreementUUID | None = None


class ARMATender(
    TenderSubmissionMixin, TenderGuaranteeMixin, TenderPeriodsMixin, TenderItemsMixin, TenderMilestonesMixin, BaseTender
):
    awardCriteria: AwardCriteria | None = None
    procuringEntity: ProcuringEntity
    lots: list[ARMALot] | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value


class ComplexAssetTender(ARMATender):
    procurementMethodType: Literal[ProcurementMethodType.COMPLEX_ASSET_ARMA]  # type: ignore[valid-type]


class SimpleAssetTender(TenderFeaturesMixin, ARMATender):
    procurementMethodType: Literal[ProcurementMethodType.SIMPLE_ASSET_ARMA]  # type: ignore[valid-type]
    agreement: AgreementUUID
