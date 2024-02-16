from cornice.resource import resource

from openprocurement.api.utils import context_unpack, json_view
from openprocurement.relocation.api.procedure.serializers.tender import (
    TransferredTenderSerializer,
)
from openprocurement.relocation.api.procedure.utils import (
    save_transfer,
    update_ownership,
)
from openprocurement.relocation.api.procedure.validation import (
    validate_ownership_data,
    validate_tender,
    validate_tender_owner_accreditation_level,
    validate_tender_transfer_accreditation_level,
    validate_tender_transfer_token,
)
from openprocurement.relocation.api.utils import (
    extract_transfer_doc,
    get_transfer_location,
)
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.utils import ProcurementMethodTypePredicate


@resource(
    name="Tender ownership",
    path="/tenders/{tender_id}/ownership",
    description="Tenders Ownership",
)
class TenderResource(TenderBaseResource):
    serializer_class = TransferredTenderSerializer

    @json_view(
        permission="create_tender",
        validators=(
            validate_tender_transfer_accreditation_level,
            validate_tender_owner_accreditation_level,
            validate_ownership_data,
            validate_tender,
            validate_tender_transfer_token,
        ),
    )
    def post(self):
        tender = self.request.validated["tender"]
        data = self.request.validated["ownership_data"]
        route_name = "{}:Tenders".format(ProcurementMethodTypePredicate.route_prefix(self.request))
        location = get_transfer_location(self.request, route_name, tender_id=tender["_id"])
        transfer = extract_transfer_doc(self.request, transfer_id=data["id"])

        if transfer.get("usedFor") and transfer.get("usedFor") != location:
            self.request.errors.add("body", "transfer", "Transfer already used")
            self.request.errors.status = 403
            return

        update_ownership(tender, transfer)
        self.request.validated["tender"] = tender

        transfer["usedFor"] = location
        self.request.validated["transfer"] = transfer

        if save_transfer(self.request):
            self.LOGGER.info(
                "Updated transfer relation {}".format(transfer["_id"]),
                extra=context_unpack(self.request, {"MESSAGE_ID": "transfer_relation_update"}),
            )

            if save_tender(self.request):
                self.LOGGER.info(
                    "Updated ownership of tender {}".format(tender["_id"]),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_ownership_update"}),
                )

                return {"data": self.serializer_class(tender).data}
