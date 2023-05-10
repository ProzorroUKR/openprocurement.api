# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.constants import (
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
)
from openprocurement.api.utils import get_now, context_unpack, raise_operation_error
from openprocurement.tender.core.utils import (
    check_skip_award_complaint_period,
    prepare_bids_for_awarding,
    exclude_unsuccessful_awarded_bids,
)
from openprocurement.tender.core.utils import (
    get_first_revision_date,
)

LOGGER = getLogger("openprocurement.tender.belowthreshold")



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


def prepare_tender_item_for_contract(item):
    prepated_item = dict(item)
    if prepated_item.get("profile", None):
        prepated_item.pop("profile")
    return prepated_item


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
            stand_still_end = calculate_stand_still_end(tender, lot_awards, now)
            in_stand_still = now < stand_still_end
            skip_award_complaint_period = check_skip_award_complaint_period(tender)
            if (
                pending_complaints
                or pending_awards_complaints
                or (in_stand_still and not skip_award_complaint_period)
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
                if "agreements" in tender:
                    allow_complete_lot = agreements_allow_to_complete(tender.agreements)
                else:
                    contracts = [
                        contract for contract in tender.contracts
                        if contract.awardID == last_award.id
                    ]
                    allow_complete_lot = contracts_allow_to_complete(contracts)
                if allow_complete_lot:
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
        stand_still_end = calculate_stand_still_end(tender, tender.awards, now)
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

        contracts = tender.get("contracts", [])
        allow_complete_tender = contracts_allow_to_complete(contracts)
        if allow_complete_tender:
            tender.status = "complete"

    if tender.procurementMethodType == "belowThreshold":
        check_ignored_claim(tender)


def calculate_stand_still_end(tender, lot_awards, now):
    first_revision_date = get_first_revision_date(tender)
    new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < first_revision_date < NEW_DEFENSE_COMPLAINTS_TO
    stand_still_ends = [
        a.complaintPeriod.endDate
        for a in lot_awards
        if (
            a.complaintPeriod
            and a.complaintPeriod.endDate
            and (a.status != "cancelled" if new_defence_complaints else True)
        )
    ]
    return max(stand_still_ends) if stand_still_ends else now


def contracts_allow_to_complete(contracts):
    return (
        contracts
        and any([contract.status == "active" for contract in contracts])
        and not any([contract.status == "pending" for contract in contracts])
    )


def agreements_allow_to_complete(agreements):
    return any([a.status == "active" for a in agreements])
