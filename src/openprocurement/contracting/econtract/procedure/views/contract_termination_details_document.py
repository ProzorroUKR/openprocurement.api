from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.views.document import (
    BaseDocumentResource,
)
from openprocurement.contracting.econtract.procedure.state.contract_termination_details_document import (
    EContractTerminationDetailsDocumentState,
)
from openprocurement.contracting.econtract.procedure.views.contract_termination_details import (
    resolve_termination_details,
)
from openprocurement.tender.core.procedure.views.document import resolve_document


@resource(
    name="EContract termination_details documents",
    collection_path="/contracts/{contract_id}/termination_details/documents",
    path="/contracts/{contract_id}/termination_details/documents/{document_id}",
    contractType="eContract",
    description="EContract terminationDetails related binary files (signed termination notice, etc.)",
    request_method=("POST",),
)
class EContractTerminationDetailsDocumentResource(BaseDocumentResource):
    state_class = EContractTerminationDetailsDocumentState
    item_name = "termination_details"

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        if not context:
            resolve_termination_details(request)
            resolve_document(request, self.item_name, self.container)

    @json_view(
        permission="edit_contract",
    )
    def collection_post(self):
        return super().collection_post()
