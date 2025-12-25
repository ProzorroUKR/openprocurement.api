from copy import deepcopy
from hashlib import sha512
from uuid import uuid4

from cornice.resource import resource

from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.database import atomic_transaction
from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.validation import (
    validate_accreditation_level,
    validate_input_data,
)
from openprocurement.api.utils import (
    context_unpack,
    get_contract_by_id,
    get_tender_by_id,
    json_view,
    request_init_contract,
    request_init_tender,
)
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.serializers.contract import (
    ContractBaseSerializer,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_in_pending_status,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.core.procedure.views.contract import ContractResource
from openprocurement.contracting.econtract.procedure.models.access import PostAccess
from openprocurement.contracting.econtract.procedure.models.contract import PostContract
from openprocurement.contracting.econtract.procedure.state.contract import (
    EContractState,
)
from openprocurement.contracting.econtract.procedure.state.contract_access import (
    ContractAccessState,
)
from openprocurement.tender.core.procedure.utils import save_tender


@resource(
    name="EContract creation",
    path="/contracts",
    description="Contracts creation",
    accept="application/json",
    request_method=("POST",),
)
class EContractPostResource(ContractBaseResource):
    state_class = EContractState
    serializer_class = ContractBaseSerializer

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_input_data(PostContract),
            validate_accreditation_level(
                levels=(AccreditationLevel.ACCR_6,),
                item="contract",
                operation="creation",
                source="data",
            ),
        ),
    )
    def post(self):
        contract = self.request.validated["data"]
        request_init_contract(self.request, contract, contract_src={})
        tender = get_tender_by_id(self.request, contract.get("tender_id"), raise_error=True)
        request_init_tender(self.request, tender)
        prev_contract = None
        for tender_contract_data in tender.get("contracts", []):
            tender_contract = get_contract_by_id(self.request, tender_contract_data["id"], raise_error=True)
            if (
                tender_contract.get("status") == "pending"
                and tender_contract.get("awardID") == contract.get("awardID")
                and tender_contract.get("buyerID") == contract.get("buyerID")
                and tender_contract.get("cancellations")
            ):
                prev_contract = tender_contract
        self.state.validate_on_post(prev_contract, contract)
        self.state.on_post(prev_contract, contract)
        with atomic_transaction():
            if save_contract(self.request, insert=True):
                if self.request.validated.get("contract_was_changed"):
                    if save_tender(self.request):
                        self.LOGGER.info(
                            f"Updated tender {tender['_id']} contract {contract['_id']}",
                            extra=context_unpack(
                                self.request,
                                {"MESSAGE_ID": "tender_contract_update_status"},
                            ),
                        )
                self.LOGGER.info(
                    "Created contract {} ({})".format(contract["_id"], contract["tender_id"]),
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "contract_create"},
                    ),
                )
                self.request.response.status = 201
                new_version_contract = deepcopy(contract)
                # save prev version of contract
                request_init_contract(self.request, prev_contract, contract_src={})
                if save_contract(self.request):
                    self.LOGGER.info(
                        f"Updated contract {prev_contract['_id']}",
                        extra=context_unpack(
                            self.request,
                            {"MESSAGE_ID": "contract_patch"},
                        ),
                    )
                return {
                    "data": self.serializer_class(new_version_contract, tender=tender).data,
                    "config": new_version_contract["config"],
                }


@resource(
    name="EContract",
    path="/contracts/{contract_id}",
    contractType="eContract",
    description="Contracts operations",
    accept="application/json",
)
class EContractResource(ContractResource):
    state_class = EContractState

    # TODO: may be in the future we will use patch only for terminationDetails, amountPaid and `terminated` status
    # @json_view(
    #     content_type="application/json",
    #     permission="edit_contract",
    #     validators=(
    #         unless_admins(unless_administrator(validate_contract_owner)),
    #         unless_admins(unless_administrator(validate_contract_in_active_status)),
    #         validate_input_data(conditional_contract_model),
    #         validate_patch_data_simple(Contract, item_name="contract"),
    #     ),
    # )
    # def patch(self):
    #     return super().patch()


@resource(
    name="EContract access",
    path="/contracts/{contract_id}/access",
    contractType="eContract",
    description="Contract access",
)
class ContractAccessResource(ContractBaseResource):
    state_class = ContractAccessState
    serializer_class = BaseSerializer

    @json_view(
        permission="edit_contract", validators=(validate_input_data(PostAccess), validate_contract_in_pending_status)
    )
    def post(self):
        contract = self.request.validated["contract"]
        data = self.request.validated["data"]
        role = self.state.get_role(data, contract)
        self.state.validate_on_post(contract, role)
        token = uuid4().hex
        self.state.set_token(contract, role, token)

        access = {"token": token}

        if role == AccessRole.BUYER:
            transfer_token = uuid4().hex
            contract["transfer_token"] = sha512(transfer_token.encode("utf-8")).hexdigest()
            access["transfer"] = transfer_token

        if save_contract(self.request):
            self.LOGGER.info(
                f"Generate Contract access {contract['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )
            self.request.response.status = 201
            return {
                "data": self.serializer_class(data).data,
                "access": access,
            }
