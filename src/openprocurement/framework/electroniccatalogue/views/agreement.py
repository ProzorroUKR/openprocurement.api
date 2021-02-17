from openprocurement.api.utils import APIResource, json_view
from openprocurement.framework.core.utils import agreementsresource


@agreementsresource(
    name="electronicCatalogue:Agreements",
    path="/agreements/{agreement_id}",
    agreementType="electronicCatalogue",
    description="Agreements resource"
)
class AgreementResource(APIResource):
    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.context.serialize("view")}
