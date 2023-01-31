from openprocurement.api.utils import json_view
from openprocurement.framework.core.utils import contractresource
from openprocurement.framework.core.views.contract import CoreAgreementContractsResource
from openprocurement.framework.core.validation import (
    validate_patch_contract_data,
    validate_agreement_operation_not_in_allowed_status,
)
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE


@contractresource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Agreements Contracts",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    agreementType=ELECTRONIC_CATALOGUE_TYPE,
    description="Agreements Contracts",
)
class AgreementContractsResource(CoreAgreementContractsResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_contract_data,
            validate_agreement_operation_not_in_allowed_status,
        ),
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
