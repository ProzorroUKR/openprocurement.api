from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import json_view, context_unpack, update_logging_context
from openprocurement.tender.core.procedure.utils import (
    save_tender,
    set_item,
)
from openprocurement.tender.core.procedure.serializers.contract import ContractSerializer
from openprocurement.tender.core.procedure.state.contract import ContractState
from pyramid.security import Allow, Everyone
from logging import getLogger

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
    state_class = ContractState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "edit_contract"),

            (Allow, "g:Administrator", "edit_contract"),
            (Allow, "g:admins", "create_contract"),
            (Allow, "g:admins", "edit_contract"),

            (Allow, "g:contracting", "create_contract"),
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

    def collection_post(self):
        update_logging_context(self.request, {"contract_id": "__new__"})

        tender = self.request.validated["tender"]
        contract = self.request.validated["data"]

        self.state.validate_contract_post(self.request, tender, contract)

        if "contracts" not in tender:
            tender["contracts"] = []
        tender["contracts"].append(contract)

        self.state.contract_on_post(contract)

        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender contract {}".format(contract["id"]),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_contract_create"}, {"contract_id": contract["id"]}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Contracts".format(tender["procurementMethodType"]),
                tender_id=tender["_id"],
                contract_id=contract["id"],
            )
            return {"data": self.serializer_class(contract).data}

    def patch(self):
        updated_contract = self.request.validated["data"]
        if updated_contract:
            contract = self.request.validated["contract"]

            self.state.validate_contract_patch(self.request, contract, updated_contract)

            set_item(self.request.validated["tender"], "contracts", contract["id"], updated_contract)
            self.state.contract_on_patch(contract, updated_contract)

            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated tender contract {contract['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_patch"}),
                )
                return {"data": self.serializer_class(updated_contract).data}
