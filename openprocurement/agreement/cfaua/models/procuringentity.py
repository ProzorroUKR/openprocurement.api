from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    schematics_embedded_role,
    schematics_default_role,
    ListType,
    Organization
    )

from openprocurement.agreement.cfaua.models.contactpoint\
    import ContactPoint


class ProcuringEntity(Organization):
    """An organization."""
    class Options:
        # TODO: do we really need roles here
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    kind = StringType(choices=['general', 'special', 'defense', 'other'])
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(
        ModelType(ContactPoint, required=True),
        required=False
    )
