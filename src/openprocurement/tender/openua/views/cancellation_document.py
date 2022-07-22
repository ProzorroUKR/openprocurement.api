# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.cancellation_document import TenderCancellationDocumentResource


# @optendersresource(
#     name="aboveThresholdUA:Tender Cancellation Documents",
#     collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
#     path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
#     procurementMethodType="aboveThresholdUA",
#     description="Tender UA cancellation documents",
# )
class TenderUaCancellationDocumentResource(TenderCancellationDocumentResource):
    pass
