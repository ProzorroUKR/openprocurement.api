from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import get_tender, get_request, \
    get_cancellation
from openprocurement.tender.core.procedure.utils import since_2020_rules


class CancellationDocumentStateMixing(BaseDocumentStateMixing, CancellationStateMixing):

    @staticmethod
    def validate_cancellation_document_allowed(request, _, cancellation):
        if since_2020_rules():
            status = cancellation["status"]
            if status == "draft":
                pass
            elif status == "pending" and any(i.get("status") == "satisfied"
                                             for i in cancellation.get("complaints", "")):
                raise_operation_error(
                    request,
                    f"Document can't be {OPERATIONS.get(request.method)} in current({status}) cancellation status"
                )

    def validate_document_post(self, data):
        request, tender, cancellation = get_request(), get_tender(), get_cancellation()
        self.validate_cancellation_in_allowed_tender_status(request, tender, cancellation)
        self.validate_cancellation_document_allowed(request, tender, cancellation)
        self.validate_pending_cancellation_present(request, tender, cancellation)

    def validate_document_patch(self, before, after):
        request, tender, cancellation = get_request(), get_tender(), get_cancellation()
        self.validate_cancellation_in_allowed_tender_status(request, tender, cancellation)
        self.validate_cancellation_document_allowed(request, tender, cancellation)
        self.validate_pending_cancellation_present(request, tender, cancellation)


class CancellationDocumentState(CancellationDocumentStateMixing, TenderState):
    pass
