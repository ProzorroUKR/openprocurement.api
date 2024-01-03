from openprocurement.planning.api.procedure.context import get_plan
from openprocurement.api.procedure.models.address import (
    Address as BaseAddress,
    validate_country_name,
    validate_region,
)


class Address(BaseAddress):
    def validate_countryName(self, address, country_name):
        validate_country_name(get_plan(), address, country_name)

    def validate_region(self, address, region):
        validate_region(get_plan(), address, region)
