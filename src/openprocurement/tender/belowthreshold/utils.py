# -*- coding: utf-8 -*-
from barbecue import chef
from logging import getLogger
from openprocurement.api.constants import TZ, RELEASE_2020_04_19
from openprocurement.api.utils import get_now, context_unpack
from openprocurement.tender.core.constants import COMPLAINT_STAND_STILL_TIME
from openprocurement.tender.core.utils import (
    calculate_tender_business_date,
    cleanup_bids_for_cancelled_lots,
    remove_draft_bids,
    calculate_tender_date,
    check_skip_award_complaint_period,
)
from openprocurement.tender.core.constants import COMPLAINT_STAND_STILL_TIME
from openprocurement.tender.core.utils import (
    check_cancellation_status,
    get_first_revision_date,
    CancelTenderLot as BaseCancelTenderLot
)

LOGGER = getLogger("openprocurement.tender.belowthreshold")


class CancelTenderLot(BaseCancelTenderLot):
    def add_next_award_method(request):
        return add_next_award(request)


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
        cleanup_bids_for_cancelled_lots(tender)
        if not set([i.status for i in tender.lots]).difference(set(["unsuccessful", "cancelled"])):
            tender.status = "unsuccessful"
        elif max([i.numberOfBids for i in tender.lots if i.status == "active"]) < 2:
            add_next_award(request)
    else:
        if tender.numberOfBids < 2 and tender.auctionPeriod and tender.auctionPeriod.startDate:
            tender.auctionPeriod.startDate = None
        if tender.numberOfBids == 0:
            tender.status = "unsuccessful"
        if tender.numberOfBids == 1:
            add_next_award(request)
    check_ignored_claim(tender)


def check_complaint_status(request, complaint, now=None):
    if not now:
        now = get_now()
    if complaint.status == "answered":
        date = calculate_tender_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, request.tender)
        if date < now:
            complaint.status = complaint.resolutionType
    elif complaint.status == "pending" and complaint.resolutionType and complaint.dateEscalated:
        complaint.status = complaint.resolutionType
    elif complaint.status == "pending":
        complaint.status = "ignored"


def check_ignored_claim(tender):
    complete_lot_ids = [None] if tender.status in ["complete", "cancelled", "unsuccessful"] else []
    complete_lot_ids.extend([i.id for i in tender.lots if i.status in ["complete", "cancelled", "unsuccessful"]])
    for complaint in tender.complaints:
        if complaint.status == "claim" and complaint.relatedLot in complete_lot_ids:
            complaint.status = "ignored"
    for award in tender.awards:
        for complaint in award.complaints:
            if complaint.status == "claim" and complaint.relatedLot in complete_lot_ids:
                complaint.status = "ignored"


def add_contract(request, award, now=None):
    tender = request.validated["tender"]
    tender.contracts.append(
        type(tender).contracts.model_class(
            {
                "awardID": award.id,
                "suppliers": award.suppliers,
                "value": generate_contract_value(tender, award),
                "date": now or get_now(),
                "items": [i for i in tender.items if not hasattr(award, "lotID") or i.relatedLot == award.lotID],
                "contractID": "{}-{}{}".format(tender.tenderID, request.registry.server_id, len(tender.contracts) + 1),
            }
        )
    )


def generate_contract_value(tender, award):
    if award.value:
        value = type(tender).contracts.model_class.value.model_class(dict(award.value.items()))
        value.amountNet = award.value.amount
        return value
    return None


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()

    for complaint in tender.complaints:
        check_complaint_status(request, complaint, now)
    for award in tender.awards:
        if award.status == "active" and not any([i.awardID == award.id for i in tender.contracts]):
            add_contract(request, award, now)
            add_next_award(request)
        for complaint in award.complaints:
            check_complaint_status(request, complaint, now)
    if (
        tender.status == "active.enquiries"
        and not tender.tenderPeriod.startDate
        and tender.enquiryPeriod.endDate.astimezone(TZ) <= now
    ):
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "active.tendering"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.tendering"}),
        )
        tender.status = "active.tendering"
        return
    elif (
        tender.status == "active.enquiries"
        and tender.tenderPeriod.startDate
        and tender.tenderPeriod.startDate.astimezone(TZ) <= now
    ):
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "active.tendering"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.tendering"}),
        )
        tender.status = "active.tendering"
        return
    elif not tender.lots and tender.status == "active.tendering" and tender.tenderPeriod.endDate <= now:
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.auction"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.auction"}),
        )
        tender.status = "active.auction"
        remove_draft_bids(request)
        check_bids(request)
        if tender.numberOfBids < 2 and tender.auctionPeriod:
            tender.auctionPeriod.startDate = None
        return
    elif (
            tender.lots
            and tender.status == "active.tendering"
            and tender.tenderPeriod.endDate <= now
    ):
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.auction"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.auction"}),
        )
        tender.status = "active.auction"
        remove_draft_bids(request)
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
            check_tender_status(request)
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
                check_tender_status(request)
                return


def check_tender_status(request):
    tender = request.validated["tender"]
    now = get_now()

    if tender.lots:
        if any([i.status in tender.block_complaint_status and i.relatedLot is None for i in tender.complaints]):
            return
        for lot in tender.lots:
            if lot.status != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            pending_complaints = any(
                [i["status"] in tender.block_complaint_status and i.relatedLot == lot.id for i in tender.complaints]
            )
            pending_awards_complaints = any(
                [i.status in tender.block_complaint_status for a in lot_awards for i in a.complaints]
            )
            stand_still_end = max([
                a.complaintPeriod.endDate
                if a.complaintPeriod and a.complaintPeriod.endDate else now
                for a in lot_awards
            ])
            skip_award_complaint_period = check_skip_award_complaint_period(tender)
            if (
                    pending_complaints
                    or pending_awards_complaints
                    or (not stand_still_end <= now and not skip_award_complaint_period)
            ):
                continue
            elif last_award.status == "unsuccessful":
                LOGGER.info(
                    "Switched lot {} of tender {} to {}".format(lot.id, tender.id, "unsuccessful"),
                    extra=context_unpack(request, {"MESSAGE_ID": "switched_lot_unsuccessful"}, {"LOT_ID": lot.id}),
                )
                lot.status = "unsuccessful"
                continue
            elif last_award.status == "active":
                active_contracts = (
                    [a.status == "active" for a in tender.agreements]
                    if "agreements" in tender
                    else [i.status == "active" and i.awardID == last_award.id for i in tender.contracts]
                )

                if any(active_contracts):
                    LOGGER.info(
                        "Switched lot {} of tender {} to {}".format(lot.id, tender.id, "complete"),
                        extra=context_unpack(request, {"MESSAGE_ID": "switched_lot_complete"}, {"LOT_ID": lot.id}),
                    )
                    lot.status = "complete"

        statuses = set([lot.status for lot in tender.lots])
        if statuses == set(["cancelled"]):
            LOGGER.info(
                "Switched tender {} to {}".format(tender.id, "cancelled"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_cancelled"}),
            )
            tender.status = "cancelled"
        elif not statuses.difference(set(["unsuccessful", "cancelled"])):
            LOGGER.info(
                "Switched tender {} to {}".format(tender.id, "unsuccessful"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            tender.status = "unsuccessful"
        elif not statuses.difference(set(["complete", "unsuccessful", "cancelled"])):
            LOGGER.info(
                "Switched tender {} to {}".format(tender.id, "complete"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_complete"}),
            )
            tender.status = "complete"
    else:
        pending_complaints = any([i.status in tender.block_complaint_status for i in tender.complaints])
        pending_awards_complaints = any(
            [i.status in tender.block_complaint_status for a in tender.awards for i in a.complaints]
        )
        stand_still_ends = [
            a.complaintPeriod.endDate
            for a in tender.awards
            if a.complaintPeriod and a.complaintPeriod.endDate
        ]
        stand_still_end = max(stand_still_ends) if stand_still_ends else now
        stand_still_time_expired = stand_still_end < now
        last_award_status = tender.awards[-1].status if tender.awards else ""
        if (
            not pending_complaints
            and not pending_awards_complaints
            and stand_still_time_expired
            and last_award_status == "unsuccessful"
        ):
            LOGGER.info(
                "Switched tender {} to {}".format(tender.id, "unsuccessful"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            tender.status = "unsuccessful"

        contracts = (
                tender.agreements[-1].get("contracts")
                if tender.get("agreements")
                else tender.get("contracts", [])
        )
        if contracts and contracts[-1].status == "active":
            tender.status = "complete"
    if tender.procurementMethodType == "belowThreshold":
        check_ignored_claim(tender)


def add_next_award(request):
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
            lot_items = [i.id for i in tender.items if i.relatedLot == lot.id]
            features = [
                i
                for i in (tender.features or [])
                if i.featureOf == "tenderer"
                or i.featureOf == "lot"
                and i.relatedItem == lot.id
                or i.featureOf == "item"
                and i.relatedItem in lot_items
            ]
            codes = [i.code for i in features]
            bids = [
                {
                    "id": bid.id,
                    "value": [i for i in bid.lotValues if lot.id == i.relatedLot][0].value,
                    "tenderers": bid.tenderers,
                    "parameters": [i for i in bid.parameters if i.code in codes],
                    "date": [i for i in bid.lotValues if lot.id == i.relatedLot][0].date,
                }
                for bid in tender.bids
                if lot.id in [i.relatedLot for i in bid.lotValues]
            ]
            if not bids:
                lot.status = "unsuccessful"
                statuses.add("unsuccessful")
                continue
            unsuccessful_awards = [i.bid_id for i in lot_awards if i.status == "unsuccessful"]
            bids = chef(bids, features, unsuccessful_awards)
            if bids:
                bid = bids[0]
                award = type(tender).awards.model_class(
                    {
                        "bid_id": bid["id"],
                        "lotID": lot.id,
                        "status": "pending",
                        "value": bid["value"],
                        "date": get_now(),
                        "suppliers": bid["tenderers"],
                    }
                )
                award.__parent__ = tender
                tender.awards.append(award)
                request.response.headers["Location"] = request.route_url(
                    "{}:Tender Awards".format(tender.procurementMethodType), tender_id=tender.id, award_id=award["id"]
                )
                statuses.add("pending")
            else:
                statuses.add("unsuccessful")
        if statuses.difference(set(["unsuccessful", "active"])):
            tender.awardPeriod.endDate = None
            tender.status = "active.qualification"
        else:
            tender.awardPeriod.endDate = now
            tender.status = "active.awarded"
    else:
        if not tender.awards or tender.awards[-1].status not in ["pending", "active"]:
            unsuccessful_awards = [i.bid_id for i in tender.awards if i.status == "unsuccessful"]
            bids = chef(tender.bids, tender.features or [], unsuccessful_awards)
            if bids:
                bid = bids[0].serialize()
                award = type(tender).awards.model_class(
                    {
                        "bid_id": bid["id"],
                        "status": "pending",
                        "date": get_now(),
                        "value": bid["value"],
                        "suppliers": bid["tenderers"],

                    }
                )
                award.__parent__ = tender
                tender.awards.append(award)
                request.response.headers["Location"] = request.route_url(
                    "{}:Tender Awards".format(tender.procurementMethodType), tender_id=tender.id, award_id=award["id"]
                )
        if tender.awards[-1].status == "pending":
            tender.awardPeriod.endDate = None
            tender.status = "active.qualification"
        else:
            tender.awardPeriod.endDate = now
            tender.status = "active.awarded"
