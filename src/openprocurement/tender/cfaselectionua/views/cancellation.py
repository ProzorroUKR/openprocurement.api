# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.cfaselectionua.utils import add_next_award
from openprocurement.tender.belowthreshold.views.cancellation import \
    TenderCancellationResource as BaseTenderCancellationResource


@optendersresource(
    name="closeFrameworkAgreementSelectionUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender cancellations",
)
class TenderCancellationResource(BaseTenderCancellationResource):
    add_next_award_method = add_next_award
