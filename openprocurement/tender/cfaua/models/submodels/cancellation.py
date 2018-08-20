from openprocurement.api.models import schematics_embedded_role, schematics_default_role, ListType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaua.models.submodels.documents import EUDocument
from openprocurement.tender.core.models import Cancellation as BaseCancellation
from schematics.types import StringType
from schematics.types.compound import ModelType


class Cancellation(BaseCancellation):
    class Options:
        roles = RolesFromCsv('Cancellation.csv', relative_to=__file__)

    documents = ListType(ModelType(EUDocument), default=list())
    reasonType = StringType(choices=['cancelled', 'unsuccessful'], default='cancelled')
