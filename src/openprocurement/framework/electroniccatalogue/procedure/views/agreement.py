from cornice.resource import resource

from openprocurement.api.constants import AgreementType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource
from openprocurement.framework.electroniccatalogue.procedure.state.agreement import ElectronicDialogueAgreementState


@resource(
    name=f"{AgreementType.ELECTRONIC_CATALOGUE}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{AgreementType.ELECTRONIC_CATALOGUE} agreements",
    agreementType=AgreementType.ELECTRONIC_CATALOGUE,
    accept="application/json",
)
class ElectronicCatalogueAgreementResource(AgreementsResource):
    state_class = ElectronicDialogueAgreementState

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
