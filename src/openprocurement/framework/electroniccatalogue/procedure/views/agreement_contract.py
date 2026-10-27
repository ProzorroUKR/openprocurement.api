from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.contract import (
    AgreementContractsResource,
)
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Agreements Contracts",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    description=f"{ELECTRONIC_CATALOGUE_TYPE} agreements contracts",
    agreementType=ELECTRONIC_CATALOGUE_TYPE,
    accept="application/json",
)
class ElectronicCatalogueAgreementContractsResource(AgreementContractsResource):
    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
