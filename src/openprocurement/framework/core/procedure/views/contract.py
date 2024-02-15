from logging import getLogger

from openprocurement.api.utils import (
    json_view,
    context_unpack,
)
from openprocurement.framework.core.procedure.serializers.contract import ContractSerializer
from openprocurement.api.procedure.context import get_object
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.api.procedure.utils import get_items, set_item

LOGGER = getLogger(__name__)


def resolve_contract(request):
    match_dict = request.matchdict
    if match_dict.get("contract_id"):
        contracts = get_items(request, request.validated["agreement"], "contracts", match_dict["contract_id"])
        request.validated["contract"] = contracts[0]


class AgreementContractsResource(FrameworkBaseResource):
    serializer_class = ContractSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_contract(request)

    @json_view(
        permission="view_framework",
    )
    def collection_get(self):
        agreement = self.request.validated["agreement"]
        data = tuple(self.serializer_class(contract).data for contract in agreement.get("contracts", []))
        return {"data": data}

    @json_view(
        permission="view_framework",
    )
    def get(self):
        return {"data": self.serializer_class(get_object("contract")).data}

    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            contract = self.request.validated["contract"]
            set_item(self.request.validated["agreement"], "contracts", contract["id"], updated)
            if save_object(self.request, "agreement"):
                self.LOGGER.info(
                    f"Updated agreement contract {self.request.validated['contract']['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": f"agreement_contract_patch"}),
                )
                return {"data": self.serializer_class(updated).data}
