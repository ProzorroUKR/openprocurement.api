from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.contract import (
    AgreementContractsResource,
)
from openprocurement.framework.ifi.constants import IFI_TYPE


@resource(
    name=f"{IFI_TYPE}:Agreements Contracts",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    description=f"{IFI_TYPE} agreements contracts",
    agreementType=IFI_TYPE,
    accept="application/json",
)
class IFIAgreementContractsResource(AgreementContractsResource):
    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
