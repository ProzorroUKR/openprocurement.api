from logging import getLogger
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.constants import TZ, NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO
from openprocurement.tender.core.utils import (
    check_complaint_statuses_at_complaint_period_end,
    context_unpack,
    get_now,
    has_unanswered_questions,
    has_unanswered_complaints,
    cancellation_block_tender,
    prepare_bids_for_awarding,
    exclude_unsuccessful_awarded_bids,
)
from openprocurement.tender.openua.utils import check_complaint_status, add_next_award, check_cancellation_status
from openprocurement.tender.belowthreshold.utils import check_tender_status, add_contract
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


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()

    check_complaint_statuses_at_complaint_period_end(tender, now)
    check_cancellation_status(request)

    if cancellation_block_tender(tender):
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
        first_revision_date = get_first_revision_date(tender)
        new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in tender.awards
            if (
                    a.complaintPeriod
                    and a.complaintPeriod.endDate
                    and (a.status != "cancelled" if new_defence_complaints else True)
            )
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
        first_revision_date = get_first_revision_date(tender)
        new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
        for lot in tender.lots:
            if lot["status"] != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in lot_awards
                if (
                        a.complaintPeriod
                        and a.complaintPeriod.endDate
                        and (a.status != "cancelled" if new_defence_complaints else True)
                )
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


def add_next_award(request, reverse=False, awarding_criteria_key="amount"):
    """Adding next award.
    reverse and awarding_criteria_key are deprecated, since we can get them from request
    :param request:
        The pyramid request object.
    :param reverse:
        Is used for sorting bids to generate award.
        By default (reverse = False) awards are generated from lower to higher by value.amount
        When reverse is set to True awards are generated from higher to lower by value.amount
    """
    tender = request.validated["tender"]
    now = get_now()
    if not tender.awardPeriod:
        tender.awardPeriod = type(tender).awardPeriod({})
    if not tender.awardPeriod.startDate:
        tender.awardPeriod.startDate = now
    if tender.lots:
        statuses = set()
        for lot in tender.lots:
            if lot.status != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            if lot_awards and lot_awards[-1].status in ["pending", "active"]:
                statuses.add(lot_awards[-1].status if lot_awards else "unsuccessful")
                continue
            all_bids = prepare_bids_for_awarding(tender, tender.bids, lot_id=lot.id)
            if all_bids:
                bids = exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=lot.id)
                if bids:
                    tender.append_award(bids[0], all_bids, lot_id=lot.id)
                    request.response.headers["Location"] = request.route_url(
                        "{}:Tender Awards".format(tender.procurementMethodType),
                        tender_id=tender.id,
                        award_id=tender.awards[-1]["id"]
                    )
                    statuses.add("pending")
                else:
                    statuses.add("unsuccessful")
            else:
                lot.status = "unsuccessful"
                statuses.add("unsuccessful")

        if statuses.difference(set(["unsuccessful", "active"])):
            tender.awardPeriod.endDate = None
            tender.status = "active.qualification"
        else:
            tender.awardPeriod.endDate = now
            tender.status = "active.awarded"

            first_revision_date = get_first_revision_date(tender)
            new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
            if new_defence_complaints and statuses == set(["unsuccessful"]):
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
        if not tender.awards or tender.awards[-1].status not in ["pending", "active"]:
            all_bids = prepare_bids_for_awarding(tender, tender.bids, lot_id=None)
            bids = exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=None)
            if bids:
                tender.append_award(bids[0], all_bids)
                request.response.headers["Location"] = request.route_url(
                    "{}:Tender Awards".format(tender.procurementMethodType),
                    tender_id=tender.id,
                    award_id=tender.awards[-1]["id"]
                )
        if tender.awards[-1].status == "pending":
            tender.awardPeriod.endDate = None
            tender.status = "active.qualification"
        else:
            tender.awardPeriod.endDate = now
            tender.status = "active.awarded"

            first_revision_date = get_first_revision_date(tender)
            new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
            if new_defence_complaints:
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
