from cornice.resource import resource

from openprocurement.api.constants import AgreementType
from openprocurement.api.utils import json_view
from openprocurement.framework.arma.procedure.state.agreement import ARMAAgreementState
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource


@resource(
    name=f"{AgreementType.ASSET_RECOVERY_MANAGEMENT_AGENCY}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{AgreementType.ASSET_RECOVERY_MANAGEMENT_AGENCY} agreements",
    agreementType=AgreementType.ASSET_RECOVERY_MANAGEMENT_AGENCY,
    accept="application/json",
)
class ARMAAgreementResource(AgreementsResource):
    state_class = ARMAAgreementState

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
