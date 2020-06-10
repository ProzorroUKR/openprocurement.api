# -*- coding: utf-8 -*-
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.utils import\
    save_tender, optendersresource, apply_patch
from openprocurement.tender.core.validation import\
    validate_tender_not_in_terminated_status

from openprocurement.tender.belowthreshold.views.tender import TenderResource
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.tender.pricequotation.utils import check_status
from openprocurement.tender.pricequotation.validation import\
    validate_patch_tender_data


@optendersresource(
    name="{}:Tender".format(PMT),
    path="/tenders/{tender_id}",
    procurementMethodType=PMT,
)
class PriceQuotationTenderResource(TenderResource):
    """
    PriceQuotation tender creation and updation
    """
    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_data,
            validate_tender_not_in_terminated_status,
        ),
        permission="edit_tender",
    )
    def patch(self):
        tender = self.context
        if self.request.authenticated_role == "chronograph":
            apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
            check_status(self.request)
            save_tender(self.request)
        else:
            apply_patch(self.request, src=self.request.validated["tender_src"])
        self.LOGGER.info(
            "Updated tender {}".format(tender.id), extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
        )
        return {"data": tender.serialize(tender.status)}
