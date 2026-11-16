from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.constants import AgreementType
from openprocurement.api.procedure.models.base import DocumentIdMixin, Model
from openprocurement.api.procedure.models.organization import Organization
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.framework.core.procedure.models.base import FrameworkRootModel
from openprocurement.framework.core.procedure.models.contract import Contract
from openprocurement.framework.core.procedure.models.framework import (
    AdditionalClassification,
    DKClassification,
    Item,
)


class PatchAgreement(Model):
    status: Literal["active", "terminated"] | None = None
    terminationDetails: str | None = None


class CommonAgreement(FrameworkRootModel):
    agreementID: str | None = None
    agreementType: AgreementType = AgreementType.DYNAMIC_PURCHASING_SYSTEM
    status: Literal["active", "terminated"]
    period: PeriodEndRequired | None = None
    procuringEntity: Organization
    contracts: list[Contract] = []
    terminationDetails: str | None = None
    attachments_: dict[str, Any] = Field(default_factory=dict, alias="_attachments")
    dateCreated: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None
    date: IsoDateTime | None = None
    owner: str | None = None
    owner_token: str | None = None
    transfer_token: str | None = None
    config: Any = None
    mode: Literal["test"] | None = None


class CommonPostAgreement(Model):
    @computed_field
    def doc_type(self) -> Any:
        return "Agreement"

    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    agreementID: str | None = None
    agreementType: AgreementType = AgreementType.DYNAMIC_PURCHASING_SYSTEM
    status: Literal["active"]
    period: PeriodEndRequired | None = None
    procuringEntity: Organization
    contracts: list[Contract] = []
    terminationDetails: str | None = None
    attachments_: dict[str, Any] = Field(default_factory=dict, alias="_attachments")
    dateCreated: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None
    date: IsoDateTime | None = None
    owner: str | None = None
    owner_token: str | None = None
    transfer_token: str = Field(default_factory=lambda: uuid4().hex)
    revisions: Any = []
    config: Any = None
    mode: Literal["test"] | None = None


class AgreementChronographData(DocumentIdMixin):
    next_check: Any = None


class Agreement(CommonAgreement):
    frameworkID: str | None = None
    classification: DKClassification
    additionalClassifications: list[AdditionalClassification] | None = None
    frameworkDetails: str | None = None
    items: list[Item] = []
    next_check: Any = None
