# -*- coding: utf-8 -*-
from decimal import Decimal
from openprocurement.api.models import DecimalType, Model
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import Parameter as BaseParameter, bids_validation_wrapper, get_tender
from schematics.exceptions import ValidationError


class Parameter(BaseParameter):
    class Options:
        roles = RolesFromCsv('Parameter.csv', relative_to=__file__)

    value = DecimalType(required=True, precision=-2)

    @bids_validation_wrapper
    def validate_value(self, data, value):
        if isinstance(data['__parent__'], Model):
            tender = get_tender(data['__parent__'])
            codes = dict([(i.code, [x.value for x in i.enum]) for i in (tender.features or [])])
            if data['code'] in codes and Decimal(str(value)) not in codes[data['code']]:
                raise ValidationError(u"value should be one of feature value.")

    @bids_validation_wrapper
    def validate_code(self, data, code):
        BaseParameter._validator_functions['code'](self, data, code)

