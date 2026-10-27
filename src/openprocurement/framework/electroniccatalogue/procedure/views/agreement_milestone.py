from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.milestone import (
    AgreementContractMilestonesResource,
)
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Agreements Contracts Milestones",
    collection_path="/agreements/{agreement_id}/contracts/{contract_id}/milestones",
    path="/agreements/{agreement_id}/contracts/{contract_id}/milestones/{milestone_id}",
    description="Agreements Contracts Milestones",
    agreementType=ELECTRONIC_CATALOGUE_TYPE,
    accept="application/json",
)
class ElectronicCatalogueAgreementContractMilestoneResource(AgreementContractMilestonesResource):
    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
