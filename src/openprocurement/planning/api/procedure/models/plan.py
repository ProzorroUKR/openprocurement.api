from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.constants_env import (
    BUDGET_BREAKDOWN_REQUIRED_FROM,
    PLAN_BUYERS_REQUIRED_FROM,
)
from openprocurement.api.context import get_request
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.item import (
    AdditionalClassification,
    validate_items_uniq,
)
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.procedure.utils import is_obj_const_active, to_decimal
from openprocurement.planning.api.constants import (
    MULTI_YEAR_BUDGET_MAX_YEARS,
    MULTI_YEAR_BUDGET_PROCEDURES,
)
from openprocurement.planning.api.procedure.context import get_plan
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
from openprocurement.planning.api.procedure.models.item import CPVClassification, Item
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
from openprocurement.planning.api.procedure.models.tender import Tender
from openprocurement.planning.api.utils import generate_plan_id
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.core.procedure.validation import validate_ccce_ua
from openprocurement.tender.esco.constants import ESCO
from openprocurement.tender.limited.constants import REPORTING
from openprocurement.tender.requestforproposal.constants import REQUEST_FOR_PROPOSAL


class PostPlan(Model):
    @serializable(serialized_name="_id")
    def id(self):
        return uuid4().hex

    @serializable(serialized_name="planID")
    def plan_id(self):
        return generate_plan_id(get_request())

    @serializable
    def doc_type(self):
        return "Plan"

    status = StringType(choices=["draft", "scheduled", "cancelled", "complete"], default="scheduled")
    procuringEntity = ModelType(ProcuringEntity, required=True)
    tender = ModelType(Tender, required=True)
    budget = ModelType(Budget)
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True))
    tender_id = MD5Type()
    mode = StringType(choices=["test"])
    items = ListType(ModelType(Item, required=True), validators=[validate_items_uniq])
    buyers = ListType(ModelType(BuyerOrganization, required=True), min_size=1, max_size=1)
    cancellation = ModelType(PostCancellation)
    documents = ListType(ModelType(PostDocument, required=True))
    rationale = ModelType(RationaleObject)
    project = ModelType(Project)

    def validate_status(self, plan, status):
        validate_status(plan, status)

    def validate_budget(self, plan, budget):
        validate_budget(plan, budget)

    def validate_buyers(self, plan, buyers):
        validate_buyers(plan, buyers)

    def validate_additionalClassifications(self, plan, classifications):
        if classifications is not None:
            validate_ccce_ua(classifications)


class PatchPlan(Model):
    status = StringType(choices=["draft", "scheduled", "cancelled", "complete"])
    procuringEntity = ModelType(ProcuringEntity)
    tender = ModelType(Tender)
    budget = ModelType(Budget)
    classification = ModelType(CPVClassification)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True))
    tender_id = MD5Type()
    mode = StringType(choices=["test"])
    items = ListType(ModelType(Item, required=True), validators=[validate_items_uniq])
    buyers = ListType(ModelType(BuyerOrganization, required=True), min_size=1, max_size=1)
    cancellation = ModelType(PatchCancellation)
    milestones = ListType(ModelType(PatchMilestone, required=True), validators=[validate_items_uniq])
    rationale = ModelType(RationaleObject)
    project = ModelType(Project)


class Plan(Model):
    _id = StringType(deserialize_from=["id", "doc_id"])
    _rev = StringType()
    doc_type = StringType()
    public_modified = BaseType()
    public_ts = BaseType()

    status = StringType(choices=["draft", "scheduled", "cancelled", "complete"])
    procuringEntity = ModelType(ProcuringEntity, required=True)
    tender = ModelType(Tender, required=True)
    budget = ModelType(Budget)
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification))
    tender_id = MD5Type()
    planID = StringType()
    mode = StringType(choices=["test"])
    items = ListType(ModelType(Item, required=True), validators=[validate_items_uniq])
    buyers = ListType(ModelType(BuyerOrganization, required=True), min_size=1, max_size=1)
    cancellation = ModelType(Cancellation)
    documents = ListType(ModelType(Document, required=True))
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])
    rationale = ModelType(RationaleObject)
    project = ModelType(Project, serialize_when_none=True)

    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()

    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    datePublished = IsoDateTimeType()

    is_masked = BooleanType()

    revisions = BaseType()

    def validate_status(self, plan, status):
        validate_status(plan, status)

    def validate_budget(self, plan, budget):
        validate_budget(plan, budget)

    def validate_buyers(self, plan, buyers):
        validate_buyers(plan, buyers)

    def validate_additionalClassifications(self, plan, classifications):
        if classifications is not None:
            validate_ccce_ua(classifications)


def validate_buyers(plan, buyers):
    if not buyers and is_obj_const_active(get_plan(), PLAN_BUYERS_REQUIRED_FROM):
        raise ValidationError("This field is required.")


def validate_status(plan, status):
    if status == "cancelled":
        cancellation = plan.get("cancellation")
        if not cancellation or cancellation.status != "active":
            raise ValidationError("An active cancellation object is required")
    elif status == "complete":
        if not plan.get("tender_id"):
            method = plan.get("tender").get("procurementMethodType")
            if method not in (BELOW_THRESHOLD, REQUEST_FOR_PROPOSAL, REPORTING, ""):
                raise ValidationError("Can't complete plan with '{}' tender.procurementMethodType".format(method))


def validate_budget(plan, budget):
    method_type = plan["tender"]["procurementMethodType"]
    validate_budget_required(plan, budget)
    validate_budget_breakdown_required(plan, budget)
    if method_type not in MULTI_YEAR_BUDGET_PROCEDURES:
        validate_budget_end_date_single_year(plan, budget)
    if method_type in MULTI_YEAR_BUDGET_PROCEDURES:
        validate_budget_end_date_multi_year(plan, budget)
    if method_type != ESCO:
        validate_budget_breakdown_amounts(plan, budget)


def validate_budget_required(plan, budget):
    if not budget:
        raise ValidationError("This field is required.")


def validate_budget_breakdown_required(plan, budget):
    if budget:
        if is_obj_const_active(plan, BUDGET_BREAKDOWN_REQUIRED_FROM):
            if not budget.get("breakdown"):
                raise ValidationError("Breakdown field is required.")


def validate_budget_breakdown_amounts(plan, budget):
    if budget:
        breakdown = budget.get("breakdown")
        if breakdown:
            amounts = [to_decimal(i["value"]["amount"]) for i in breakdown]
            if sum(amounts) > to_decimal(budget["amount"]):
                raise ValidationError("Sum of the breakdown values amounts can't be greater than budget amount")


def validate_budget_end_date_multi_year(plan, budget):
    if budget:
        period = budget.get("period")
        if period:
            start_date = period["startDate"]
            end_date = period["endDate"]
            if end_date.year - start_date.year > MULTI_YEAR_BUDGET_MAX_YEARS:
                raise ValidationError(
                    "Period startDate and endDate must be within {} budget years for {}.".format(
                        MULTI_YEAR_BUDGET_MAX_YEARS + 1,
                        plan["tender"]["procurementMethodType"],
                    )
                )


def validate_budget_end_date_single_year(plan, budget):
    if budget:
        period = budget.get("period")
        if period:
            start_date = period["startDate"]
            end_date = period["endDate"]
            if end_date.year != start_date.year:
                raise ValidationError(
                    "Period startDate and endDate must be within one year for {}.".format(
                        plan["tender"]["procurementMethodType"]
                    )
                )
