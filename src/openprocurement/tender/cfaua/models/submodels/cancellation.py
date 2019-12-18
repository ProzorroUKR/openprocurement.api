from openprocurement.api.models import schematics_embedded_role, schematics_default_role, ListType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import Cancellation as BaseCancellation, EUDocument
from schematics.types import StringType
from schematics.types.compound import ModelType


class Cancellation(BaseCancellation):
    class Options:
        roles = RolesFromCsv("Cancellation.csv", relative_to=__file__)

    documents = ListType(ModelType(EUDocument, required=True), default=list())
    reasonType = StringType(choices=["cancelled", "unsuccessful"], default="cancelled")
