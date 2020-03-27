# -*- coding: utf-8 -*-
from datetime import timedelta

from openprocurement.tender.core.views.cancellation_complaint import TenderCancellationComplaintResource
from openprocurement.tender.core.utils import optendersresource, calculate_tender_business_date


@optendersresource(
    name="negotiation:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation",
    description="Tender cancellation complaints",
)
class TenderNegotiationCancellationComplaintResource(TenderCancellationComplaintResource):
    """Tender Negotiation Cancellation Complaints """

    def recalculate_tender_periods(self):
        tender = self.request.validated["tender"]
        cancellation = self.request.validated["cancellation"]
        tenderer_action_date = self.context.tendererActionDate

        date = cancellation.complaintPeriod.startDate

        delta = (tenderer_action_date - date).days
        delta_plus = 1 if (tenderer_action_date - date).seconds > 3599 else 0

        delta += delta_plus

        delta = timedelta(days=1 if not delta else delta)

        if tender.status in ["active"]:
            for award in tender.awards:
                complaint_period = award.complaintPeriod
                if (
                    complaint_period
                    and complaint_period.startDate
                    and complaint_period.endDate
                    and award.complaintPeriod.startDate < date < award.complaintPeriod.endDate
                ):
                    award.complaintPeriod.endDate = calculate_tender_business_date(
                        award.complaintPeriod.endDate, delta, tender)


@optendersresource(
    name="negotiation.quick:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation.quick",
    description="Tender cancellation complaints",
)
class TenderNegotiationQuickCancellationComplaintResource(TenderNegotiationCancellationComplaintResource):
    """Tender Negotiation Quick Cancellation Complaints """
