from pydantic import Field, field_validator

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.procedure.models.base import model_field_validator, validate_uniq_code, validate_uniq_id
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import (
    IsoDuration,
)
from openprocurement.tender.cfaua.constants import CFA_UA_LOTS_MAX_SIZE as CFA_LOTS_MAX_SIZE
from openprocurement.tender.cfaua.constants import CFA_UA_LOTS_MIN_SIZE as CFA_LOTS_MIN_SIZE
from openprocurement.tender.cfaua.constants import CFAUAProcurementMethodType
from openprocurement.tender.cfaua.procedure.models.feature import CFAFeature
from openprocurement.tender.core.procedure.models.lot import Lot, PatchTenderLot, PostTenderLot
from openprocurement.tender.core.procedure.models.tender import (
    PatchTender,
    PostTender,
    Tender,
    validate_cfa_features,
    validate_cfa_max_agreement_duration_period,
    validate_cfa_max_awards_number,
)


class CFAPostTender(PostTender):
    procurementMethodType: CFAUAProcurementMethodType = ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA
    agreementDuration: IsoDuration
    maxAwardsCount: int
    lots: list[PostTenderLot] = Field(min_length=CFA_LOTS_MIN_SIZE, max_length=CFA_LOTS_MAX_SIZE)
    features: list[CFAFeature] | None = None

    @model_field_validator("features")
    def validate_features(self, features):
        validate_cfa_features(self, features)

    @field_validator("agreementDuration")
    @classmethod
    def validate_agreement_duration_items(cls, value):
        validate_cfa_max_agreement_duration_period(value)
        return value

    @field_validator("maxAwardsCount")
    @classmethod
    def validate_max_awards_count_items(cls, value):
        validate_cfa_max_awards_number(value)
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


class CFAPatchTender(PatchTender):
    procurementMethodType: CFAUAProcurementMethodType | None = None
    agreementDuration: IsoDuration | None = None
    maxAwardsCount: int | None = None
    lots: list[PatchTenderLot] | None = Field(None, min_length=CFA_LOTS_MIN_SIZE, max_length=CFA_LOTS_MAX_SIZE)
    features: list[CFAFeature] | None = None

    @field_validator("agreementDuration")
    @classmethod
    def validate_agreement_duration_items(cls, value):
        validate_cfa_max_agreement_duration_period(value)
        return value

    @field_validator("maxAwardsCount")
    @classmethod
    def validate_max_awards_count_items(cls, value):
        validate_cfa_max_awards_number(value)
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


class CFATender(Tender):
    procurementMethodType: CFAUAProcurementMethodType
    agreementDuration: IsoDuration
    maxAwardsCount: int
    lots: list[Lot] = Field(min_length=CFA_LOTS_MIN_SIZE, max_length=CFA_LOTS_MAX_SIZE)
    features: list[CFAFeature] | None = None
    auctionPeriod: Period | None = None

    @model_field_validator("features")
    def validate_features(self, features):
        validate_cfa_features(self, features)

    @field_validator("agreementDuration")
    @classmethod
    def validate_agreement_duration_items(cls, value):
        validate_cfa_max_agreement_duration_period(value)
        return value

    @field_validator("maxAwardsCount")
    @classmethod
    def validate_max_awards_count_items(cls, value):
        validate_cfa_max_awards_number(value)
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
