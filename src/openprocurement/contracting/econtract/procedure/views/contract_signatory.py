from cornice.resource import resource

from openprocurement.api.database import atomic_transaction
from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_in_pending_status,
    validate_contract_participant,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.econtract.procedure.models.signatory import (
    PostSignatory,
)
from openprocurement.contracting.econtract.procedure.state.contract_signatory import (
    SignatoryState,
)
from openprocurement.tender.core.procedure.utils import save_tender


@resource(
    name="EContract signatories",
    path="/contracts/{contract_id}/signatories",
    contractType="eContract",
    description="EContracts Signatories",
)
class EContractsSignatoriesResource(ContractBaseResource):
    serializer_class = BaseSerializer
    state_class = SignatoryState

    def save(self, **kwargs):
        contract = self.request.validated["contract"]
        if self.request.validated.get("contract_was_changed"):
            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated tender {self.request.validated['tender']['_id']} contract {contract['_id']}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "tender_contract_update_status"},
                    ),
                )
        return save_contract(self.request, **kwargs)

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_administrator(unless_admins(validate_contract_participant)),
            validate_contract_in_pending_status,
            validate_input_data(PostSignatory),
        ),
    )
    def post(self):
        contract = self.request.validated["contract"]

        signatory = self.request.validated["data"]

        if not contract.get("signatories"):
            contract["signatories"] = []

        self.state.signatory_on_post(signatory)

        contract["signatories"].append(signatory)

        with atomic_transaction():
            if save_contract(self.request):
                if self.request.validated.get("contract_was_changed"):
                    if save_tender(self.request):
                        self.LOGGER.info(
                            f"Updated tender {self.request.validated['tender']['_id']} contract {contract['_id']}",
                            extra=context_unpack(
                                self.request,
                                {"MESSAGE_ID": "tender_contract_update_status"},
                            ),
                        )

                self.LOGGER.info(
                    f"Created signatory for contract {contract['_id']}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "contract_signatory_create"},
                        {"contract_id": contract["_id"]},
                    ),
                )
                self.request.response.status = 201
                if "tender" in self.request.validated:
                    self.state.always(self.request.validated["tender"])
                return {"data": self.serializer_class(signatory).data}
