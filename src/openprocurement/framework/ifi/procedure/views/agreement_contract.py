from cornice.resource import resource

from openprocurement.api.constants import AgreementType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.contract import (
    AgreementContractsResource,
)


@resource(
    name=f"{AgreementType.INTERNATIONAL_FINANCIAL_INSTITUTIONS}:Agreements Contracts",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    description=f"{AgreementType.INTERNATIONAL_FINANCIAL_INSTITUTIONS} agreements contracts",
    agreementType=AgreementType.INTERNATIONAL_FINANCIAL_INSTITUTIONS,
    accept="application/json",
)
class IFIAgreementContractsResource(AgreementContractsResource):
    @json_view(
        content_type="application/json",
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
