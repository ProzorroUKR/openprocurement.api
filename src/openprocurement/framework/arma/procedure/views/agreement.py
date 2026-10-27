from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.arma.procedure.state.agreement import ARMAAgreementState
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource


@resource(
    name=f"{ARMA_TYPE}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{ARMA_TYPE} agreements",
    agreementType=ARMA_TYPE,
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
