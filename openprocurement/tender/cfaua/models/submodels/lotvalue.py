from openprocurement.api.models import Model
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import LotValue as BaseLotValue, get_tender
from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.tender.cfaua.models.submodels.value import Value


class LotValue(BaseLotValue):
    class Options:
        roles = RolesFromCsv('LotValue.csv', relative_to=__file__)

    subcontractingDetails = StringType()
    status = StringType(choices=['pending', 'active', 'unsuccessful'], default='pending')
    value = ModelType(Value, required=True)

    def validate_value(self, data, value):
        if value and isinstance(data['__parent__'], Model) and (data['__parent__'].status not in ('invalid', 'deleted', 'draft')) and data['relatedLot']:
            lots = [i for i in get_tender(data['__parent__']).lots if i.id == data['relatedLot']]
            if not lots:
                return
            lot = lots[0]
            if lot.value.amount < value.amount:
                raise ValidationError(u"value of bid should be less than value of lot")
            if lot.get('value').currency != value.currency:
                raise ValidationError(u"currency of bid should be identical to currency of value of lot")
            if lot.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                raise ValidationError(u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot")

    def validate_relatedLot(self, data, relatedLot):
        if isinstance(data['__parent__'], Model) and (data['__parent__'].status not in ('invalid', 'deleted', 'draft')) and relatedLot not in [i.id for i in get_tender(data['__parent__']).lots]:
            raise ValidationError(u"relatedLot should be one of lots")
