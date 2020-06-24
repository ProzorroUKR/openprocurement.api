# -*- coding: utf-8 -*-
from openprocurement.api.utils import context_unpack, json_view, APIResource, APIResourceListing

from openprocurement.contracting.api.utils import (
    contractingresource,
    apply_patch,
    contract_serialize,
    set_ownership,
    save_contract,
    get_transaction_by_id,
)
from openprocurement.contracting.api.validation import (
    validate_contract_data,
    validate_patch_contract_data,
    validate_credentials_generate,
    validate_contract_update_not_in_allowed_status,
    validate_terminate_contract_without_amountPaid,
    validate_update_contracting_value_readonly,
    validate_update_contracting_value_identical,
    validate_update_contracting_paid_amount,
    validate_update_contracting_value_amount,
    validate_update_contract_paid_net_required,
    validate_put_transaction_to_contract,
    validate_transaction_existence,
)
from openprocurement.contracting.api.design import (
    FIELDS,
    contracts_by_dateModified_view,
    contracts_real_by_dateModified_view,
    contracts_test_by_dateModified_view,
    contracts_by_local_seq_view,
    contracts_real_by_local_seq_view,
    contracts_test_by_local_seq_view,
)
from openprocurement.tender.core.validation import validate_update_contract_value_net_required

VIEW_MAP = {
    u"": contracts_real_by_dateModified_view,
    u"test": contracts_test_by_dateModified_view,
    u"_all_": contracts_by_dateModified_view,
}

CHANGES_VIEW_MAP = {
    u"": contracts_real_by_local_seq_view,
    u"test": contracts_test_by_local_seq_view,
    u"_all_": contracts_by_local_seq_view,
}

FEED = {u"dateModified": VIEW_MAP, u"changes": CHANGES_VIEW_MAP}


@contractingresource(name="Contracts", path="/contracts", description="Contracts")
class ContractsResource(APIResourceListing):
    def __init__(self, request, context):
        super(ContractsResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = contract_serialize
        self.object_name_for_listing = "Contracts"
        self.log_message_id = "contract_list_custom"

    @json_view(content_type="application/json", permission="create_contract", validators=(validate_contract_data,))
    def post(self):
        contract = self.request.validated["contract"]
        for i in self.request.validated["json_data"].get("documents", []):
            doc = type(contract).documents.model_class(i)
            doc.__parent__ = contract
            contract.documents.append(doc)

        self.request.validated["contract"] = contract
        self.request.validated["contract_src"] = {}
        if save_contract(self.request):
            self.LOGGER.info(
                "Created contract {} ({})".format(contract.id, contract.contractID),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "contract_create"},
                    {"contract_id": contract.id, "contractID": contract.contractID or ""},
                ),
            )
            self.request.response.status = 201
            return {"data": contract.serialize("view"), "access": {"token": contract.owner_token}}


@contractingresource(name="Contract", path="/contracts/{contract_id}", description="Contract")
class ContractResource(ContractsResource):
    @json_view(permission="view_contract")
    def get(self):
        return {"data": self.request.validated["contract"].serialize("view")}

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_patch_contract_data,
            validate_update_contract_value_net_required,
            validate_update_contract_paid_net_required,
            validate_update_contracting_value_readonly,
            validate_update_contracting_value_identical,
            validate_update_contracting_value_amount,
            validate_update_contracting_paid_amount,
            validate_contract_update_not_in_allowed_status,
        ),
    )
    def patch(self):
        """Contract Edit (partial)
        """
        contract = self.request.validated["contract"]
        apply_patch(self.request, save=False, src=self.request.validated["contract_src"])

        validate_terminate_contract_without_amountPaid(self.request)

        if save_contract(self.request):
            self.LOGGER.info(
                "Updated contract {}".format(contract.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )
            return {"data": contract.serialize("view")}


@contractingresource(
    name="Contract credentials", path="/contracts/{contract_id}/credentials", description="Contract credentials"
)
class ContractCredentialsResource(APIResource):
    def __init__(self, request, context):
        super(ContractCredentialsResource, self).__init__(request, context)
        self.server = request.registry.couchdb_server

    @json_view(permission="generate_credentials", validators=(validate_credentials_generate,))
    def patch(self):
        contract = self.request.validated["contract"]

        access = set_ownership(contract, self.request)
        if save_contract(self.request):
            self.LOGGER.info(
                "Generate Contract credentials {}".format(contract.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )
            return {"data": contract.serialize("view"), "access": access}


@contractingresource(
    name="Contract transactions",
    path="/contracts/{contract_id}/transactions/{transaction_id}",
    description="Contract transactions",
)
class ContractTransactionsResource(APIResource):
    def __init__(self, request, context):
        super(ContractTransactionsResource, self).__init__(request, context)
        self.server = request.registry.couchdb_server

    @json_view(
        content_type="application/json",
        permission="edit_contract_transactions",
        validators=(validate_put_transaction_to_contract,)
    )
    def put(self):
        new_transaction = self.request.json["data"]
        transaction_id = self.request.matchdict["transaction_id"]
        new_transaction.update({"id": transaction_id})

        contract = self.request.validated["contract"]
        transactions = contract.implementation.transactions

        status_mapping = {
            0: "successful",
            -1: "canceled",
        }
        _status_value = new_transaction['status']
        new_transaction['status'] = status_mapping.get(_status_value, _status_value)

        existing_transaction = next((trans for trans in transactions if trans["id"] == transaction_id), None)

        if existing_transaction:
            existing_transaction["status"] = new_transaction["status"]

            if save_contract(self.request):
                self.LOGGER.info(
                    "Transaction {} for {} contract already exists, status updated".format(transaction_id, contract.id)
                )
        else:

            trans = type(contract.implementation).transactions.model_class(new_transaction)
            trans.__parent__ = contract.implementation
            transactions.append(trans)

            if save_contract(self.request):
                self.LOGGER.info(
                    "New transaction {} for {} contract has been created".format(transaction_id, contract.id)
                )

        return {"data": contract.serialize("view")}

    @json_view(
        permission="view_contract",
        validators=(validate_transaction_existence,)
    )
    def get(self):
        _transaction = get_transaction_by_id(self.request)
        return {'data': _transaction.serialize("view")}
