# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.api.views.base import BaseResource
from openprocurement.contracting.api.utils import contractingresource, save_contract
from openprocurement.relocation.api.utils import (
    extract_transfer,
    update_ownership,
    save_transfer,
    get_transfer_location,
)
from openprocurement.relocation.api.validation import (
    validate_ownership_data,
    validate_contract_accreditation_level,
    validate_contract_owner_accreditation_level,
    validate_contract,
    validate_contract_transfer_token,
)


@contractingresource(
    name="Contract ownership", path="/contracts/{contract_id}/ownership", description="Contracts Ownership"
)
class ContractResource(BaseResource):
    @json_view(
        permission="view_contract",
        validators=(
            validate_contract_accreditation_level,
            validate_contract_owner_accreditation_level,
            validate_ownership_data,
            validate_contract,
            validate_contract_transfer_token,
        ),
    )
    def post(self):
        contract = self.request.validated["contract"]
        data = self.request.validated["ownership_data"]

        location = get_transfer_location(self.request, "Contract", contract_id=contract.id)
        transfer = extract_transfer(self.request, transfer_id=data["id"])

        if transfer.get("usedFor") and transfer.get("usedFor") != location:
            self.request.errors.add("body", "transfer", "Transfer already used")
            self.request.errors.status = 403
            return

        update_ownership(contract, transfer)
        self.request.validated["contract"] = contract

        transfer.usedFor = location
        self.request.validated["transfer"] = transfer

        if save_transfer(self.request):
            self.LOGGER.info(
                "Updated transfer relation {}".format(transfer.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "transfer_relation_update"}),
            )

            if save_contract(self.request):
                self.LOGGER.info(
                    "Updated ownership of contract {}".format(contract.id),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "contract_ownership_update"}),
                )

                return {"data": contract.serialize("view")}
