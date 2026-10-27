from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.agreement import AgreementsResource
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.framework.electroniccatalogue.procedure.state.agreement import ElectronicDialogueAgreementState


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Agreements",
    collection_path="/agreements",
    path="/agreements/{agreement_id}",
    description=f"{ELECTRONIC_CATALOGUE_TYPE} agreements",
    agreementType=ELECTRONIC_CATALOGUE_TYPE,
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
