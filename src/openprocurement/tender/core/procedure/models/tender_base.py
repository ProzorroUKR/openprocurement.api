from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.constants_env import MPC_REQUIRED_FROM
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.tender.core.constants import PROCUREMENT_METHODS
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.agreement import AgreementUUID
from openprocurement.tender.core.procedure.models.criterion import (
    Criterion,
    validate_criteria_requirement_uniq,
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
from openprocurement.tender.core.procedure.models.question import (
    Question,
    validate_questions_related_items,
)
from openprocurement.tender.core.procedure.models.review_request import ReviewRequest
from openprocurement.tender.core.procedure.utils import (
    generate_tender_id,
    tender_created_after,
)
from openprocurement.tender.core.procedure.validation import (
    validate_funders_ids,
    validate_funders_unique,
    validate_object_id_uniq,
)


class PlanRelation(Model):
    id = MD5Type(required=True)


def validate_plans(data, value):
    if value:
        if len({i["id"] for i in value}) < len(value):
            raise ValidationError("The list should not contain duplicates")
        if len(value) > 1 and data.get("procuringEntity", {}).get("kind", "") != "central":
            raise ValidationError("Linking more than one plan is allowed only if procuringEntity.kind is 'central'")


def validate_inspector(data, value):
    if value:
        if not data.get("funders"):
            raise ValidationError("Inspector couldn't exist without funders")


class CommonBaseTender(Model):
    mainProcurementCategory = StringType(choices=["goods", "services", "works"])
    awardCriteriaDetails = StringType()  # Any detailed or further information on the selection criteria.
    awardCriteriaDetails_en = StringType()
    awardCriteriaDetails_ru = StringType()
    eligibilityCriteria = StringType()  # A description of any eligibility criteria for potential suppliers.
    eligibilityCriteria_en = StringType()
    eligibilityCriteria_ru = StringType()
    status = StringType(
        choices=[
            "draft",
            "active.enquiries",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ]
    )
    buyers = ListType(ModelType(Buyer, required=True))

    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    documents = ListType(ModelType(PostDocument, required=True))  # All documents and attachments related to the tender.
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    procurementMethodRationale = StringType()
    procurementMethodRationale_en = StringType()
    procurementMethodRationale_ru = StringType()
    funders = ListType(
        ModelType(Organization, required=True),
        validators=[validate_funders_unique, validate_funders_ids],
    )
    is_masked = BooleanType()

    procurementMethod = StringType(choices=PROCUREMENT_METHODS)
    contractTemplateName = StringType()

    if SANDBOX_MODE:
        procurementMethodDetails = StringType()


class PatchBaseTender(CommonBaseTender):
    criteria = ListType(
        ModelType(Criterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_uniq],
    )


class PostBaseTender(CommonBaseTender):
    @serializable(serialized_name="_id")
    def id(self):
        return uuid4().hex

    @serializable(serialized_name="tenderID")
    def serialize_tender_id(self):
        return generate_tender_id(get_request())

    @serializable
    def doc_type(self):
        return "Tender"

    title = StringType(required=True)
    mode = StringType(choices=["test"])

    if SANDBOX_MODE:
        procurementMethodDetails = StringType()

    status = StringType(choices=["draft"], default="draft")
    agreements = ListType(ModelType(AgreementUUID, required=True), min_size=1, max_size=1)
    inspector = ModelType(Organization)
    plans = ListType(ModelType(PlanRelation, required=True))

    def validate_buyers(self, data, value):
        if data.get("procuringEntity", {}).get("kind", "") == "central" and not value:
            raise ValidationError(BaseType.MESSAGES["required"])

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_procurementMethodDetails(self, data, value):
        if self.mode and self.mode == "test" and self.procurementMethodDetails and self.procurementMethodDetails != "":
            raise ValidationError("procurementMethodDetails should be used with mode test")

    def validate_mainProcurementCategory(self, data, value):
        if value is None:
            if tender_created_after(MPC_REQUIRED_FROM):
                raise ValidationError(BaseType.MESSAGES["required"])

    def validate_inspector(self, data, value):
        validate_inspector(data, value)

    def validate_plans(self, data, value):
        validate_plans(data, value)


class BaseTender(PatchBaseTender):
    _id = StringType(deserialize_from=["id", "doc_id"])
    _rev = StringType()
    doc_type = StringType()
    public_modified = BaseType()
    public_ts = BaseType()

    date = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    dateCreated = IsoDateTimeType()
    tenderID = StringType()
    revisions = BaseType()
    bids = BaseType()
    questions = ListType(ModelType(Question, required=True))
    documents = ListType(ModelType(Document, required=True))
    status = StringType(
        choices=[
            "draft",
            "active.enquiries",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ]
    )
    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()
    title = StringType(required=True)
    mode = StringType(choices=["test"])
    mainProcurementCategory = StringType(choices=["goods", "services", "works"])
    buyers = ListType(ModelType(Buyer, required=True))
    agreements = ListType(ModelType(AgreementUUID, required=True), min_size=1, max_size=1)
    inspector = ModelType(Organization)
    reviewRequests = ListType(ModelType(ReviewRequest, required=True))

    procurementMethod = StringType(choices=PROCUREMENT_METHODS, required=True)
    noticePublicationDate = IsoDateTimeType()
    plans = ListType(ModelType(PlanRelation, required=True))

    if SANDBOX_MODE:
        procurementMethodDetails = StringType()

    complaints = BaseType()
    awards = BaseType()
    contracts = BaseType()
    cancellations = BaseType()

    config = BaseType()

    numberOfBids = BaseType()  # deprecated
    _attachments = BaseType()  # deprecated

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_mainProcurementCategory(self, data, value):
        if value is None:
            if tender_created_after(MPC_REQUIRED_FROM):
                raise ValidationError(BaseType.MESSAGES["required"])

    def validate_documents(self, data, documents):
        validate_tender_document_relations(data, documents)

    def validate_questions(self, data, questions):
        validate_questions_related_items(data, questions)

    def validate_inspector(self, data, value):
        validate_inspector(data, value)

    def validate_plans(self, data, value):
        validate_plans(data, value)
