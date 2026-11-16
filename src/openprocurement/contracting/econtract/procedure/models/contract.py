from openprocurement.contracting.core.procedure.models.contract import (
    Contract as BaseContract,
)
from openprocurement.contracting.core.procedure.models.contract import (
    PostContract as BasePostContract,
)
from openprocurement.contracting.econtract.procedure.models.cancellation import (
    Cancellation,
)
from openprocurement.contracting.econtract.procedure.models.change import Change
from openprocurement.contracting.econtract.procedure.models.document import Document
from openprocurement.contracting.econtract.procedure.models.signatory import Signatory
from openprocurement.contracting.econtract.procedure.models.termination_details import (
    TerminationDetails,
)


class PostContract(BasePostContract):
    author: str | None = None


class Contract(BaseContract):
    changes: list[Change] | None = None
    documents: list[Document] | None = None
    cancellations: list[Cancellation] | None = None
    author: str | None = None
    signatories: list[Signatory] | None = None
    terminationDetails: TerminationDetails | None = None
