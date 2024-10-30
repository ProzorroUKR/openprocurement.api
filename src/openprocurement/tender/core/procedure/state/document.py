from openprocurement.api.constants import CONFIDENTIAL_EDRPOU_LIST
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.document import ConfidentialityTypes
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.tender import TenderState


class BaseDocumentStateMixing:
    check_edrpou_confidentiality = True
    all_documents_should_be_public = False

    def document_on_post(self, data):
        self.validate_document_post(data)
        self.document_always(data)

    def document_on_patch(self, before, after):
        self.validate_document_patch(before, after)
        self.document_always(after)

    def document_always(self, data):
        pass

    def validate_confidentiality(self, data):
        if not self.check_edrpou_confidentiality:
            return
        tender = get_tender()
        if (
            not self.all_documents_should_be_public
            and data.get("title") == "sign.p7s"
            and data.get("format") == "application/pkcs7-signature"
            and data.get("author", "tender_owner") == "tender_owner"
            and tender.get("procuringEntity", {}).get("identifier", {}).get("id") in CONFIDENTIAL_EDRPOU_LIST
        ):
            if data["confidentiality"] != ConfidentialityTypes.BUYER_ONLY:
                raise_operation_error(
                    self.request,
                    "Document should be confidential",
                    name="confidentiality",
                    status=422,
                )
        elif data["confidentiality"] == ConfidentialityTypes.BUYER_ONLY:
            raise_operation_error(
                self.request,
                "Document should be public",
                name="confidentiality",
                status=422,
            )

    def validate_document_post(self, data):
        pass

    def validate_document_patch(self, before, after):
        pass


class BaseDocumentState(BaseDocumentStateMixing, TenderState):
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
