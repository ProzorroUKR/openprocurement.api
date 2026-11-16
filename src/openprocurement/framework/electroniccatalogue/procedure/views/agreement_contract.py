from cornice.resource import resource

from openprocurement.api.constants import AgreementType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.contract import (
    AgreementContractsResource,
)


@resource(
    name=f"{AgreementType.ELECTRONIC_CATALOGUE}:Agreements Contracts",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    description=f"{AgreementType.ELECTRONIC_CATALOGUE} agreements contracts",
    agreementType=AgreementType.ELECTRONIC_CATALOGUE,
    accept="application/json",
)
class ElectronicCatalogueAgreementContractsResource(AgreementContractsResource):
    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
