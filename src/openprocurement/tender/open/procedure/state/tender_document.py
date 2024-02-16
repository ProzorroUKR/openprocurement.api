from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_document import (
    TenderDocumentState,
)
from openprocurement.tender.open.procedure.state.tender_details import (
    OpenTenderDetailsState,
)


class UATenderDocumentState(TenderDocumentState):
    def document_on_post(self, data):
        super().document_on_post(data)
        self.invalidate_bids_data()

    def document_on_patch(self, before, after):
        super().document_on_patch(before, after)
        self.invalidate_bids_data()

    def invalidate_bids_data(self):
        tender = get_tender()
        if is_item_owner(get_request(), tender) and tender.get("status") == "active.tendering":
            tender_state = OpenTenderDetailsState(self.request)
            tender_state.validate_tender_period_extension(tender)
            tender_state.invalidate_bids_data(tender)
