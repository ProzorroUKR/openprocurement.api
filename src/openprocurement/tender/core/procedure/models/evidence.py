from typing import Literal
from uuid import uuid4

from pydantic import Field

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.reference import Reference
from openprocurement.api.procedure.types import (
    MD5,
)


class BaseEligibleEvidence(Model):
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    type: Literal["document", "statement"] = "statement"
    relatedDocument: Reference | None = None


class EligibleEvidence(BaseEligibleEvidence):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)


class PatchEvidence(BaseEligibleEvidence):
    type: Literal["document", "statement"] | None = None


class Evidence(EligibleEvidence):
    # relatedDocument is required for the document type by the state (validate_evidence_related_document)
    pass
