from cornice.resource import resource

from openprocurement.api.database import atomic_transaction
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.relocation.api.procedure.serializers.agreement import (
    TransferredAgreementSerializer,
)
from openprocurement.relocation.api.procedure.state.ownership import AgreementOwnershipState
from openprocurement.relocation.api.procedure.utils import (
    save_transfer,
    update_ownership,
)
from openprocurement.relocation.api.utils import (
    extract_transfer_doc,
    get_transfer_location,
)


@resource(
    name="Agreement ownership",
    path="/agreements/{agreement_id}/ownership",
    description="Agreements Ownership",
)
class AgreementResource(FrameworkBaseResource):
    serializer_class = TransferredAgreementSerializer
    state_class = AgreementOwnershipState

    @json_view(
        permission="edit_agreement",
    )
    def post(self):
        self.state.validate_ownership_post_request()
        agreement = self.request.validated["agreement"]
        data = self.request.validated["ownership_data"]
        route_name = "{}:Agreements".format(agreement["agreementType"])
        location = get_transfer_location(self.request, route_name, agreement_id=agreement["_id"])
        transfer = extract_transfer_doc(self.request, transfer_id=data["id"])

        if transfer.get("usedFor") and transfer.get("usedFor") != location:
            self.request.errors.add("body", "transfer", "Transfer already used")
            self.request.errors.status = 403
            return

        update_ownership(agreement, transfer)
        self.request.validated["agreement"] = agreement

        transfer["usedFor"] = location
        self.request.validated["transfer"] = transfer

        with atomic_transaction():
            if save_transfer(self.request):
                self.LOGGER.info(
                    "Updated transfer relation {}".format(transfer["_id"]),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "transfer_relation_update"}),
                )

                if save_object(self.request, "agreement"):
                    self.LOGGER.info(
                        "Updated ownership of agreement {}".format(agreement["_id"]),
                        extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_ownership_update"}),
                    )

                    return {"data": self.serializer_class(agreement).data}
