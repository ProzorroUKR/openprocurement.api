from openprocurement.tender.core.procedure.models.address import Address as BaseAddress

class Address(BaseAddress):
    def validate_countryName(self, data, value):
        pass

    def validate_region(self, data, value):
        pass
