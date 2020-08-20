from openprocurement.api.constants import CPV_ITEMS_CLASS_FROM
from openprocurement.api.validation import validate_cpv_group
from schematics.exceptions import ValidationError
from openprocurement.api.utils import get_now


class TenderCPVItemsValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, items):
        cpv_336_group = items[0].classification.id[:3] == "336" if items else False
        if (
            not cpv_336_group
            and (data.get("revisions")[0].date if data.get("revisions") else get_now()) > CPV_ITEMS_CLASS_FROM
            and items
            and len(set([i.classification.id[:4] for i in items])) != 1
        ):
            raise ValidationError(u"CPV class of items should be identical")
        else:
            validate_cpv_group(items)
