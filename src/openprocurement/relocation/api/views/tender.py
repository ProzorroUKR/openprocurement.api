# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.api.views.base import BaseResource
from openprocurement.tender.core.utils import save_tender, optendersresource
from openprocurement.relocation.api.utils import (
    extract_transfer,
    update_ownership,
    save_transfer,
    get_transfer_location,
)
from openprocurement.relocation.api.validation import (
    validate_ownership_data,
    validate_tender_accreditation_level,
    validate_tender_owner_accreditation_level,
    validate_tender,
    validate_tender_transfer_token,
)


@optendersresource(name="Tender ownership", path="/tenders/{tender_id}/ownership", description="Tenders Ownership")
class TenderResource(BaseResource):
    @json_view(
        permission="create_tender",
        validators=(
            validate_tender_accreditation_level,
            validate_tender_owner_accreditation_level,
            validate_ownership_data,
            validate_tender,
            validate_tender_transfer_token,
        ),
    )
    def post(self):
        tender = self.request.validated["tender"]
        data = self.request.validated["ownership_data"]

        route_name = "{}:Tenders".format(tender.procurementMethodType)
        location = get_transfer_location(self.request, route_name, tender_id=tender.id)
        transfer = extract_transfer(self.request, transfer_id=data["id"])

        if transfer.get("usedFor") and transfer.get("usedFor") != location:
            self.request.errors.add("body", "transfer", "Transfer already used")
            self.request.errors.status = 403
            return

        update_ownership(tender, transfer)
        self.request.validated["tender"] = tender

        transfer.usedFor = location
        self.request.validated["transfer"] = transfer

        if save_transfer(self.request):
            self.LOGGER.info(
                "Updated transfer relation {}".format(transfer.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "transfer_relation_update"}),
            )

            if save_tender(self.request):
                self.LOGGER.info(
                    "Updated ownership of tender {}".format(tender.id),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_ownership_update"}),
                )

                return {"data": tender.serialize("view")}
