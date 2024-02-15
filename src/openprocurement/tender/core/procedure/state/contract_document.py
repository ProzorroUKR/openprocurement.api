from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.context import get_award
from openprocurement.tender.core.procedure.state.document import BaseDocumentState


class ContractDocumentState(BaseDocumentState):
    def validate_document_post(self, data):
        request, tender, award = get_request(), get_tender(), get_award()
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))

    def validate_document_patch(self, before, after):
        request, tender, award = get_request(), get_tender(), get_award()
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))
