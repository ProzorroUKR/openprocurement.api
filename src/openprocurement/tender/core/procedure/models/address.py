from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.api.procedure.models.address import (
    validate_country_name,
    validate_region,
    Address as BaseAddress,
    PostAddress as BasePostAddress,
    PatchAddress as BasePatchAddress,
)


class PatchAddress(BasePatchAddress):
    pass


class PostAddress(BasePostAddress):
    def validate_countryName(self, address, country_name):
        validate_country_name(get_tender(), address, country_name)

    def validate_region(self, address, region):
        validate_region(get_tender(), address, region)


class Address(BaseAddress):
    def validate_countryName(self, address, country_name):
        validate_country_name(get_tender(), address, country_name)

    def validate_region(self, address, region):
        validate_region(get_tender(), address, region)
