from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field, field_validator

from openprocurement.api.constants import FUNDERS, SANDBOX_MODE, TENDER_PROCEDURE_JSONSCHEMAS
from openprocurement.api.procedure.errors import ConversionError, ValidationError
from openprocurement.api.procedure.models.base import Model, RootModel, model_field_validator, validate_object_id_uniq
from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.core.constants import ProcurementMethod
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.agreement import AgreementUUID
from openprocurement.tender.core.procedure.models.criterion import (
    Criterion,
)
from openprocurement.tender.core.procedure.models.document import (
    Document,
    PostDocument,
    validate_tender_document_relations,
)
from openprocurement.tender.core.procedure.models.item import (
    validate_related_buyer_in_items,
)
from openprocurement.tender.core.procedure.models.organization import (
    Buyer,
    Organization,
)
from openprocurement.tender.core.procedure.models.period import QualificationPeriod
from openprocurement.tender.core.procedure.models.question import (
    Question,
    validate_questions_related_items,
)
from openprocurement.tender.core.procedure.models.review_request import ReviewRequest
from openprocurement.tender.core.procedure.utils import (
    generate_tender_id,
)


class MainProcurementCategory(StrEnum):
    GOODS = "goods"
    SERVICES = "services"
    WORKS = "works"


MAIN_PROCUREMENT_CATEGORY_CHOICES = [
    MainProcurementCategory.GOODS.value,
    MainProcurementCategory.SERVICES.value,
    MainProcurementCategory.WORKS.value,
]


class PlanRelation(Model):
    id: MD5


def validate_plans(plan_ids, procuring_entity_kind):
    if plan_ids:
        if len(set(plan_ids)) < len(plan_ids):
            raise ValidationError("The list should not contain duplicates")
        if len(plan_ids) > 1 and procuring_entity_kind != ProcuringEntityKind.CENTRAL:
            raise ValidationError(
                "Linking more than one plan is allowed only if procuringEntity.kind is '{}'".format(
                    ProcuringEntityKind.CENTRAL
                )
            )


def validate_inspector(tender, value):
    if value:
        if not tender.funders:
            raise ValidationError("Inspector couldn't exist without funders")


class CommonBaseTender(Model):
    mainProcurementCategory: str | None = None
    awardCriteriaDetails: str | None = None
    awardCriteriaDetails_en: str | None = None
    awardCriteriaDetails_ru: str | None = None
    eligibilityCriteria: str | None = None
    eligibilityCriteria_en: str | None = None
    eligibilityCriteria_ru: str | None = None
    status: (
        Literal[
            "draft",
            "draft.pending",
            "draft.unsuccessful",
            "active",
            "active.enquiries",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.qualification.stand-still",
            "active.awarded",
            "active.stage2.waiting",
            "complete",
            "cancelled",
            "unsuccessful",
        ]
        | None
    ) = None
    buyers: list[Buyer] | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    documents: list[PostDocument] | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    procurementMethodRationale: str | None = None
    procurementMethodRationale_en: str | None = None
    procurementMethodRationale_ru: str | None = None
    funders: list[Organization] | None = None
    is_masked: bool | None = None
    procurementMethod: ProcurementMethod | None = None
    contractTemplateName: str | None = None

    procurementMethodDetails: str | None = None  # the sandbox mode only

    @field_validator("procurementMethodDetails")
    @classmethod
    def validate_procurement_method_details(cls, value):
        if value and not SANDBOX_MODE:
            raise ConversionError("Rogue field")
        return value

    @field_validator("funders")
    @classmethod
    def validate_funders_items(cls, value):
        validate_funders_ids(value)
        return value


class PatchBaseTender(CommonBaseTender):
    criteria: list[Criterion] | None = None

    @field_validator("criteria")
    @classmethod
    def validate_criteria_items(cls, value):
        validate_object_id_uniq(value)
        return value


class PostBaseTender(CommonBaseTender):
    @computed_field(alias="_id")
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def tenderID(self) -> Any:
        return generate_tender_id(get_request())

    @computed_field
    def doc_type(self) -> Any:
        return "Tender"

    title: str
    mode: Literal["test"] | None = None

    status: Literal["draft"] = "draft"
    agreements: list[AgreementUUID] | None = Field(None, min_length=1, max_length=1)
    inspector: Organization | None = None
    plans: list[PlanRelation] | None = None
    procedure: Any = None

    @model_field_validator("buyers")
    def validate_buyers(self, value):
        procuring_entity = getattr(self, "procuringEntity", None)  # not a field of PostBaseTender itself
        procuring_entity_kind = procuring_entity.kind if procuring_entity else None
        if procuring_entity_kind == ProcuringEntityKind.CENTRAL and (not value):
            raise ValidationError("This field is required.")
        elif procuring_entity_kind != ProcuringEntityKind.CENTRAL and value:
            raise ValidationError("Rogue field.")

    @model_field_validator("items")
    def validate_items(self, items):
        validate_related_buyer_in_items(self, items)

    @model_field_validator("inspector")
    def validate_inspector(self, value):
        validate_inspector(self, value)

    @model_field_validator("plans")
    def validate_plans(self, value):
        procuring_entity = getattr(self, "procuringEntity", None)
        validate_plans([plan.id for plan in value or []], procuring_entity.kind if procuring_entity else None)

    @model_field_validator("procedure")
    def validate_procedure(self, value):
        if TENDER_PROCEDURE_JSONSCHEMAS.get(getattr(self, "procurementMethodType", None)) is None:
            if value is not None:
                raise ValidationError("Rogue field.")
        elif value is None:
            raise ValidationError("This field is required.")


class BaseTender(PatchBaseTender, RootModel):
    date: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None
    dateCreated: IsoDateTime | None = None
    tenderID: str | None = None
    bids: Any = None
    questions: list[Question] | None = None
    documents: list[Document] | None = None
    status: Literal[
        "draft",
        "draft.pending",
        "draft.unsuccessful",
        "draft.stage2",
        "active",
        "active.enquiries",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.auction",
        "active.qualification",
        "active.qualification.stand-still",
        "active.awarded",
        "active.stage2.pending",
        "active.stage2.waiting",
        "complete",
        "cancelled",
        "unsuccessful",
    ]
    owner: str | None = None
    owner_token: str | None = None
    transfer_token: str | None = None
    title: str
    mode: Literal["test"] | None = None
    mainProcurementCategory: str | None = None
    buyers: list[Buyer] | None = None
    agreements: list[AgreementUUID] | None = Field(None, min_length=1, max_length=1)
    inspector: Organization | None = None
    reviewRequests: list[ReviewRequest] | None = None
    procurementMethod: ProcurementMethod
    noticePublicationDate: IsoDateTime | None = None
    plans: list[PlanRelation] | None = None
    procedure: Any = None

    complaints: Any = None
    awards: Any = None
    contracts: Any = None
    cancellations: Any = None
    qualifications: Any = None
    qualificationPeriod: QualificationPeriod | None = None
    complaintPeriod: Any = None
    next_check: Any = None
    contractChangeRationaleTypes: Any = None
    config: Any = None
    numberOfBids: Any = None
    attachments_: Any = Field(None, alias="_attachments")

    @model_field_validator("items")
    def validate_items(self, items):
        validate_related_buyer_in_items(self, items)

    @model_field_validator("documents")
    def validate_documents(self, documents):
        validate_tender_document_relations(self, documents)

    @model_field_validator("questions")
    def validate_questions(self, questions):
        validate_questions_related_items(self, questions)

    @model_field_validator("inspector")
    def validate_inspector(self, value):
        validate_inspector(self, value)

    @model_field_validator("plans")
    def validate_plans(self, value):
        procuring_entity = getattr(self, "procuringEntity", None)
        validate_plans([plan.id for plan in value or []], procuring_entity.kind if procuring_entity else None)


def validate_funders_ids(funders, *args):
    for funder in funders:
        if funder.identifier and (funder.identifier.scheme, funder.identifier.id) not in FUNDERS:
            raise ValidationError("Funder identifier should be one of the values allowed")
