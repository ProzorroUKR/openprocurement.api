from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.types import MD5Type, BaseType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.types import StringType
from openprocurement.api.context import get_now
from openprocurement.api.models import IsoDateTimeType, ListType, Model
from openprocurement.tender.core.utils import generate_tender_id
from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.tender.core.procedure.models.base import validate_object_id_uniq
from openprocurement.tender.core.procedure.models.document import (
    PostDocument,
    Document,
    validate_tender_document_relations,
)
from openprocurement.tender.core.procedure.models.criterion import Criterion, validate_criteria_requirement_id_uniq
from openprocurement.tender.core.procedure.models.organization import Organization, BaseOrganization
from openprocurement.tender.core.procedure.models.question import validate_questions_related_items, Question
from openprocurement.tender.core.models import (
    validate_funders_unique,
    validate_funders_ids,
)
from openprocurement.api.utils import get_now
from openprocurement.api.constants import (
    MPC_REQUIRED_FROM,
    SANDBOX_MODE,
)


class PlanRelation(Model):
    id = MD5Type(required=True)


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
        ]
    )
    buyers = ListType(ModelType(BaseOrganization, required=True))

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
        validators=[validate_funders_unique, validate_funders_ids]
    )
    plans = ListType(ModelType(PlanRelation, required=True))
    is_masked = BooleanType()

    if SANDBOX_MODE:
        procurementMethodDetails = StringType()

    def validate_plans(self, data, value):
        if value:
            if len(set(i["id"] for i in value)) < len(value):
                raise ValidationError("The list should not contain duplicates")
            if len(value) > 1 and data.get("procuringEntity", {}).get("kind", "") != "central":
                raise ValidationError("Linking more than one plan is allowed only if procuringEntity.kind is 'central'")


class PatchBaseTender(CommonBaseTender):
    criteria = ListType(
        ModelType(Criterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_id_uniq],
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

    def validate_buyers(self, data, value):
        if data.get("procuringEntity", {}).get("kind", "") == "central" and not value:
            raise ValidationError(BaseType.MESSAGES["required"])

    def validate_procurementMethodDetails(self, *args, **kw):
        if self.mode and self.mode == "test" and self.procurementMethodDetails and self.procurementMethodDetails != "":
            raise ValidationError("procurementMethodDetails should be used with mode test")

    def validate_mainProcurementCategory(self, data, value):
        if value is None:
            validation_date = get_first_revision_date(get_tender(), default=get_now())
            if validation_date >= MPC_REQUIRED_FROM:
                raise ValidationError(BaseType.MESSAGES["required"])


class BaseTender(PatchBaseTender):
    _id = StringType(deserialize_from=['id', 'doc_id'])
    _rev = StringType()
    doc_type = StringType()
    public_modified = BaseType()

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
    buyers = ListType(ModelType(BaseOrganization, required=True))

    if SANDBOX_MODE:
        procurementMethodDetails = StringType()

    complaints = BaseType()
    awards = BaseType()
    contracts = BaseType()
    cancellations = BaseType()
    numberOfBids = BaseType()  # deprecated
    _attachments = BaseType()  # deprecated

    def validate_mainProcurementCategory(self, data, value):
        if value is None:
            validation_date = get_first_revision_date(get_tender(), default=get_now())
            if validation_date >= MPC_REQUIRED_FROM:
                raise ValidationError(BaseType.MESSAGES["required"])

    def validate_documents(self, data, documents):
        validate_tender_document_relations(data, documents)

    def validate_questions(self, data, questions):
        validate_questions_related_items(data, questions)
