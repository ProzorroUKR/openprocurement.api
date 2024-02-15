from openprocurement.contracting.core.procedure.views.document import (
    BaseDocumentResource,
)
from openprocurement.tender.core.procedure.views.document import resolve_document


class ContractDocumentResource(BaseDocumentResource):
    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        if not context:
            resolve_document(request, self.item_name, self.container)
