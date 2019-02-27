from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    ListType,
    Organization
    )

from openprocurement.agreement.cfaua.models.contactpoint\
    import ContactPoint


class ProcuringEntity(Organization):
    """An organization."""
    class Options:
        # TODO: do we really need roles here
        roles = RolesFromCsv('ProcuringEntity.csv', relative_to=__file__)

    kind = StringType(choices=['general', 'special', 'defense', 'other'])
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(
        ModelType(ContactPoint, required=True),
        required=False
    )
