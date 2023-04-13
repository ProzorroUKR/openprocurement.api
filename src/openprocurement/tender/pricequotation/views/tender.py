# -*- coding: utf-8 -*-
from openprocurement.api.utils import context_unpack, json_view, get_now
from openprocurement.tender.core.utils import optendersresource, apply_patch
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
)

from openprocurement.tender.belowthreshold.views.tender import TenderResource
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.validation import validate_patch_tender_data, validate_tender_publish


# @optendersresource(
#     name="{}:Tender".format(PMT),
#     path="/tenders/{tender_id}",
#     procurementMethodType=PMT,
# )
class PriceQuotationTenderResource(TenderResource):
    """
    PriceQuotation tender creation and updation
    """
    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_data,
            validate_tender_publish,
            validate_tender_not_in_terminated_status,
        ),
        permission="edit_tender",
    )
    def patch(self):
        tender = self.context
        new_status = self.request.validated["data"].get("status", "")
        if tender.status == "draft" and new_status == "draft.publishing" and not tender.noticePublicationDate:
            now = get_now()
            self.request.validated["data"]["noticePublicationDate"] = now.isoformat()
            self.request.validated["data"]["tenderPeriod"]["startDate"] = now.isoformat()
        apply_patch(self.request, src=self.request.validated["tender_src"])
        self.LOGGER.info(
            "Updated tender {}".format(tender.id), extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
        )
        return {"data": tender.serialize(tender.status)}
