from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field, field_validator

from openprocurement.api.constants import (
    CCCE_UA,
    CCCE_UA_SCHEME,
    DK_CODES,
    SANDBOX_MODE,
    FrameworkType,
)
from openprocurement.api.context import get_request
from openprocurement.api.procedure.errors import ConversionError, ValidationError
from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import DocumentIdMixin, Model, model_field_validator
from openprocurement.api.procedure.models.item import (
    AdditionalClassification as BaseAdditionalClassification,
)
from openprocurement.api.procedure.models.item import (
    Classification as BaseClassification,
)
from openprocurement.api.procedure.models.item import CPVClassification, validate_ccce_ua
from openprocurement.api.procedure.models.item import Item as BaseItem
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.models.unit import Unit
from openprocurement.api.procedure.types import (
    IsoDateTime,
)
from openprocurement.framework.core.procedure.models.base import FrameworkRootModel
from openprocurement.framework.core.procedure.models.change import Change
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.framework.core.procedure.models.question import Question
from openprocurement.framework.core.utils import generate_framework_pretty_id


def validate_sandbox_only(value):
    """a field allowed in the sandbox mode only"""
    if value and not SANDBOX_MODE:
        raise ConversionError("Rogue field")


class Item(BaseItem):
    classification: CPVClassification
    additionalClassifications: list[BaseAdditionalClassification] = []
    deliveryDate: PeriodEndRequired
    deliveryAddress: Address
    unit: Unit


class DKClassification(BaseClassification):
    scheme: Literal["ДК021"]
    id: str

    @field_validator("id")
    @classmethod
    def validate_id(cls, id):
        if id not in DK_CODES:
            raise ValidationError("Value must be one of {0}.".format(DK_CODES))
        return id


class AdditionalClassification(BaseClassification):
    @model_field_validator("id")
    def validate_id(self, value):
        if self.scheme == CCCE_UA_SCHEME and value not in CCCE_UA:
            raise ValidationError(f"{CCCE_UA_SCHEME} id not found in standards")


class EnquiryPeriod(PeriodEndRequired):
    clarificationsUntil: IsoDateTime | None = None


class PostFramework(Model):
    @computed_field(alias="_id")
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def prettyID(self) -> Any:
        return generate_framework_pretty_id(get_request())

    @computed_field
    def doc_type(self) -> Any:
        return "Framework"

    status: Literal["draft"] = "draft"
    title: str
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    mode: Literal["test"] | None = None

    frameworkDetails: str | None = None  # the sandbox mode only

    @field_validator("frameworkDetails")
    @classmethod
    def validate_framework_details(cls, value):
        validate_sandbox_only(value)
        return value

    qualificationPeriod: PeriodEndRequired
    procuringEntity: BaseOrganization
    items: list[Item] | None = None
    classification: DKClassification
    additionalClassifications: list[AdditionalClassification] | None = None
    documents: list[PostDocument] = []
    agreementID: str | None = None

    @field_validator("additionalClassifications")
    @classmethod
    def validate_additional_classifications(cls, classifications):
        if classifications is not None:
            validate_ccce_ua(classifications)
        return classifications


class PatchFramework(Model):
    status: Literal["active", "complete", "unsuccessful"] | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    qualificationPeriod: PeriodEndRequired | None = None
    procuringEntity: BaseOrganization | None = None
    items: list[Item] | None = None
    classification: DKClassification | None = None
    additionalClassifications: list[AdditionalClassification] | None = None
    documents: list[PostDocument] | None = None
    agreementID: str | None = None


class Framework(FrameworkRootModel):
    prettyID: str | None = None
    title: str
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    frameworkType: FrameworkType
    status: Literal["draft", "active", "complete", "unsuccessful"] = "draft"
    mode: Literal["test"] | None = None

    frameworkDetails: str | None = None  # the sandbox mode only

    @field_validator("frameworkDetails")
    @classmethod
    def validate_framework_details(cls, value):
        validate_sandbox_only(value)
        return value

    procuringEntity: BaseOrganization
    items: list[Item] | None = None
    classification: DKClassification
    additionalClassifications: list[AdditionalClassification] | None = None
    documents: list[Document] = []
    agreementID: str | None = None
    questions: list[Question] | None = None
    successful: bool = False
    owner: str | None = None
    owner_token: str | None = None
    transfer_token: str | None = None
    date: IsoDateTime | None = None
    dateCreated: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None
    period: PeriodEndRequired | None = None
    qualificationPeriod: PeriodEndRequired
    enquiryPeriod: EnquiryPeriod | None = None
    changes: list[Change] | None = None
    attachments_: dict[str, Any] = Field(default_factory=dict, alias="_attachments")
    next_check: Any = None
    config: Any = None

    @field_validator("additionalClassifications")
    @classmethod
    def validate_additional_classifications(cls, classifications):
        if classifications is not None:
            validate_ccce_ua(classifications)
        return classifications


class FrameworkChronographData(DocumentIdMixin):
    next_check: Any = None


class PatchActiveFramework(Model):
    status: Literal["active", "complete", "unsuccessful"] | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    procuringEntity: BaseOrganization | None = None
    documents: list[PostDocument] | None = None

    frameworkDetails: str | None = None  # the sandbox mode only

    @field_validator("frameworkDetails")
    @classmethod
    def validate_framework_details(cls, value):
        validate_sandbox_only(value)
        return value
