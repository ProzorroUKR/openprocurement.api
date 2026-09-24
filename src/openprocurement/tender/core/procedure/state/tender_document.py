from copy import deepcopy

from openprocurement.api.constants_env import (
    BELOWTHRESHOLD_FUNDERS_IDS,
    EVALUATION_REPORTS_DOC_REQUIRED_FROM,
    NOTICE_DOC_REQUIRED_FROM,
)
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import OPERATIONS, validate_doc_type_quantity


class TenderDocumentState(BaseDocumentState):
    document_post_owner_exempt_roles = ("bots", "auction")
    document_update_owner_exempt_roles = ("bots", "auction")
    # tender statuses in which documents can be added / updated
    document_operation_allowed_tender_statuses: tuple = (
        "draft",
        "draft.stage2",  # competitive dialogue
        "active.enquiries",
        "active.tendering",
    )
    # belowThreshold: tenders of BELOWTHRESHOLD_FUNDERS_IDS also allow it in these statuses
    document_operation_allowed_tender_statuses_for_funder: tuple = ()
    # the auction role has its own allowed statuses (None = the same as everyone)
    document_operation_auction_role_statuses: tuple | None = ("active.auction", "active.qualification")
    # evaluation reports (sign docs) only are also allowed in these statuses
    document_operation_sign_docs_extra_statuses: tuple = ("active.pre-qualification",)

    def validate_document_operation_allowed(self):
        request = self.request
        tender = get_tender()
        allowed_statuses = list(self.document_operation_allowed_tender_statuses)
        if tender.get("_id") in BELOWTHRESHOLD_FUNDERS_IDS:
            allowed_statuses.extend(self.document_operation_allowed_tender_statuses_for_funder)
        if request.authenticated_role == "auction" and self.document_operation_auction_role_statuses is not None:
            allowed_statuses = list(self.document_operation_auction_role_statuses)
        else:
            data = request.validated["data"]
            documents = data if isinstance(data, list) else [data]
            if all(doc.get("documentType") == "evaluationReports" for doc in documents):
                allowed_statuses.extend(self.document_operation_sign_docs_extra_statuses)
        if tender["status"] not in allowed_statuses:
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} document in current ({tender['status']}) tender status",
            )

    def validate_document_author_allowed(self):
        document = self.request.validated["document"]
        role = "tender_owner" if self.is_item_owner("tender") else self.request.authenticated_role
        if role != (document.get("author") or "tender_owner"):
            raise_operation_error(self.request, "Can update document only author", location="url", name="role")

    allow_deletion = True
    deletion_allowed_statuses = ("draft", "draft.stage2")
    # bt/rfp/open/openua/CO (and their heirs): pending bids become invalid after a tender document change
    invalidate_bids_on_document_change = False

    def document_on_post(self, data):
        super().document_on_post(data)
        if self.invalidate_bids_on_document_change:
            self.invalidate_bids_data(get_tender())

    def document_on_patch(self, before, after):
        super().document_on_patch(before, after)
        if self.invalidate_bids_on_document_change:
            self.invalidate_bids_data(get_tender())

    def validate_sign_documents_already_exists(self, doc_data):
        tender_docs = deepcopy(get_tender().get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            tender_docs.extend(new_documents)
        else:  # PATCH/PUT
            tender_docs.append(doc_data)
        if tender_created_after(NOTICE_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(tender_docs)
        if tender_created_after(EVALUATION_REPORTS_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(tender_docs, document_type="evaluationReports")
        validate_doc_type_quantity(tender_docs, document_type="acceptanceReport")

    def document_always(self, data: dict) -> None:
        self.validate_sign_documents_already_exists(data)
        if data.get("documentType") != "notice":
            self.validate_action_with_exist_inspector_review_request()
        self.validate_contract_proforma_document(data)
        super().document_always(data)

    def validate_contract_proforma_document(self, data: dict) -> None:
        if data.get("documentType") != "contractProforma":
            return

        tender = self.request.validated["tender"]
        if tender.get("contractTemplateName"):
            raise_operation_error(
                self.request,
                "Cannot use both contractTemplateName and contractProforma document simultaneously",
                status=422,
            )
