from openprocurement.api.database import atomic_transaction
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_download_contract_document,
)
from openprocurement.contracting.core.procedure.views.document import (
    BaseDocumentResource,
)
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.views.document import resolve_document


class ContractDocumentResource(BaseDocumentResource):
    state_class = ContractDocumentState

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        if not context:
            resolve_document(request, self.item_name, self.container)

    def save(self, **kwargs):
        with atomic_transaction():
            contract = self.request.validated["contract"]
            if self.request.validated.get("contract_was_changed"):
                if save_tender(self.request):
                    self.LOGGER.info(
                        f"Updated tender {self.request.validated['tender']['_id']} contract {contract['_id']}",
                        extra=context_unpack(
                            self.request,
                            {"MESSAGE_ID": "tender_contract_update_status"},
                        ),
                    )
            return save_contract(self.request, **kwargs)

    @json_view(
        validators=(validate_download_contract_document,),
        permission="view_contract",
    )
    def get(self):
        return super().get()
