from copy import deepcopy

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules
from openprocurement.tender.core.procedure.validation import OPERATIONS, validate_doc_type_quantity


class QualificationDocumentStateMixin:
    document_post_owner_exempt_roles = ("bots",)
    document_update_owner_exempt_roles = ("bots",)

    def validate_document_operation_allowed(self):
        request, tender = self.request, get_tender()
        qualification = request.validated["qualification"]
        lot_id = qualification.get("lotID")
        if (
            tender_created_after_2020_rules()
            and lot_id
            and request.authenticated_role == "tender_owner"
            and any(i["status"] == "pending" and i.get("relatedLot") == lot_id for i in tender.get("cancellations", ""))
        ):
            raise_operation_error(request, "Can't update qualification with pending cancellation lot")
        if tender["status"] != "active.pre-qualification":
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} document in current ({tender['status']}) tender status",
            )
        if qualification["status"] != "pending":
            raise_operation_error(
                request, f"Can't {OPERATIONS.get(request.method)} document in current qualification status"
            )


class QualificationDocumentState(QualificationDocumentStateMixin, BaseDocumentState):
    def document_always(self, data):
        super().document_always(data)
        self.validate_sign_documents_already_exists(data)

    def validate_sign_documents_already_exists(self, doc_data):
        qualification = self.request.validated["qualification"]
        qualification_docs = deepcopy(qualification.get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            qualification_docs.extend(new_documents)
        else:  # PATCH/PUT
            qualification_docs.append(doc_data)
        validate_doc_type_quantity(qualification_docs, document_type="deviationReport", obj_name="qualification")
