from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.procedure.state.agreement import DPSAgreementState


@resource(
    name=f"{DPS_TYPE}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{DPS_TYPE} agreements",
    agreementType=DPS_TYPE,
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
