from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.api.context import get_request
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import json_view, context_unpack, raise_operation_error
from openprocurement.tender.core.procedure.utils import (
    save_tender,
    set_item,
)
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer
from openprocurement.tender.core.procedure.state.contract import ContractState
from openprocurement.tender.core.procedure.views.contract import resolve_contract
from openprocurement.tender.core.procedure.models.contract_items_unit_value import Value
from openprocurement.tender.core.procedure.validation import validate_input_data, validate_item_owner
from pyramid.security import Allow, Everyone
from copy import deepcopy
from logging import getLogger

LOGGER = getLogger(__name__)


def resolve_contract_item(request):
    match_dict = request.matchdict
    item_id = match_dict.get("item_id")
    if item_id:
        items = get_items(request, request.validated["contract"], "items", item_id)
        request.validated["item"] = items[0]


def get_item_unit_value(item):
    unit = item.get("unit")
    if unit is None:
        raise_operation_error(
            get_request(),
            "Not Found",
            status=404,
            location="url",
            name="unit"
        )

    if "value" not in unit:
        unit["value"] = {}
    return unit["value"]


class ContractItemsUnitValueResource(TenderBaseResource):

    serializer_class = BaseSerializer
    state_class = ContractState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "edit_contract"),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_contract(request)
            resolve_contract_item(request)

    @json_view(permission="view_tender")
    def get(self):
        data = self.serializer_class(
            get_item_unit_value(
                self.request.validated["item"]
            )
        ).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_item_owner(item_name="tender"),
            validate_input_data(Value),
        ),
    )
    def patch(self):
        data = self.request.validated["data"]
        if data:
            contract = self.request.validated["contract"]
            # update items.unit.value magic # TODO: in a better way
            updated_contract = deepcopy(contract)
            items = get_items(self.request, updated_contract, "items", self.request.validated["item"]["id"])
            updated_value = get_item_unit_value(items[0])
            updated_value.update(data)
            # process updated contract
            self.state.validate_contract_patch(self.request, contract, updated_contract)
            set_item(self.request.validated["tender"], "contracts", contract["id"], updated_contract)
            self.state.contract_on_patch(contract, updated_contract)
            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated tender contract {contract['id']} item unit value",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_item_unit_value_patch"}),
                )
                return {"data": self.serializer_class(updated_value).data}
