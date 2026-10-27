from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.core.procedure.views.contract import (
    AgreementContractsResource,
)


@resource(
    name=f"{ARMA_TYPE}:Agreements Contracts",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    description=f"{ARMA_TYPE} agreements contracts",
    agreementType=ARMA_TYPE,
    accept="application/json",
)
class ARMAAgreementContractsResource(AgreementContractsResource):
    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
