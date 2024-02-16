from openprocurement.api.constants import VALIDATE_ADDRESS_FROM
from openprocurement.api.procedure.models.address import Address as BaseAddress
from openprocurement.api.procedure.models.address import (
    validate_country_name,
    validate_region,
)
from openprocurement.api.procedure.utils import is_obj_const_active
from openprocurement.planning.api.procedure.context import get_plan


class Address(BaseAddress):
    def validate_countryName(self, address, country_name):
        if is_obj_const_active(get_plan(), VALIDATE_ADDRESS_FROM):
            validate_country_name(address, country_name)

    def validate_region(self, address, region):
        if is_obj_const_active(get_plan(), VALIDATE_ADDRESS_FROM):
            validate_region(address, region)
