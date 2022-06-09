from openprocurement.tender.core.procedure.views.contract_document import TenderContractDocumentResource
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.tender.core.procedure.validation import (
    validate_item_owner,
    unless_admins,
    validate_input_data,
    validate_patch_data,
    unless_bots,
    update_doc_fields_on_put_document,
    validate_upload_document,
    validate_data_model,
)
from openprocurement.tender.limited.procedure.validation import (
    validate_document_operation_not_in_active,
    validate_contract_document_operation_not_in_allowed_contract_status,
)
from cornice.resource import resource


@resource(
    name="reporting:Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType="reporting",
    description="Tender contract documents",
)
class ReportingContractDocumentResource(TenderContractDocumentResource):
    @json_view(
        validators=(
            unless_bots(unless_admins(validate_item_owner("tender"))),
            validate_input_data(PostDocument, allow_bulk=True),
            validate_document_operation_not_in_active,
            validate_contract_document_operation_not_in_allowed_contract_status("add"),
        ),
        permission="upload_contract_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            unless_bots(unless_admins(validate_item_owner("tender"))),
            validate_input_data(PostDocument),
            validate_document_operation_not_in_active,
            validate_contract_document_operation_not_in_allowed_contract_status("update"),

            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(Document),
        ),
        permission="upload_contract_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        validators=(
            unless_bots(unless_admins(validate_item_owner("tender"))),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),
            validate_document_operation_not_in_active,
            validate_contract_document_operation_not_in_allowed_contract_status("update"),
        ),
        permission="upload_contract_documents",
    )
    def patch(self):
        return super().patch()


@resource(
    name="negotiation:Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType="negotiation",
    description="Tender contract documents",
)
class NegotiationContractDocumentResource(ReportingContractDocumentResource):
    pass


@resource(
    name="negotiation.quick:Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType="negotiation.quick",
    description="Tender contract documents",
)
class NegotiationQuickContractDocumentResource(ReportingContractDocumentResource):
    pass
