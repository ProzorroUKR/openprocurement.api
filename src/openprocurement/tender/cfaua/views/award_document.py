# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import validate_file_upload
from openprocurement.tender.cfaua.validation import validate_award_document_tender_not_in_allowed_status
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import (
    validate_award_document_lot_not_in_allowed_status,
    validate_award_document_author)
from openprocurement.tender.openua.validation import validate_accepted_complaints
from openprocurement.tender.openua.views.award_document import TenderUaAwardDocumentResource as BaseResource


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender award documents",
)
class TenderAwardDocumentResource(BaseResource):
    """ Tender Award Document """
    @json_view(
        validators=(
            validate_file_upload,
            validate_award_document_tender_not_in_allowed_status,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author,
            validate_accepted_complaints
        ),
        permission="upload_tender_documents",
    )
    def collection_post(self):
        return super(BaseResource, self).collection_post()
