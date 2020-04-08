from schematics.transforms import whitelist, blacklist
from schematics.types import MD5Type
from openprocurement.api.models import\
    schematics_default_role, schematics_embedded_role
from openprocurement.tender.core.models import BaseAward


class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """

    class Options:
        roles = {
            "create": blacklist("id", "status", "date", "documents"),
            "edit": whitelist(
                "status", "title", "title_en", "title_ru",
                "description", "description_en", "description_ru"
            ),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "Administrator": whitelist(),
        }

    bid_id = MD5Type(required=True)
