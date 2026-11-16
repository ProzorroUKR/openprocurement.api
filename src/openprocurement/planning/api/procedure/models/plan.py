from typing import Literal
from uuid import uuid4

from pydantic import Field, computed_field, field_validator

from openprocurement.api.constants import UKTZED_SCHEME
from openprocurement.api.context import get_request
from openprocurement.api.procedure.models.base import Model, RootModel, validate_uniq_id
from openprocurement.api.procedure.models.item import AdditionalClassification, CPVClassification, validate_ccce_ua
from openprocurement.api.procedure.types import MD5, IsoDateTime
from openprocurement.planning.api.procedure.models.budget import Budget
from openprocurement.planning.api.procedure.models.cancellation import (
    Cancellation,
    PatchCancellation,
    PostCancellation,
)
from openprocurement.planning.api.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.planning.api.procedure.models.item import Item
from openprocurement.planning.api.procedure.models.milestone import (
    Milestone,
    PatchMilestone,
)
from openprocurement.planning.api.procedure.models.organization import (
    BuyerOrganization,
    ProcuringEntity,
)
from openprocurement.planning.api.procedure.models.project import Project
from openprocurement.planning.api.procedure.models.rationale import RationaleObject
from openprocurement.planning.api.procedure.models.tender import PlanTender
from openprocurement.planning.api.utils import generate_plan_id


def validate_plan_additional_classifications(classifications: list[AdditionalClassification]) -> None:
    validate_ccce_ua(classifications)
    if any(classification.scheme == UKTZED_SCHEME for classification in classifications):
        raise ValueError(f"Forbidden to add {UKTZED_SCHEME}. Should be added in items.additionalClassifications.")


class PostPlan(Model):
    @computed_field(alias="_id")
    def id(self) -> str:
        return uuid4().hex

    @computed_field
    def planID(self) -> str:
        return generate_plan_id(get_request())

    @computed_field
    def doc_type(self) -> str:
        return "Plan"

    status: Literal["draft", "scheduled", "cancelled", "complete"] = "scheduled"
    procuringEntity: ProcuringEntity
    tender: PlanTender
    budget: Budget | None = None
    classification: CPVClassification
    additionalClassifications: list[AdditionalClassification] | None = None
    tender_id: MD5 | None = None
    mode: Literal["test"] | None = None
    items: list[Item] | None = None
    buyers: list[BuyerOrganization] | None = Field(None, min_length=1, max_length=1)
    cancellation: PostCancellation | None = None
    documents: list[PostDocument] | None = None
    rationale: RationaleObject | None = None
    project: Project | None = None

    @field_validator("items")
    @classmethod
    def validate_uniq_ids(cls, value: list) -> list:
        validate_uniq_id(value)
        return value

    @field_validator("additionalClassifications")
    @classmethod
    def validate_additional_classifications(cls, value: list) -> list:
        validate_plan_additional_classifications(value)
        return value


class PatchPlan(Model):
    status: Literal["draft", "scheduled", "cancelled", "complete"] | None = None
    procuringEntity: ProcuringEntity | None = None
    tender: PlanTender | None = None
    budget: Budget | None = None
    classification: CPVClassification | None = None
    additionalClassifications: list[AdditionalClassification] | None = None
    tender_id: MD5 | None = None
    mode: Literal["test"] | None = None
    items: list[Item] | None = None
    buyers: list[BuyerOrganization] | None = Field(None, min_length=1, max_length=1)
    cancellation: PatchCancellation | None = None
    milestones: list[PatchMilestone] | None = None
    rationale: RationaleObject | None = None
    project: Project | None = None

    @field_validator("items", "milestones")
    @classmethod
    def validate_uniq_ids(cls, value: list) -> list:
        validate_uniq_id(value)
        return value


class Plan(RootModel):
    status: Literal["draft", "scheduled", "cancelled", "complete"] | None = None
    procuringEntity: ProcuringEntity
    tender: PlanTender
    budget: Budget | None = None
    classification: CPVClassification
    additionalClassifications: list[AdditionalClassification] | None = None
    tender_id: MD5 | None = None
    planID: str | None = None
    mode: Literal["test"] | None = None
    items: list[Item] | None = None
    buyers: list[BuyerOrganization] | None = Field(None, min_length=1, max_length=1)
    cancellation: Cancellation | None = None
    documents: list[Document] | None = None
    milestones: list[Milestone] | None = None
    rationale: RationaleObject | None = None
    project: Project | None = None

    owner: str | None = None
    owner_token: str | None = None
    transfer_token: str | None = None

    dateCreated: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None
    datePublished: IsoDateTime | None = None

    is_masked: bool | None = None

    @field_validator("items", "milestones")
    @classmethod
    def validate_uniq_ids(cls, value: list) -> list:
        validate_uniq_id(value)
        return value

    @field_validator("additionalClassifications")
    @classmethod
    def validate_additional_classifications(cls, value: list) -> list:
        validate_plan_additional_classifications(value)
        return value
