# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)
from openprocurement.tender.core.validation import (
    validate_award_document_tender_not_in_allowed_status_base,
    validate_award_document_author,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.award_document import TenderAwardDocumentResource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Award Documents".format(PMT),
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender award documents",
)
class PQTenderAwardDocumentResource(TenderAwardDocumentResource):
    """ PriceQuotation award document resource """
    
    @json_view(
        validators=(
            validate_file_upload,
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_author,
        ),
        permission="upload_award_documents"
    )
    def collection_post(self):
        return super(TenderAwardDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_author,
        ),
        permission="upload_award_documents"
    )
    def put(self):
        return super(TenderAwardDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_author,
        ),
        permission="upload_award_documents",
    )
    def patch(self):
        return super(TenderAwardDocumentResource, self).patch()
