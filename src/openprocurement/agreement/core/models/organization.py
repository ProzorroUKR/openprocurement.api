from openprocurement.api.models import BusinessOrganization as BaseBusinessOrganization


class BusinessOrganization(BaseBusinessOrganization):
    def validate_scale(self, data, value):
        pass
