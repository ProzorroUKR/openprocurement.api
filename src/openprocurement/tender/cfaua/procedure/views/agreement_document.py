from openprocurement.tender.core.procedure.views.document import BaseDocumentResource, resolve_document
from openprocurement.tender.core.procedure.views.agreement import resolve_agreement
from openprocurement.tender.cfaua.procedure.state.agreement_document import AgreementDocumentState
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Agreement Documents",
    collection_path="/tenders/{tender_id}/agreements/{agreement_id}/documents",
    path="/tenders/{tender_id}/agreements/{agreement_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender agreement documents",
)
class CFAUATenderAgreementDocumentResource(BaseDocumentResource):
    item_name = "agreement"
    state_class = AgreementDocumentState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_agreement(request)
            resolve_document(request, item_name="agreement", container="documents")
