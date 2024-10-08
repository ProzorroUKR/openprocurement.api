from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, IntType, MD5Type, StringType
from schematics.types.compound import DictType
from schematics.types.serializable import serializable

from openprocurement.api.constants import DK_CODES, SANDBOX_MODE
from openprocurement.api.context import get_request
from openprocurement.api.procedure.models.base import Model, RootModel
from openprocurement.api.procedure.models.item import (
    Classification as BaseClassification,
)
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.framework.core.procedure.models.question import Question
from openprocurement.framework.core.utils import generate_framework_pretty_id
from openprocurement.framework.dps.constants import DPS_TYPE


class DKClassification(BaseClassification):
    scheme = StringType(required=True, choices=["ДК021"])
    id = StringType(required=True)

    def validate_id(self, data, id):
        if id not in DK_CODES:
            raise ValidationError(BaseType.MESSAGES["choices"].format(DK_CODES))


class EnquiryPeriod(PeriodEndRequired):
    clarificationsUntil = IsoDateTimeType()


class PostFramework(Model):
    @serializable(serialized_name="_id")
    def id(self):
        return uuid4().hex

    @serializable(serialized_name="prettyID")
    def pretty_id(self):
        return generate_framework_pretty_id(get_request())

    @serializable
    def doc_type(self):
        return "Framework"

    status = StringType(choices=["draft"], default="draft")
    title = StringType(required=True)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    mode = StringType(choices=["test"])
    if SANDBOX_MODE:
        frameworkDetails = StringType()
    qualificationPeriod = ModelType(PeriodEndRequired, required=True)
    procuringEntity = ModelType(BaseOrganization, required=True)
    classification = ModelType(DKClassification, required=True)
    additionalClassifications = ListType(ModelType(BaseClassification))
    documents = ListType(ModelType(PostDocument, required=True), default=[])
    agreementID = StringType()

    def validate_frameworkDetails(self, *args, **kw):
        if self.mode == "test" and self.frameworkDetails and self.frameworkDetails != "":
            raise ValidationError("frameworkDetails should be used with mode test")


class PatchFramework(Model):
    status = StringType(
        choices=[
            "active",
            "complete",
            "unsuccessful",
        ]
    )
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    qualificationPeriod = ModelType(PeriodEndRequired)
    procuringEntity = ModelType(BaseOrganization)
    classification = ModelType(DKClassification)
    additionalClassifications = ListType(ModelType(BaseClassification))
    documents = ListType(ModelType(PostDocument))
    agreementID = StringType()


class Framework(RootModel):
    prettyID = StringType()
    title = StringType(required=True)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    frameworkType = StringType(required=True)
    status = StringType(
        choices=[
            "draft",
            "active",
            "complete",
            "unsuccessful",
        ],
        default="draft",
    )
    mode = StringType(choices=["test"])
    if SANDBOX_MODE:
        frameworkDetails = StringType()
    procuringEntity = ModelType(BaseOrganization, required=True)
    classification = ModelType(DKClassification, required=True)
    additionalClassifications = ListType(ModelType(BaseClassification))
    documents = ListType(ModelType(Document, required=True), default=[])
    agreementID = StringType()
    questions = ListType(ModelType(Question, required=True))

    successful = BooleanType(required=True, default=False)

    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()

    date = IsoDateTimeType()
    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    period = ModelType(PeriodEndRequired)
    qualificationPeriod = ModelType(PeriodEndRequired, required=True)
    enquiryPeriod = ModelType(EnquiryPeriod)

    _attachments = DictType(DictType(BaseType), default=[])  # couchdb attachments
    revisions = BaseType()
    next_check = BaseType()
    config = BaseType()


class FrameworkChronographData(Model):
    _id = MD5Type(deserialize_from=["id"])
    next_check = BaseType()


class PatchActiveFramework(Model):
    status = StringType(
        choices=[
            "active",
            "complete",
            "unsuccessful",
        ],
    )
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    qualificationPeriod = ModelType(PeriodEndRequired)
    procuringEntity = ModelType(BaseOrganization)
    documents = ListType(ModelType(PostDocument))
    if SANDBOX_MODE:
        frameworkDetails = StringType()


class FrameworkConfig(Model):
    test = BooleanType()
    clarificationUntilDuration = IntType(min_value=0)
    restrictedDerivatives = BooleanType()
    qualificationComplainDuration = IntType(min_value=0)

    def validate_restrictedDerivatives(self, data, value):
        framework = get_request().validated.get("data")
        if not framework:
            return
        if framework.get("frameworkType") == DPS_TYPE:
            if value is None:
                raise ValidationError("restrictedDerivatives is required for this framework type")
            if framework.get("procuringEntity", {}).get("kind") == "defense":
                if value is False:
                    raise ValidationError("restrictedDerivatives must be true for defense procuring entity")
            else:
                if value is True:
                    raise ValidationError("restrictedDerivatives must be false for non-defense procuring entity")
        else:
            if value is True:
                raise ValidationError("restrictedDerivatives must be false for this framework type")
