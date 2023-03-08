from openprocurement.api.utils import (
    json_view,
    context_unpack,
)
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.core.utils import apply_patch
from openprocurement.framework.core.validation import validate_restricted_access


class CoreAgreementContractsResource(BaseResource):
    @json_view(
        validators=(
            validate_restricted_access("agreement")
        ),
        permission="view_agreement",
    )
    def collection_get(self):
        agreement = self.context
        return {"data": [contract.serialize("view") for contract in agreement.contracts]}

    @json_view(
        validators=(
            validate_restricted_access("agreement")
        ),
        permission="view_agreement",
    )
    def get(self):
        return {"data": self.request.validated["contract"].serialize("view")}

    def patch(self):
        contract = self.request.validated["contract"]

        if apply_patch(self.request, "agreement", src=contract.to_primitive()):
            self.LOGGER.info(
                f"Updated contract {contract.id}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )

        return {"data": contract.serialize("view")}
