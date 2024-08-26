from datetime import timedelta

from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class NegotiationCancellationComplaintState(CancellationComplaintStateMixin, NegotiationTenderState):
    def validate_post_cancellation_complaint_permission(self):
        pass

    def recalculate_tender_periods(self, complaint):
        tender = self.request.validated["tender"]
        cancellation = self.request.validated["cancellation"]

        tenderer_action_date = dt_from_iso(complaint["tendererActionDate"])
        date = dt_from_iso(cancellation["complaintPeriod"]["startDate"])

        delta = (tenderer_action_date - date).days
        delta_plus = 1 if (tenderer_action_date - date).seconds > 3599 else 0
        delta += delta_plus
        delta = timedelta(days=1 if not delta else delta)

        if tender["status"] == "active":
            for award in tender.get("awards", ""):
                if complaint_period := award.get("complaintPeriod"):
                    if start_date := complaint_period.get("startDate"):
                        if end_date := complaint_period.get("endDate"):
                            if dt_from_iso(start_date) < date < dt_from_iso(end_date):
                                award["complaintPeriod"]["endDate"] = calculate_tender_full_date(
                                    end_date,
                                    delta,
                                    tender=tender,
                                ).isoformat()
