from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource
from openprocurement.framework.ifi.constants import IFI_TYPE
from openprocurement.framework.ifi.procedure.state.agreement import IFIAgreementState


@resource(
    name=f"{IFI_TYPE}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{IFI_TYPE} agreements",
    agreementType=IFI_TYPE,
    accept="application/json",
)
class IFIAgreementResource(AgreementsResource):
    state_class = IFIAgreementState

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
