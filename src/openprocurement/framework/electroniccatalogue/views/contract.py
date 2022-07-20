from openprocurement.api.utils import json_view, context_unpack
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.core.utils import apply_patch
from openprocurement.framework.core.validation import validate_patch_contract_data
from openprocurement.framework.electroniccatalogue.utils import contractresource
from openprocurement.framework.electroniccatalogue.validation import validate_agreement_operation_not_in_allowed_status


@contractresource(
    name="electronicCatalogue:Agreements:Contracts",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    agreementType="electronicCatalogue",
    description="Agreement contracts resource",
)
class AgreementContractsResource(BaseResource):
    @json_view(permission="view_agreement")
    def collection_get(self):
        agreement = self.context
        return {"data": [contract.serialize("view") for contract in agreement.contracts]}

    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.request.validated["contract"].serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
                validate_patch_contract_data,
                validate_agreement_operation_not_in_allowed_status,
        ),
        permission="edit_agreement",
    )
    def patch(self):
        contract = self.request.validated["contract"]

        if apply_patch(self.request, "agreement", src=contract.to_primitive()):
            self.LOGGER.info(
                f"Updated contract {contract.id}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )

        return {"data": contract.serialize("view")}
