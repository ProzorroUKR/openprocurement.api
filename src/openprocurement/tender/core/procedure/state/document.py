from openprocurement.api.procedure.models.document import ConfidentialityType
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.models.document import Document, PatchDocument, PostDocument
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.validation import (
    validate_edrpou_confidentiality_doc,
)


class BaseDocumentStateMixin:
    post_data_model = PostDocument
    patch_data_model = PatchDocument
    data_model = Document

    # the object whose owner may change the documents (request.validated key)
    document_owner_item_name = "tender"
    # roles that may add / update the documents without being the owner
    document_post_owner_exempt_roles: tuple = ()
    document_update_owner_exempt_roles: tuple = ()
    edrpou_confidentiality_check = True
    all_documents_should_be_public = False
    allow_deletion = False
    deletion_allowed_statuses = ("draft",)

    def validate_get_request(self):
        self.validate_document_view_allowed()
        self.validate_document_download_allowed()

    def validate_post_request(self):
        self.validate_document_owner(self.document_post_owner_exempt_roles)
        self.validate_input_data(self.get_post_data_model(), allow_bulk=True)
        self.validate_document_operation_allowed()

    def validate_put_request(self):
        self.validate_document_owner(self.document_update_owner_exempt_roles)
        self.validate_input_data(self.get_post_data_model())
        self.update_doc_fields_on_put_document()
        self.validate_document_operation_allowed()
        self.validate_document_author_allowed()
        self.validate_upload_document()
        self.validate_data_model(self.get_data_model())

    def validate_patch_request(self):
        self.validate_document_owner(self.document_update_owner_exempt_roles)
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data(self.get_data_model(), "document")
        self.validate_document_operation_allowed()
        self.validate_document_author_allowed()

    def validate_delete_request(self):
        self.validate_document_owner(())
        self.validate_document_author_allowed()

    def validate_document_owner(self, exempt_roles):
        if self.request.authenticated_role not in exempt_roles:
            self.validate_item_owner(self.document_owner_item_name)

    def validate_document_view_allowed(self):
        pass

    def validate_document_operation_allowed(self):
        """Availability of the add / update operation: statuses of the tender and of the parent object"""

    def validate_document_author_allowed(self):
        """Only the author may update the document (tender / award documents)"""

    def validate_document_download_allowed(self):
        request = self.request
        if not request.params.get("download") or "document" not in request.validated:
            return
        document = request.validated["document"]
        if (
            document.get("confidentiality", "") == ConfidentialityType.BUYER_ONLY
            and request.authenticated_role not in ("aboveThresholdReviewers", "sas")
            and not ("bid" in request.validated and self.is_item_owner("bid"))
            and not self.is_item_owner("tender")
        ):
            raise_operation_error(request, "Document download forbidden.")

    def document_on_post(self, data):
        self.validate_document_post(data)
        self.document_always(data)

    def document_on_patch(self, before, after):
        self.validate_document_patch(before, after)
        self.document_always(after)

    def document_always(self, data):
        pass

    def validate_confidentiality(self, data):
        if not self.edrpou_confidentiality_check:
            return
        validate_edrpou_confidentiality_doc(data, should_be_public=self.all_documents_should_be_public)

    def validate_document_post(self, data):
        pass

    def validate_document_patch(self, before, after):
        pass

    def validate_document_delete(self, item, item_name):
        if not self.allow_deletion:
            raise_operation_error(
                self.request,
                f"Forbidden to delete document for {item_name}",
            )
        if item.get("status") not in self.deletion_allowed_statuses:
            raise_operation_error(
                self.request,
                f"Can't delete document when {item_name} in current ({item['status']}) status",
            )


class BaseDocumentState(BaseDocumentStateMixin, TenderState):
    def validate_document_author(self, document):
        if self.request.authenticated_role != document["author"]:
            raise_operation_error(
                self.request,
                "Can update document only author",
                location="url",
                name="role",
            )

    def document_always(self, data):
        self.invalidate_review_requests()
        self.validate_confidentiality(data)
