from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import Item as BaseItem
from openprocurement.api.utils import get_now, get_first_revision_date
from openprocurement.api.constants import UNIT_PRICE_REQUIRED_FROM
from schematics.exceptions import ValidationError


class Item(BaseItem):
    class Options:
        roles = RolesFromCsv("Item.csv", relative_to=__file__)

    def validate_unit(self, data, value):
        _parent = data['__parent__']
        validation_date = get_first_revision_date(_parent, default=get_now())
        if validation_date >= UNIT_PRICE_REQUIRED_FROM and not value:
            raise ValidationError(u"This field is required.")

    def validate_quantity(self, data, value):
        _parent = data['__parent__']
        validation_date = get_first_revision_date(_parent, default=get_now())
        if validation_date >= UNIT_PRICE_REQUIRED_FROM and value is None:
            raise ValidationError(u"This field is required.")
