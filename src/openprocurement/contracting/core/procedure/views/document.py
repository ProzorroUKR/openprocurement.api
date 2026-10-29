from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.tender.core.procedure.documents import get_file
from openprocurement.tender.core.procedure.views.document import DocumentResourceMixin


class BaseDocumentResource(DocumentResourceMixin, ContractBaseResource):
    state_class = ContractDocumentState
    serializer_class = DocumentSerializer
    container = "documents"
    item_name = "contract"

    def save(self, **kwargs):
        return save_contract(self.request, **kwargs)

    def get_file(self):
        return get_file(self.request, item_name="contract")

    @json_view(permission="view_contract")
    def collection_get(self):
        return super().collection_get()

    @json_view(
        permission="upload_contract_documents",
    )
    def collection_post(self):
        self.state.validate_document_post_request()
        return super().collection_post()

    @json_view(permission="view_contract")
    def get(self):
        self.state.validate_document_get_request()
        return super().get()

    @json_view(
        permission="edit_contract_documents",
    )
    def put(self):
        self.state.validate_document_put_request()
        return super().put()

    @json_view(
        content_type="application/json",
        permission="edit_contract_documents",
    )
    def patch(self):
        self.state.validate_document_patch_request()
        return super().patch()
