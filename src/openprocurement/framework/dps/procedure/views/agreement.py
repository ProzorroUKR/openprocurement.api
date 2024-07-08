from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_input_data_from_resolved_model,
    validate_patch_data,
)
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.validation import (
    validate_agreement_framework,
    validate_agreement_operation_not_in_allowed_status,
)
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.procedure.models.agreement import Agreement


@resource(
    name=f"{DPS_TYPE}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{DPS_TYPE} agreements",
    agreementType=DPS_TYPE,
    accept="application/json",
)
class DPSAgreementResource(AgreementsResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_input_data_from_resolved_model(),
            validate_patch_data(Agreement, item_name="agreement"),
            validate_agreement_framework,
            validate_agreement_operation_not_in_allowed_status,
        ),
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
