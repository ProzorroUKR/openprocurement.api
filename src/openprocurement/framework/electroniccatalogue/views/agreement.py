from openprocurement.api.utils import json_view
from openprocurement.framework.core.utils import agreementsresource
from openprocurement.framework.core.views.agreement import CoreAgreementResource
from openprocurement.framework.core.validation import (
    validate_patch_agreement_data,
    validate_agreement_operation_not_in_allowed_status,
)


@agreementsresource(
    name="electronicCatalogue:Agreements",
    path="/agreements/{agreement_id}",
    agreementType="electronicCatalogue",
    description="Agreements resource"
)
class AgreementResource(CoreAgreementResource):

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_agreement_data,
            validate_agreement_operation_not_in_allowed_status,
        ),
        permission="edit_agreement"
    )
    def patch(self):
        return super().patch()
