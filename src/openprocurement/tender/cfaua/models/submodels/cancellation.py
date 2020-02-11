from openprocurement.api.models import ListType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import (
    Cancellation as BaseCancellation,
    EUDocument,
)

from schematics.types.compound import ModelType


class Cancellation(BaseCancellation):
    class Options:
        roles = RolesFromCsv("Cancellation.csv", relative_to=__file__)

    documents = ListType(ModelType(EUDocument, required=True), default=list())
