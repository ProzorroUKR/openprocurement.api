from logging import getLogger
from openprocurement.api.constants import TZ
from openprocurement.tender.core.utils import (
    check_complaint_statuses_at_complaint_period_end,
    context_unpack,
    get_now,
    has_unanswered_questions,
    has_unanswered_complaints,
    block_tender,
)
from openprocurement.tender.openua.utils import check_complaint_status, add_next_award, check_cancellation_status
from openprocurement.tender.belowthreshold.utils import check_tender_status, add_contract
from openprocurement.tender.core.utils import (
    calculate_tender_business_date as calculate_tender_business_date_base,
    calculate_clarif_business_date as calculate_clarif_business_date_base,
    calculate_complaint_business_date as calculate_complaint_business_date_base
)

LOGGER = getLogger("openprocurement.tender.openuadefense")


def read_json(name):
    import os.path
    from json import loads

    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, name)
    with open(file_path) as lang_file:
        data = lang_file.read()
    return loads(data)


WORKING_DAYS = read_json("data/working_days.json")


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


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()

    check_complaint_statuses_at_complaint_period_end(tender, now)
    check_cancellation_status(request)

    if block_tender(request):
        return

    for award in tender.awards:
        if award.status == "active" and not any([i.awardID == award.id for i in tender.contracts]):
            add_contract(request, award, now)
            add_next_award(request)
    if (
        not tender.lots
        and tender.status == "active.tendering"
        and tender.tenderPeriod.endDate <= now
        and not has_unanswered_complaints(tender)
        and not has_unanswered_questions(tender)
    ):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.auction"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.auction"}),
        )
        tender.status = "active.auction"
        check_bids(request)
        if tender.numberOfBids < 2 and tender.auctionPeriod:
            tender.auctionPeriod.startDate = None
        return
    elif (
        tender.lots
        and tender.status == "active.tendering"
        and tender.tenderPeriod.endDate <= now
        and not has_unanswered_complaints(tender)
        and not has_unanswered_questions(tender)
    ):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.auction"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.auction"}),
        )
        tender.status = "active.auction"
        check_bids(request)
        [setattr(i.auctionPeriod, "startDate", None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod]
        return
    elif not tender.lots and tender.status == "active.awarded":
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in tender.awards
            if a.complaintPeriod and a.complaintPeriod.endDate
        ]
        if not standStillEnds:
            return
        standStillEnd = max(standStillEnds)
        if standStillEnd <= now:
            pending_complaints = any([i["status"] in tender.block_complaint_status for i in tender.complaints])
            pending_awards_complaints = any(
                [i["status"] in tender.block_complaint_status for a in tender.awards for i in a.complaints]
            )
            awarded = any([i["status"] == "active" for i in tender.awards])
            if not pending_complaints and not pending_awards_complaints and not awarded:
                LOGGER.info(
                    "Switched tender {} to {}".format(tender.id, "unsuccessful"),
                    extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
                )
                check_tender_status(request)
                return
    elif tender.lots and tender.status in ["active.qualification", "active.awarded"]:
        if any([i["status"] in tender.block_complaint_status and i.relatedLot is None for i in tender.complaints]):
            return
        for lot in tender.lots:
            if lot["status"] != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in lot_awards
                if a.complaintPeriod and a.complaintPeriod.endDate
            ]
            if not standStillEnds:
                continue
            standStillEnd = max(standStillEnds)
            if standStillEnd <= now:
                pending_complaints = any(
                    [i["status"] in tender.block_complaint_status and i.relatedLot == lot.id for i in tender.complaints]
                )
                pending_awards_complaints = any(
                    [i["status"] in tender.block_complaint_status for a in lot_awards for i in a.complaints]
                )
                awarded = any([i["status"] == "active" for i in lot_awards])
                if not pending_complaints and not pending_awards_complaints and not awarded:
                    LOGGER.info(
                        "Switched lot {} of tender {} to {}".format(lot["id"], tender.id, "unsuccessful"),
                        extra=context_unpack(
                            request, {"MESSAGE_ID": "switched_lot_unsuccessful"}, {"LOT_ID": lot["id"]}
                        ),
                    )
                    check_tender_status(request)
