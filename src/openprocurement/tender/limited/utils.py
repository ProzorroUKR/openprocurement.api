from openprocurement.api.utils import get_now
from openprocurement.tender.core.utils import (
    check_cancellation_status,
    CancelTenderLot as BaseCancelTenderLot,
    check_complaint_statuses_at_complaint_period_end
)


class ReportingCancelTenderLot(BaseCancelTenderLot):

    @staticmethod
    def cancel_tender_method(request):
        tender = request.validated["tender"]
        tender.status = "cancelled"

    @staticmethod
    def add_next_award_method(request):
        pass

    def cancel_lot(self, request, cancellation=None):
        raise NotImplementedError("N/A for this procedure")


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()
    check_complaint_statuses_at_complaint_period_end(tender, now)
    check_cancellation_status(request)


def check_tender_status(request):
    tender = request.validated["tender"]
    if (
        tender.contracts
        and any([contract.status == "active" for contract in tender.contracts])
        and not any([contract.status == "pending" for contract in tender.contracts])
    ):
        tender.status = "complete"


def check_tender_negotiation_status(request):
    tender = request.validated["tender"]
    now = get_now()
    if tender.lots:
        for lot in tender.lots:
            if lot.status != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            pending_awards_complaints = any(
                [i.status in ["claim", "answered", "pending"] for a in lot_awards for i in a.complaints]
            )
            stand_still_end = max([
                a.complaintPeriod.endDate
                if a.complaintPeriod and a.complaintPeriod.endDate else now
                for a in lot_awards
            ])
            if pending_awards_complaints or not stand_still_end <= now:
                continue
            elif last_award.status == "unsuccessful":
                lot.status = "unsuccessful"
                continue
            elif last_award.status == "active" and any(
                [i.status == "active" and i.awardID == last_award.id for i in tender.contracts]
            ):
                lot.status = "complete"
        statuses = set([lot.status for lot in tender.lots])
        if statuses == set(["cancelled"]):
            tender.status = "cancelled"
        elif not statuses.difference(set(["unsuccessful", "cancelled"])):
            tender.status = "unsuccessful"
        elif not statuses.difference(set(["complete", "unsuccessful", "cancelled"])):
            tender.status = "complete"
    else:
        if (
            tender.contracts
            and any([contract.status == "active" for contract in tender.contracts])
            and not any([contract.status == "pending" for contract in tender.contracts])
        ):
            tender.status = "complete"
