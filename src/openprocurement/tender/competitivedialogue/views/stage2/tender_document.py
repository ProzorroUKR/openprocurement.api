# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import (
    validate_file_upload,
    validate_file_update,
    validate_patch_document_data,
)
from openprocurement.tender.competitivedialogue.validation import validate_update_tender_document
from openprocurement.tender.core.validation import (
    validate_tender_document_update_not_by_author_or_tender_owner,
    validate_document_operation_in_not_allowed_period,
    validate_patch_document_contract_proforma,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.tender_document import TenderEUDocumentResource
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE


@optendersresource(
    name="{}:Tender Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU related binary files (PDFs, etc.)",
)
class CompetitiveDialogueStage2EUDocumentResource(TenderEUDocumentResource):
    @json_view(
        permission="upload_tender_documents",
        validators=(
                validate_file_upload,
                validate_document_operation_in_not_allowed_period,
                validate_update_tender_document,
        ),
    )
    def collection_post(self):
        return super(TenderEUDocumentResource, self).collection_post()

    @json_view(
        permission="upload_tender_documents",
        validators=(
                validate_file_update,
                validate_document_operation_in_not_allowed_period,
                validate_tender_document_update_not_by_author_or_tender_owner,
                validate_update_tender_document,
        ),
    )
    def put(self):
        return super(TenderEUDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_tender_documents",
        validators=(
                validate_patch_document_data,
                validate_patch_document_contract_proforma,
                validate_document_operation_in_not_allowed_period,
                validate_tender_document_update_not_by_author_or_tender_owner,
                validate_update_tender_document,
        ),
    )
    def patch(self):
        return super(TenderEUDocumentResource, self).patch()


@optendersresource(
    name="{}:Tender Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA related binary files (PDFs, etc.)",
)
class CompetitiveDialogueStage2UADocumentResource(TenderUaDocumentResource):
    pass
