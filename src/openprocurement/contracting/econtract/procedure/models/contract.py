from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.contracting.core.procedure.models.contract import (
    Contract as BaseContract,
)
from openprocurement.contracting.econtract.procedure.models.document import Document


class Contract(BaseContract):
    documents = ListType(ModelType(Document, required=True))
