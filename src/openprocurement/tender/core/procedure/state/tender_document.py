from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.api.context import get_request
from openprocurement.tender.core.procedure.context import get_tender


class TenderDocumentState(BaseDocumentState):
    def validate_document_post(self, data):
        request, tender = get_request(), get_tender()
        self.validate_cancellation_blocks(request, tender)

    def validate_document_patch(self, before, after):
        request, tender = get_request(), get_tender()
        self.validate_cancellation_blocks(request, tender)

