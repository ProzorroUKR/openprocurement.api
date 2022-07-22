# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.views.cancellation_document import TenderCancellationDocumentResource
from openprocurement.tender.core.utils import optendersresource


# @optendersresource(
#     name="closeFrameworkAgreementSelectionUA:Tender Cancellation Documents",
#     collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
#     path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
#     procurementMethodType="closeFrameworkAgreementSelectionUA",
#     description="Tender cancellation documents",
# )
class TenderCFASUACancellationDocumentResource(TenderCancellationDocumentResource):
    """ Cancellation Document """
