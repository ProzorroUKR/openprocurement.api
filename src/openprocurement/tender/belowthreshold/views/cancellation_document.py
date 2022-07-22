# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)

from openprocurement.tender.core.utils import (
    optendersresource,
)

from openprocurement.tender.core.validation import (
    validate_cancellation_operation_document,
    validate_operation_cancellation_permission,
)
from openprocurement.tender.belowthreshold.validation import (
    validate_cancellation_document_operation_not_in_allowed_status,
)
from openprocurement.tender.core.views.document import CoreDocumentResource


# @optendersresource(
#     name="belowThreshold:Tender Cancellation Documents",
#     collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
#     path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
#     procurementMethodType="belowThreshold",
#     description="Tender cancellation documents",
# )
class TenderCancellationDocumentResource(CoreDocumentResource):
    container = "documents"
    context_name = "tender_cancellation"

    @json_view(
        validators=(
            validate_file_upload,
            validate_cancellation_document_operation_not_in_allowed_status,
            validate_operation_cancellation_permission,
            validate_cancellation_operation_document,
        ),
        permission="edit_cancellation",
    )
    def collection_post(self):
        """Tender Cancellation Document Upload
        """
        return super(TenderCancellationDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_cancellation_document_operation_not_in_allowed_status,
            validate_operation_cancellation_permission,
            validate_cancellation_operation_document,
        ),
        permission="edit_cancellation",
    )
    def put(self):
        """Tender Cancellation Document Update"""
        return super(TenderCancellationDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_cancellation_document_operation_not_in_allowed_status,
            validate_operation_cancellation_permission,
            validate_cancellation_operation_document,
        ),
        permission="edit_cancellation",
    )
    def patch(self):
        """Tender Cancellation Document Update"""
        return super(TenderCancellationDocumentResource, self).patch()
