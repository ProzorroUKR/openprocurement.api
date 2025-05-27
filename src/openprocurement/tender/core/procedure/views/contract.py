from logging import getLogger

from pyramid.security import Allow, Everyone

from openprocurement.api.procedure.utils import get_items
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.serializers.contract import (
    ContractSerializer,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource

LOGGER = getLogger(__name__)


def resolve_contract(request):
    match_dict = request.matchdict
    if match_dict.get("contract_id"):
        contract_id = match_dict["contract_id"]
        contract = get_items(request, request.validated["tender"], "contracts", contract_id)[0]
        request.validated["contract"] = contract

        tender = request.validated["tender"]
        awards = [a for a in tender["awards"] if a["id"] == contract["awardID"]]
        request.validated["award"] = awards[0]


class TenderContractResource(TenderBaseResource):
    serializer_class = ContractSerializer

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_contract(request)

    @json_view(permission="view_tender")
    def collection_get(self):
        tender = self.request.validated["tender"]
        data = tuple(self.serializer_class(contract).data for contract in tender.get("contracts", []))
        return {"data": data}

    @json_view(permission="view_tender")
    def get(self):
        data = self.serializer_class(self.request.validated["contract"]).data
        return {"data": data}
