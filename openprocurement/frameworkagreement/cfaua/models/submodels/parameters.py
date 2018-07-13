from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import Parameter as BaseParameter, bids_validation_wrapper


class Parameter(BaseParameter):
    class Options:
        roles = RolesFromCsv('Parameter.csv', relative_to=__file__)

    @bids_validation_wrapper
    def validate_value(self, data, value):
        BaseParameter._validator_functions['value'](self, data, value)

    @bids_validation_wrapper
    def validate_code(self, data, code):
        BaseParameter._validator_functions['code'](self, data, code)
