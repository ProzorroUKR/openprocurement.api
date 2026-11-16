from typing import Literal

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    IsoDateTime,
)
from openprocurement.contracting.econtract.procedure.models.document import Document
from openprocurement.contracting.econtract.procedure.models.value import AmountPaid


class BaseTerminationDetails(Model):
    reasonType: Literal["completed", "disrupted"] | None = None
    reason: str | None = None
    amountPaid: AmountPaid | None = None


class PostTerminationDetails(BaseTerminationDetails):
    pass


class TerminationDetails(BaseTerminationDetails):
    status: Literal["draft", "active"]
    dateCreated: IsoDateTime
    datePublished: IsoDateTime | None = None
    documents: list[Document] | None = None


class PatchContractTerminationDetails(Model):
    terminationDetails: PostTerminationDetails | None = None
