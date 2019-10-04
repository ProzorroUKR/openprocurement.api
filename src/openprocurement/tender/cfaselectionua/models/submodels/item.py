from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import Item as BaseItem


class Item(BaseItem):
    class Options:
        roles = RolesFromCsv("Item.csv", relative_to=__file__)
