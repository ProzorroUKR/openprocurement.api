# -*- coding: utf-8 -*-
from cornice.resource import resource

from openprocurement.api.utils import json_view, context_unpack
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.relocation.api.procedure.serializers.contract import TransferredContractSerializer
from openprocurement.relocation.api.procedure.utils import update_ownership, save_transfer
from openprocurement.relocation.api.utils import (
    extract_transfer_doc,
    get_transfer_location,
)
from openprocurement.relocation.api.procedure.validation import (
    validate_ownership_data,
    validate_contract_owner_accreditation_level,
    validate_contract_transfer_accreditation_level,
    validate_contract,
    validate_contract_transfer_token,
)


@resource(
    name="Contract ownership",
    path="/contracts/{contract_id}/ownership",
    description="Contracts Ownership",
)
class ContractResource(ContractBaseResource):
    serializer_class = TransferredContractSerializer

    @json_view(
        permission="edit_contract",
        validators=(
            validate_contract_transfer_accreditation_level,
            validate_contract_owner_accreditation_level,
            validate_ownership_data,
            validate_contract,
            validate_contract_transfer_token,
        ),
    )
    def post(self):
        contract = self.request.validated["contract"]
        data = self.request.validated["ownership_data"]

        location = get_transfer_location(self.request, "Contract", contract_id=contract["_id"])
        transfer = extract_transfer_doc(self.request, transfer_id=data["id"])

        if transfer.get("usedFor") and transfer.get("usedFor") != location:
            self.request.errors.add("body", "transfer", "Transfer already used")
            self.request.errors.status = 403
            return

        update_ownership(contract, transfer)
        self.request.validated["contract"] = contract

        transfer["usedFor"] = location
        self.request.validated["transfer"] = transfer

        if save_transfer(self.request):
            self.LOGGER.info(
                "Updated transfer relation {}".format(transfer["_id"]),
                extra=context_unpack(self.request, {"MESSAGE_ID": "transfer_relation_update"}),
            )

            if save_contract(self.request):
                self.LOGGER.info(
                    "Updated ownership of contract {}".format(contract["_id"]),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "contract_ownership_update"}),
                )

                return {"data": self.serializer_class(contract).data}
