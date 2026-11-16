from cornice.resource import resource

from openprocurement.api.constants import AgreementType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource
from openprocurement.framework.dps.procedure.state.agreement import DPSAgreementState


@resource(
    name=f"{AgreementType.DYNAMIC_PURCHASING_SYSTEM}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{AgreementType.DYNAMIC_PURCHASING_SYSTEM} agreements",
    agreementType=AgreementType.DYNAMIC_PURCHASING_SYSTEM,
    accept="application/json",
)
class DPSAgreementResource(AgreementsResource):
    state_class = DPSAgreementState

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
