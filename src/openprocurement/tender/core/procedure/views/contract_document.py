from cornice.resource import resource
from pyramid.security import Allow, Everyone

from openprocurement.api.utils import json_view, raise_operation_error
from openprocurement.tender.core.procedure.validation import (
    validate_download_tender_document,
)
from openprocurement.tender.core.procedure.views.contract import resolve_contract
from openprocurement.tender.core.procedure.views.document import (
    BaseDocumentResource,
    resolve_document,
)


@resource(
    name="Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    description="Tender contract documents",
)
class TenderContractDocumentResource(BaseDocumentResource):
    item_name = "contract"

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
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

    @json_view(
        validators=(validate_download_tender_document,),
        permission="view_tender",
    )
    def get(self):
        return super().get()

    def collection_post(self):
        raise_operation_error(self.request, "Method Not Allowed", status=405)

    def put(self):
        raise_operation_error(self.request, "Method Not Allowed", status=405)

    def patch(self):
        raise_operation_error(self.request, "Method Not Allowed", status=405)
