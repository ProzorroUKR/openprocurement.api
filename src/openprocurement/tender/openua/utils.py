# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import get_now
from openprocurement.api.constants import TZ
from openprocurement.tender.core.utils import (
    has_unanswered_questions,
    has_unanswered_complaints,
    remove_draft_bids,
    check_cancellation_status,
    block_tender,
    CancelTenderLot as BaseCancelTenderLot,
    check_complaint_statuses_at_complaint_period_end,
    prepare_bids_for_awarding,
    exclude_unsuccessful_awarded_bids,
)
from openprocurement.tender.belowthreshold.utils import check_tender_status, context_unpack, add_contract

LOGGER = getLogger("openprocurement.tender.openua")


class CancelTenderLot(BaseCancelTenderLot):

    @staticmethod
    def add_next_award_method(request):
        configurator = request.content_configurator
        add_next_award(
            request,
            reverse=configurator.reverse_awarding_criteria,
            awarding_criteria_key=configurator.awarding_criteria_key,
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
            if i.numberOfBids < 2 and i.status == "active"
        ]

        if not set([i.status for i in tender.lots]).difference(set(["unsuccessful", "cancelled"])):
            tender.status = "unsuccessful"
    elif tender.numberOfBids <2:
        if tender.auctionPeriod and tender.auctionPeriod.startDate:
            tender.auctionPeriod.startDate = None
        tender.status = "unsuccessful"


def check_complaint_status(request, complaint):
    if complaint.status == "answered":
        complaint.status = complaint.resolutionType


def check_status(request):
    tender = request.validated["tender"]

    now = get_now()
    configurator = request.content_configurator

    check_complaint_statuses_at_complaint_period_end(tender, now)
    check_cancellation_status(request, cancel_class=CancelTenderLot)

    for award in tender.awards:
        if award.status == "active" and not any([i.awardID == award.id for i in tender.contracts]):
            add_contract(request, award, now)
            add_next_award(
                request,
                reverse=configurator.reverse_awarding_criteria,
                awarding_criteria_key=configurator.awarding_criteria_key,
            )

    if block_tender(request):
        return

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
        remove_draft_bids(request)
        check_bids(request)
        if tender.numberOfBids < 2 and tender.auctionPeriod:
            tender.auctionPeriod.startDate = None
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
        remove_draft_bids(request)
        check_bids(request)
        [setattr(i.auctionPeriod, "startDate", None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod]

    elif not tender.lots and tender.status == "active.awarded":
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in tender.awards
            if a.complaintPeriod and a.complaintPeriod.endDate
        ]
        if standStillEnds:
            standStillEnd = max(standStillEnds)
            if standStillEnd <= now:
                check_tender_status(request)
    elif tender.lots and tender.status in ["active.qualification", "active.awarded"]:
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
                check_tender_status(request)
                break


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
