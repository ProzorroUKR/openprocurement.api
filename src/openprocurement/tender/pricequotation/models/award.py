from schematics.transforms import whitelist, blacklist
from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType, BaseType
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    schematics_default_role,
    schematics_embedded_role,
    ListType,
)
from openprocurement.api.constants import PQ_MULTI_PROFILE_FROM
from openprocurement.api.utils import get_now, get_first_revision_date

from openprocurement.tender.core.models import BaseAward, Item as BaseAwardItem
from openprocurement.tender.pricequotation.utils import get_bid_owned_award_acl
from openprocurement.tender.pricequotation.validation import validate_profile_pattern


class AwardItem(BaseAwardItem):
    profile = StringType()

    def validate_profile(self, data, value):
        multi_profile_released = get_first_revision_date(data, default=get_now()) > PQ_MULTI_PROFILE_FROM

        if multi_profile_released and not value:
            raise ValidationError(BaseType.MESSAGES["required"])
        if multi_profile_released and value:
            validate_profile_pattern(value)
        if not multi_profile_released and value:
            raise ValidationError("Rogue field.")


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
            "edit_tender_owner": whitelist(
                "status", "title", "title_en", "title_ru",
                "description", "description_en", "description_ru"
            ),
            "edit_bid_owner": whitelist(
                "status", "title", "title_en", "title_ru",
                "description", "description_en", "description_ru"
            ),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "Administrator": whitelist(),
        }

    bid_id = MD5Type(required=True)
    items = ListType(ModelType(AwardItem, required=True))

    def __acl__(self):
        return get_bid_owned_award_acl(self)

    def get_role(self):
        root = self.get_root()
        request = root.request
        if request.authenticated_role in ("tender_owner", "bid_owner"):
            role = "edit_{}".format(request.authenticated_role)
        else:
            role = request.authenticated_role
        return role
