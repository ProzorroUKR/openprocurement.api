from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.contract_document import ContractDocumentState
from openprocurement.tender.core.procedure.views.contract import resolve_contract
from openprocurement.tender.core.procedure.views.document import BaseDocumentResource, resolve_document
from pyramid.security import Allow, Everyone


class TenderContractDocumentResource(BaseDocumentResource):
    item_name = "contract"
    state_class = ContractDocumentState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "edit_contract"),
            (Allow, "g:brokers", "upload_contract_documents"),
            (Allow, "g:brokers", "edit_contract_documents"),
            (Allow, "g:bots", "upload_contract_documents"),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_contract(request)
            resolve_document(request, self.item_name, self.container)

    @json_view(permission="view_tender")
    def collection_get(self):
        return super().collection_get()

    @json_view(permission="view_tender")
    def get(self):
        return super().get()
