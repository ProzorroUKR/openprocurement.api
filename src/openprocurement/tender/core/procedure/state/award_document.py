from copy import deepcopy

from openprocurement.api.constants_env import AWARD_NOTICE_DOC_REQUIRED_FROM
from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_award
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import OPERATIONS, validate_doc_type_quantity


class AwardDocumentState(BaseDocumentState):
    document_post_owner_exempt_roles = ("bots",)
    # tender statuses in which award documents can be added / updated (bots: also the extra ones)
    award_document_allowed_tender_statuses: tuple = ("active.qualification",)
    award_document_bots_extra_statuses: tuple = ("active.awarded",)
    # cfaua: bots may add documents in more statuses than update them (None = the same as on update)
    award_document_post_bots_extra_statuses: tuple | None = None
    # limited: no lot / author checks, documents can be added to pending awards only
    award_document_lot_check = True
    award_document_author_check = True
    award_document_post_requires_pending_award = False
    # cfaua: no document operations while an award of the lot has an accepted complaint
    award_document_forbidden_with_accepted_lot_complaint = False

    def validate_document_operation_allowed(self):
        request, tender, award = self.request, get_tender(), get_award()
        operation = OPERATIONS.get(request.method)
        if self.award_document_post_requires_pending_award and request.method == "POST":
            if award["status"] != "pending":
                raise_operation_error(request, f"Can't add document in current ({award['status']}) award status")
        allowed_statuses = list(self.award_document_allowed_tender_statuses)
        if request.authenticated_role == "bots":
            bots_extra_statuses = self.award_document_bots_extra_statuses
            if request.method == "POST" and self.award_document_post_bots_extra_statuses is not None:
                bots_extra_statuses = self.award_document_post_bots_extra_statuses
            allowed_statuses.extend(bots_extra_statuses)
        if tender["status"] not in allowed_statuses:
            raise_operation_error(request, f"Can't {operation} document in current ({tender['status']}) tender status")
        if self.award_document_lot_check and any(
            i.get("status", "active") != "active" for i in tender.get("lots", "") if i["id"] == award.get("lotID")
        ):
            raise_operation_error(request, f"Can {operation} document only in active lot status")
        if self.award_document_forbidden_with_accepted_lot_complaint and any(
            any(c.get("status") == "accepted" for c in i.get("complaints", ""))
            for i in tender.get("awards", "")
            if i.get("lotID") == award.get("lotID")
        ):
            raise_operation_error(request, f"Can't {operation} document with accepted complaint")

    def validate_document_author_allowed(self):
        if not self.award_document_author_check:
            return
        doc_author = self.request.validated["document"].get("author") or "tender_owner"
        role = "tender_owner" if self.is_item_owner("tender") else self.request.authenticated_role
        if doc_author == "bots" and role != "bots":
            # if role != doc_author:   # TODO: unkoment when "author": "brokers" fixed
            raise_operation_error(self.request, "Can update document only author", location="url", name="role")

    def validate_document_post(self, data):
        request, tender, award = get_request(), get_tender(), get_award()
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))

    def validate_document_patch(self, before, after):
        request, tender, award = get_request(), get_tender(), get_award()
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))

    def document_always(self, data):
        super().document_always(data)
        self.validate_sign_documents_already_exists(data)

    def validate_sign_documents_already_exists(self, doc_data):
        award_docs = deepcopy(get_award().get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            award_docs.extend(new_documents)
        else:  # PATCH/PUT
            award_docs.append(doc_data)
        if tender_created_after(AWARD_NOTICE_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(award_docs, obj_name="award")
        validate_doc_type_quantity(award_docs, document_type="extensionReport", obj_name="award")
        validate_doc_type_quantity(award_docs, document_type="deviationReport", obj_name="award")
        validate_doc_type_quantity(award_docs, document_type="acceptanceReport", obj_name="award")
