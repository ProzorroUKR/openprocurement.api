from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing
from openprocurement.tender.core.procedure.state.cancellation import CancellationState
from openprocurement.tender.core.procedure.context import get_tender, get_request, get_cancellation


class AgreementDocumentStateMixing(BaseDocumentStateMixing):

    @staticmethod
    def validate_agreement_document(request, tender, agreement, operation):
        tender_status = tender["status"]
        if tender_status not in ("active.qualification", "active.awarded"):
            raise_operation_error(
                request,
                f"Can't {operation} document in current ({tender_status}) tender status",
            )

        award_ids = tuple(c["awardID"] for c in agreement.get("contracts", ""))
        lot_ids = tuple(
            a.get("lotID")
            for a in tender.get("awards", "")
            if a["id"] in award_ids
        )
        if any(
            i["status"] != "active"
            for i in tender.get("lots", "")
            if i["id"] in lot_ids
        ):
            raise_operation_error(request, f"Can {operation} document only in active lot status")

        if agreement["status"] not in ("pending", "active"):
            raise_operation_error(request, f"Can't {operation} document in current agreement status")

        if any(
            any(c["status"] == "accepted"
                for c in i.get("complaints", ""))
            for i in tender.get("awards", "")
            if i.get("lotID") in lot_ids
        ):
            raise_operation_error(request, f"Can't {operation} document with accepted complaint")
        return True


class AgreementDocumentState(AgreementDocumentStateMixing, CancellationState):
    def validate_document_post(self, data):
        request, tender, cancellation = get_request(), get_tender(), get_cancellation()

        self.validate_agreement_document(request, tender, request.validated["agreement"],
                                         operation="add" if request.method == "POST" else "update")

    def validate_document_patch(self, before, after):
        request, tender, cancellation = get_request(), get_tender(), get_cancellation()
        self.validate_agreement_document(request, tender, request.validated["agreement"], operation="update")
