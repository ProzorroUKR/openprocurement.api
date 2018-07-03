from openprocurement.api.models import schematics_embedded_role, schematics_default_role, ListType
from openprocurement.frameworkagreement.cfaua.models.submodels.documents import EUDocument
from openprocurement.tender.core.models import Cancellation as BaseCancellation
from schematics.transforms import whitelist
from schematics.types import StringType
from schematics.types.compound import ModelType


class Cancellation(BaseCancellation):
    class Options:
        roles = {
            'create': whitelist('reason', 'status', 'reasonType', 'cancellationOf', 'relatedLot'),
            'edit': whitelist('status', 'reasonType'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    documents = ListType(ModelType(EUDocument), default=list())
    reasonType = StringType(choices=['cancelled', 'unsuccessful'], default='cancelled')