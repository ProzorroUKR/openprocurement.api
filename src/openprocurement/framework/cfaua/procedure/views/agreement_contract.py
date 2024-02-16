from cornice.resource import resource

from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.utils import get_items
from openprocurement.api.utils import json_view
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.views.base import AgreementBaseResource
from openprocurement.framework.core.procedure.serializers.contract import (
    ContractSerializer,
)


def resolve_contract(request):
    match_dict = request.matchdict
    if match_dict.get("contract_id"):
        contracts = get_items(request, request.validated["agreement"], "contracts", match_dict["contract_id"])
        request.validated["contract"] = contracts[0]


@resource(
    name=f"{CFA_UA}:Agreement Contract",
    collection_path="/agreements/{agreement_id}/contracts",
    path="/agreements/{agreement_id}/contracts/{contract_id}",
    agreementType=CFA_UA,
    description="Agreements",
)
class AgreementContractsResource(AgreementBaseResource):
    serializer_class = ContractSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_contract(request)

    @json_view(permission="view_agreement")
    def collection_get(self):
        agreement = self.request.validated["agreement"]
        data = tuple(self.serializer_class(contract).data for contract in agreement.get("contracts", []))
        return {"data": data}

    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.serializer_class(get_object("contract")).data}
