from logging import getLogger
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.constants import (
    TZ,
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
)
from openprocurement.tender.core.utils import (
    check_complaint_statuses_at_complaint_period_end,
    context_unpack,
    get_now,
    has_unanswered_questions,
    has_unanswered_complaints,
    cancellation_block_tender,
)
from openprocurement.tender.openua.utils import (
    check_complaint_status,
    check_cancellation_status,
    add_next_award as add_next_award_base,
)
from openprocurement.tender.belowthreshold.utils import check_tender_status
from openprocurement.tender.core.utils import (
    calculate_tender_business_date as calculate_tender_business_date_base,
    calculate_clarif_business_date as calculate_clarif_business_date_base,
    calculate_complaint_business_date as calculate_complaint_business_date_base
)
from openprocurement.tender.openuadefense.constants import WORKING_DAYS

LOGGER = getLogger("openprocurement.tender.openuadefense")


def calculate_tender_business_date(date_obj, timedelta_obj, tender=None, working_days=False):
    return calculate_tender_business_date_base(
        date_obj, timedelta_obj, tender=tender, working_days=working_days, calendar=WORKING_DAYS
    )

def calculate_complaint_business_date(date_obj, timedelta_obj, tender=None, working_days=False):
    return calculate_complaint_business_date_base(
        date_obj, timedelta_obj, tender=tender, working_days=working_days, calendar=WORKING_DAYS
    )

def calculate_clarif_business_date(date_obj, timedelta_obj, tender=None, working_days=False):
    return calculate_clarif_business_date_base(
        date_obj, timedelta_obj, tender=tender, working_days=working_days, calendar=WORKING_DAYS
    )


def check_bids(request):
    tender = request.validated["tender"]

    if tender.lots:
        [
            setattr(i.auctionPeriod, "startDate", None)
            for i in tender.lots
            if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate
        ]
        [
            setattr(i, "status", "unsuccessful")
            for i in tender.lots
            if i.numberOfBids == 0 and i.status == "active"
        ]
        numberOfBids_in_active_lots = [i.numberOfBids for i in tender.lots if i.status == "active"]
        if numberOfBids_in_active_lots and max(numberOfBids_in_active_lots) < 2:
            add_next_award(request)
        if not set([i.status for i in tender.lots]).difference(set(["unsuccessful", "cancelled"])):
            tender.status = "unsuccessful"
    else:
        if tender.numberOfBids < 2 and tender.auctionPeriod and tender.auctionPeriod.startDate:
            tender.auctionPeriod.startDate = None
        if tender.numberOfBids == 0:
            tender.status = "unsuccessful"
        if tender.numberOfBids == 1:
            add_next_award(request)


def add_next_award(request):
    add_next_award_base(request)
    process_new_defense_complaints(request)


def process_new_defense_complaints(request):
    tender = request.validated["tender"]
    first_revision_date = get_first_revision_date(tender)
    new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
    if not new_defence_complaints:
        return

    if tender.lots:
        statuses = set()
        for lot in tender.lots:
            if lot.status != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            statuses.add(lot_awards[-1].status if lot_awards else "unsuccessful")

        if statuses == set(["unsuccessful"]):
            for lot in tender.lots:
                if lot.status != "active":
                    continue
                pending_complaints = any([
                    i["status"] in tender.block_complaint_status
                    and i.relatedLot == lot.id
                    for i in tender.complaints
                ])
                lot_awards = [i for i in tender.awards if i.lotID == lot.id]
                if not lot_awards:
                    continue
                awards_no_complaint_periods = all([
                    not a.complaintPeriod
                    for a in lot_awards
                    if a["status"] == "unsuccessful"
                ])
                if (
                    not pending_complaints
                    and awards_no_complaint_periods
                ):
                    LOGGER.info(
                        "Switched lot {} of tender {} to {}".format(lot.id, tender.id, "unsuccessful"),
                        extra=context_unpack(
                            request,
                            {"MESSAGE_ID": "switched_lot_unsuccessful"},
                            {"LOT_ID": lot.id}
                        ),
                    )
                    lot.status = "unsuccessful"

            lot_statuses = set([lot.status for lot in tender.lots])
            if not lot_statuses.difference(set(["unsuccessful", "cancelled"])):
                LOGGER.info(
                    "Switched tender {} to {}".format(tender.id, "unsuccessful"),
                    extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
                )
                tender.status = "unsuccessful"

    else:
        if not tender.awards[-1].status == "pending":
            pending_complaints = any([i["status"] in tender.block_complaint_status for i in tender.complaints])
            last_award_unsuccessful = tender.awards[-1].status == "unsuccessful"
            awards_no_complaint_periods = all([
                not a.complaintPeriod
                for a in tender.awards
                if a["status"] == "unsuccessful"
            ])
            if (
                not pending_complaints
                and last_award_unsuccessful
                and awards_no_complaint_periods
            ):
                LOGGER.info(
                    "Switched tender {} to {}".format(tender.id, "unsuccessful"),
                    extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
                )
                tender.status = "unsuccessful"
