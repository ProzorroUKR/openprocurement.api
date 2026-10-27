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
        contract_was_changed = self.request.validated.get("contract_was_changed")
        contract = self.request.validated["contract"]
        # keep only db writes inside the transaction: the time between save_data and commit
        # must be minimal, see docs/source/developers/projects/cdb/feed_ordering.rst
        with atomic_transaction(enabled=bool(contract_was_changed)):
            tender_saved = False
            if contract_was_changed:
                tender_saved = save_tender(self.request)
            contract_saved = save_contract(self.request, **kwargs)

        if tender_saved:
            self.LOGGER.info(
                f"Updated tender {self.request.validated['tender']['_id']} contract {contract['_id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_contract_update_status"},
                ),
            )
        return contract_saved

    @json_view(
        validators=(validate_download_contract_document,),
        permission="view_contract",
    )
    def get(self):
        return super().get()
