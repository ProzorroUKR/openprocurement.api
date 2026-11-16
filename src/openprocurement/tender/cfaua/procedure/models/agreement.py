from typing import Any, Literal
from uuid import uuid4

from isodate import duration_isoformat
from pydantic import Field, field_validator

from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator, validate_uniq_code, validate_uniq_id
from openprocurement.api.procedure.models.milestone import Milestone
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.cfaua.constants import CFA_UA_MAX_AGREEMENT_PERIOD
from openprocurement.tender.cfaua.procedure.models.agreement_contract import CFAAgreementContract
from openprocurement.tender.cfaua.procedure.models.feature import CFAFeature
from openprocurement.tender.core.procedure.models.feature import validate_related_items
from openprocurement.tender.core.procedure.models.item import Item


class CFAPatchAgreement(Model):
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    status: Literal["pending", "active", "unsuccessful", "cancelled"] | None = None
    period: Period | None = None
    dateSigned: IsoDateTime | None = None
    agreementNumber: str | None = None


class CFAAgreement(Model):
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    agreementID: str | None = None
    agreementNumber: str | None = None
    date: IsoDateTime | None = None
    dateSigned: IsoDateTime | None = None
    features: list[CFAFeature] | None = None
    items: list[Item] | None = None
    period: Period | None = None
    status: Literal["pending", "active", "unsuccessful", "cancelled"]
    contracts: list[CFAAgreementContract] | None = None
    milestones: list[Milestone] | None = None
    documents: Any = None

    @model_field_validator("features")
    def validate_features(self, features):
        validate_related_items(self, features)

    @model_field_validator("period")
    def validate_period(self, value):
        if self.status == "active":
            if not value:
                raise ValidationError("Period is required for agreement signing.")
            if not value.startDate or not value.endDate:
                raise ValidationError("startDate and endDate are required in agreement.period.")
            calculated_end_date = value.startDate + CFA_UA_MAX_AGREEMENT_PERIOD
            if value.endDate > calculated_end_date:
                raise ValidationError(
                    f"Agreement period can't be greater than {duration_isoformat(CFA_UA_MAX_AGREEMENT_PERIOD)}."
                )

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
