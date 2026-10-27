from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.constants import UKTZED_SCHEME
from openprocurement.api.context import get_request
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.item import AdditionalClassification
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.validation import validate_uniq_id
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
from openprocurement.planning.api.procedure.models.tender import PlanTender
from openprocurement.planning.api.utils import generate_plan_id
from openprocurement.tender.core.procedure.validation import validate_ccce_ua


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
    tender = ModelType(PlanTender, required=True)
    budget = ModelType(Budget)
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True))
    tender_id = MD5Type()
    mode = StringType(choices=["test"])
    items = ListType(ModelType(Item, required=True), validators=[validate_uniq_id])
    buyers = ListType(ModelType(BuyerOrganization, required=True), min_size=1, max_size=1)
    cancellation = ModelType(PostCancellation)
    documents = ListType(ModelType(PostDocument, required=True))
    rationale = ModelType(RationaleObject)
    project = ModelType(Project)

    def validate_additionalClassifications(self, plan, classifications):
        if classifications is not None:
            validate_ccce_ua(classifications)
            validate_uktzed_forbidden(classifications)


class PatchPlan(Model):
    status = StringType(choices=["draft", "scheduled", "cancelled", "complete"])
    procuringEntity = ModelType(ProcuringEntity)
    tender = ModelType(PlanTender)
    budget = ModelType(Budget)
    classification = ModelType(CPVClassification)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True))
    tender_id = MD5Type()
    mode = StringType(choices=["test"])
    items = ListType(ModelType(Item, required=True), validators=[validate_uniq_id])
    buyers = ListType(ModelType(BuyerOrganization, required=True), min_size=1, max_size=1)
    cancellation = ModelType(PatchCancellation)
    milestones = ListType(ModelType(PatchMilestone, required=True), validators=[validate_uniq_id])
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
    tender = ModelType(PlanTender, required=True)
    budget = ModelType(Budget)
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification))
    tender_id = MD5Type()
    planID = StringType()
    mode = StringType(choices=["test"])
    items = ListType(ModelType(Item, required=True), validators=[validate_uniq_id])
    buyers = ListType(ModelType(BuyerOrganization, required=True), min_size=1, max_size=1)
    cancellation = ModelType(Cancellation)
    documents = ListType(ModelType(Document, required=True))
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])
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

    def validate_additionalClassifications(self, plan, classifications):
        if classifications is not None:
            validate_ccce_ua(classifications)
            validate_uktzed_forbidden(classifications)


def validate_uktzed_forbidden(classifications):
    if any(classification["scheme"] == UKTZED_SCHEME for classification in classifications):
        raise ValidationError(f"Forbidden to add {UKTZED_SCHEME}. Should be added in items.additionalClassifications.")
