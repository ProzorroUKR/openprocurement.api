from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.framework.core.procedure.models.milestone import Milestone
from openprocurement.framework.core.procedure.models.organization import (
    ContractBusinessOrganization,
)


class PatchContract(Model):
    suppliers: list[ContractBusinessOrganization] | None = Field(None, min_length=1)

    @field_validator("suppliers")
    @classmethod
    def validate_suppliers(cls, suppliers):
        if suppliers and len(suppliers) != 1:
            raise ValidationError("Contract must have only one supplier")
        return suppliers


class Contract(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    qualificationID: str | None = None
    status: Literal["active", "suspended", "terminated"] | None = None
    submissionID: str | None = None
    suppliers: list[ContractBusinessOrganization] = Field(min_length=1)
    milestones: list[Milestone] = Field(min_length=1)
    date: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None

    @field_validator("suppliers")
    @classmethod
    def validate_suppliers(cls, suppliers):
        if len(suppliers) != 1:
            raise ValidationError("Contract must have only one supplier")
        return suppliers
