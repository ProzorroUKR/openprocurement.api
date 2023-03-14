from openprocurement.api.utils import json_view
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.core.utils import agreementsresource


@agreementsresource(
    name="cfaua:Agreement Contract",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    agreementType="cfaua",
    description="Agreements",
)
class AgreementContractsResource(BaseResource):
    @json_view(permission="view_agreement")
    def collection_get(self):
        agreement = self.context
        return {"data": [contract.serialize("view") for contract in agreement.contracts]}

    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.request.validated["contract"].serialize("view")}
