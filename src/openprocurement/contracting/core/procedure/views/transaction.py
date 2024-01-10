from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.tender.core.procedure.validation import unless_bots, unless_admins
from openprocurement.tender.core.procedure.validation import validate_input_data
from openprocurement.api.procedure.utils import get_items
from openprocurement.contracting.core.procedure.models.transaction import PutTransaction
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.core.procedure.serializers.contract import ContractBaseSerializer
from openprocurement.contracting.core.procedure.validation import validate_contract_owner
from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.contracting.api.procedure.state.contract_transaction import TransactionState


def resolve_transaction(request):
    match_dict = request.matchdict
    if match_dict.get("transaction_id"):
        transaction_id = match_dict["transaction_id"]
        contract = request.validated["contract"]
        transaction = get_items(request, contract.get("implementation", {}),
                                "transactions", transaction_id, request.method != "PUT")
        if transaction:
            request.validated["transaction"] = transaction[0]


class ContractTransactionsResource(ContractBaseResource):

    state_class = TransactionState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_transaction(request)

    @json_view(
        content_type="application/json",
        permission="edit_contract_transactions",
        validators=(
            unless_bots(unless_admins(validate_contract_owner)),
            validate_input_data(PutTransaction),
        )
    )
    def put(self):
        new_transaction = self.request.validated["data"]
        transaction_id = self.request.matchdict["transaction_id"]
        new_transaction.update({"id": transaction_id})

        contract = self.request.validated["contract"]

        self.state.transaction_on_put(new_transaction)

        if not contract.get("implementation"):
            contract["implementation"] = {"transactions": []}

        if "transaction" in self.request.validated:
            self.request.validated["transaction"]["status"] = new_transaction["status"]
            msg = f"Transaction {transaction_id} for {contract['_id']} contract already exists, status updated"
        else:
            contract["implementation"]["transactions"].append(new_transaction)
            msg = f"New transaction {transaction_id} for {contract['_id']} contract has been created"

        if save_contract(self.request):
            self.LOGGER.info(msg)

        return {"data": ContractBaseSerializer(contract).data}

    @json_view(permission="view_contract")
    def get(self):
        return {'data': BaseSerializer(self.request.validated["transaction"]).data}
