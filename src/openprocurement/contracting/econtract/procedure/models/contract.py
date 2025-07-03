from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.contracting.core.procedure.models.contract import (
    Contract as BaseContract,
)
from openprocurement.contracting.core.procedure.models.contract import (
    PostContract as BasePostContract,
)
from openprocurement.contracting.econtract.procedure.models.cancellation import (
    Cancellation,
)
from openprocurement.contracting.econtract.procedure.models.document import Document


class PostContract(BasePostContract):
    author = StringType()


class Contract(BaseContract):
    documents = ListType(ModelType(Document, required=True))
    cancellations = ListType(ModelType(Cancellation, required=True))
    author = StringType()
