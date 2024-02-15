# -*- coding: utf-8 -*-
from cornice.resource import resource

from openprocurement.api.utils import json_view, context_unpack
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.relocation.api.procedure.serializers.agreement import TransferredAgreementSerializer
from openprocurement.tender.core.utils import ProcurementMethodTypePredicate
from openprocurement.relocation.api.procedure.serializers.tender import TransferredTenderSerializer
from openprocurement.relocation.api.procedure.utils import update_ownership, save_transfer
from openprocurement.relocation.api.procedure.validation import (
    validate_ownership_data,
    validate_tender_owner_accreditation_level,
    validate_tender_transfer_accreditation_level,
    validate_tender,
    validate_tender_transfer_token,
    validate_agreement_transfer_accreditation_level,
    validate_agreement_owner_accreditation_level,
    validate_agreement,
    validate_agreement_transfer_token,
)
from openprocurement.relocation.api.utils import (
    get_transfer_location,
    extract_transfer_doc,
)
from openprocurement.tender.core.procedure.utils import save_tender


@resource(
    name="Agreement ownership",
    path="/agreements/{agreement_id}/ownership",
    description="Agreements Ownership",
)
class AgreementResource(FrameworkBaseResource):
    serializer_class = TransferredAgreementSerializer

    @json_view(
        permission="edit_agreement",
        validators=(
            validate_agreement_transfer_accreditation_level,
            validate_agreement_owner_accreditation_level,
            validate_ownership_data,
            validate_agreement,
            validate_agreement_transfer_token,
        ),
    )
    def post(self):
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
