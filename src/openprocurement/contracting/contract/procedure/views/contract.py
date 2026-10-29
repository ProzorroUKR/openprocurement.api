from cornice.resource import resource

from openprocurement.api.database import atomic_transaction
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.serializers.contract import (
    ContractBaseSerializer,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.core.procedure.views.contract import (
    ContractResource as BaseContractResource,
)
from openprocurement.tender.core.procedure.utils import save_tender, set_ownership


@resource(
    name="Contract",
    path="/contracts/{contract_id}",
    contractType="contract",
    description="Contracts operations",
    accept="application/json",
)
class ContractResource(BaseContractResource):
    @json_view(
        content_type="application/json",
        permission="edit_contract",
    )
    def patch(self):
        """Contract Edit (partial)"""
        self.state.validate_contract_patch_request()
        updated = self.request.validated["data"]
        contract_src = self.request.validated["contract_src"]
        if updated:
            contract = self.request.validated["contract"] = updated
            self.state.on_patch(contract_src, contract)
            contract_was_changed = self.request.validated.get("contract_was_changed")
            # keep only db writes inside the transaction: the time between save_data and commit
            # must be minimal, see docs/source/developers/projects/cdb/feed_ordering.rst
            with atomic_transaction(enabled=bool(contract_was_changed)):
                tender_saved = False
                contract_saved = save_contract(self.request)
                if contract_saved and contract_was_changed:
                    tender_saved = save_tender(self.request)

            if tender_saved:
                self.LOGGER.info(
                    f"Updated tender {self.request.validated['tender']['_id']} contract {contract['_id']}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "tender_contract_update_status"},
                    ),
                )
            if contract_saved:
                self.LOGGER.info(
                    f"Updated contract {contract['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
                )
                return {
                    "data": self.serializer_class(contract, tender=self.request.validated.get("tender")).data,
                    "config": contract["config"],
                }


@resource(
    name="Contract credentials",
    path="/contracts/{contract_id}/credentials",
    contractType="contract",
    description="Contract credentials",
)
class ContractCredentialsResource(ContractBaseResource):
    serializer_class = ContractBaseSerializer

    @json_view(
        permission="edit_contract",
    )
    def patch(self):
        self.state.validate_credentials_patch_request()
        contract = self.request.validated["contract"]
        access = set_ownership(contract, self.request, access_role=AccessRole.CONTRACT)
        if save_contract(self.request):
            self.LOGGER.info(
                f"Generate Contract credentials {contract['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )
            return {
                "data": self.serializer_class(contract, tender=self.request.validated.get("tender")).data,
                "config": contract["config"],
                "access": access,
            }
