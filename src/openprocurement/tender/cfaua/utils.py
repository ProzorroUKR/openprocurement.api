# -*- coding: utf-8 -*-
from logging import getLogger
from functools import partial

from cornice.resource import resource
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.api.utils import error_handler, context_unpack, get_now
from barbecue import chef
from openprocurement.tender.core.utils import (
    remove_draft_bids,
    has_unanswered_questions,
    has_unanswered_complaints,
    calculate_tender_business_date,
    block_tender,
    check_complaint_statuses_at_complaint_period_end,
)
from openprocurement.tender.openeu.utils import CancelTenderLot as BaseCancelTenderLot
from openprocurement.tender.openua.utils import check_complaint_status
from openprocurement.tender.core.utils import (
    check_cancellation_status,
    prepare_bids_for_awarding,
    exclude_unsuccessful_awarded_bids,
)

from openprocurement.tender.cfaua.models.submodels.qualification import Qualification
from openprocurement.tender.cfaua.traversal import (
    agreement_factory,
    qualifications_factory,
    bid_financial_documents_factory,
    bid_eligibility_documents_factory,
    bid_qualification_documents_factory,
)
from zope.component import getAdapter


LOGGER = getLogger(__name__)


agreement_resource = partial(resource, error_handler=error_handler, factory=agreement_factory)
qualifications_resource = partial(resource, error_handler=error_handler, factory=qualifications_factory)
bid_financial_documents_resource = partial(
    resource, error_handler=error_handler, factory=bid_financial_documents_factory
)
bid_eligibility_documents_resource = partial(
    resource, error_handler=error_handler, factory=bid_eligibility_documents_factory
)
bid_qualification_documents_resource = partial(
    resource, error_handler=error_handler, factory=bid_qualification_documents_factory
)


class CancelTenderLot(BaseCancelTenderLot):
    def cancel_lot(self, request, cancellation):
        super(CancelTenderLot, self).cancel_lot(request, cancellation)

        # cancel agreements
        tender = request.validated["tender"]
        if tender.status == "active.awarded" and tender.agreements:
            cancelled_lots = {i.id for i in tender.lots if i.status == "cancelled"}
            for agreement in tender.agreements:
                if agreement.get_lot_id() in cancelled_lots:
                    agreement.status = "cancelled"

    def cancel_tender(self, request):

        tender = request.validated["tender"]
        if tender.status == "active.tendering":
            tender.bids = []

        elif tender.status in ("active.pre-qualification", "active.pre-qualification.stand-still", "active.auction"):
            for bid in tender.bids:
                if bid.status in ("pending", "active"):
                    bid.status = "invalid.pre-qualification"

        tender.status = "cancelled"

        for agreement in tender.agreements:
            if agreement.status in ("pending", "active"):
                agreement.status = "cancelled"


def check_initial_bids_count(request):
    tender = request.validated["tender"]

    if tender.lots:
        [
            setattr(i.auctionPeriod, "startDate", None)
            for i in tender.lots
            if i.numberOfBids < getAdapter(tender, IContentConfigurator).min_bids_number
            and i.auctionPeriod
            and i.auctionPeriod.startDate
        ]

        for i in tender.lots:
            if (
                i.numberOfBids < getAdapter(tender, IContentConfigurator).min_bids_number
                and i.status == "active"
            ):
                setattr(i, "status", "unsuccessful")
                for bid_index, bid in enumerate(tender.bids):
                    for lot_index, lot_value in enumerate(bid.lotValues):
                        if lot_value.relatedLot == i.id:
                            setattr(tender.bids[bid_index].lotValues[lot_index], "status", "unsuccessful")

        # [setattr(i, 'status', 'unsuccessful') for i in tender.lots if i.numberOfBids < 2 and i.status == 'active']

        if not set([i.status for i in tender.lots]).difference(set(["unsuccessful", "cancelled"])):
            LOGGER.info(
                "Switched tender {} to {}".format(tender.id, "unsuccessful"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            tender.status = "unsuccessful"
    elif tender.numberOfBids < getAdapter(tender, IContentConfigurator).min_bids_number:  # pragma: no cover
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "unsuccessful"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
        )
        if tender.auctionPeriod and tender.auctionPeriod.startDate:
            tender.auctionPeriod.startDate = None
        tender.status = "unsuccessful"


def prepare_qualifications(request, bids=[], lotId=None):
    """ creates Qualification for each Bid
    """
    new_qualifications = []
    tender = request.validated["tender"]
    if not bids:
        bids = tender.bids
    if tender.lots:
        active_lots = [lot.id for lot in tender.lots if lot.status == "active"]
        for bid in bids:
            if bid.status not in ["invalid", "deleted"]:
                for lotValue in bid.lotValues:
                    if lotValue.status == "pending" and lotValue.relatedLot in active_lots:
                        if lotId:
                            if lotValue.relatedLot == lotId:
                                qualification = Qualification({"bidID": bid.id, "status": "pending", "lotID": lotId})
                                qualification.date = get_now()
                                tender.qualifications.append(qualification)
                                new_qualifications.append(qualification.id)
                        else:
                            qualification = Qualification(
                                {"bidID": bid.id, "status": "pending", "lotID": lotValue.relatedLot}
                            )
                            qualification.date = get_now()
                            tender.qualifications.append(qualification)
                            new_qualifications.append(qualification.id)
    else:  # pragma: no cover
        for bid in bids:
            if bid.status == "pending":
                qualification = Qualification({"bidID": bid.id, "status": "pending"})
                qualification.date = get_now()
                tender.qualifications.append(qualification)
                new_qualifications.append(qualification.id)
    return new_qualifications


def all_bids_are_reviewed(request):
    """ checks if all tender bids are reviewed
    """
    if request.validated["tender"].lots:
        active_lots = [lot.id for lot in request.validated["tender"].lots if lot.status == "active"]
        return all(
            [
                lotValue.status != "pending"
                for bid in request.validated["tender"].bids
                if bid.status not in ["invalid", "deleted"]
                for lotValue in bid.lotValues
                if lotValue.relatedLot in active_lots
            ]
        )
    else:  # pragma: no cover
        return all([bid.status != "pending" for bid in request.validated["tender"].bids])


def check_tender_status_on_active_qualification_stand_still(request):

    tender = request.validated["tender"]
    config = getAdapter(tender, IContentConfigurator)
    now = get_now()
    active_lots = [
        lot.id for lot in tender.lots
        if lot.status == "active"
    ] if tender.lots else [None]

    if not (
        tender.awardPeriod
        and tender.awardPeriod.endDate <= now
        and not any(
            [
                i.status in tender.block_complaint_status
                for a in tender.awards
                for i in a.complaints
                if a.lotID in active_lots
            ]
        )
    ):
        return
    statuses = set()
    if tender.lots:
        for lot in tender.lots:
            if lot.status != "active":  # pragma: no cover
                statuses.add(lot.status)
                continue
            active_lot_awards = [i for i in tender.awards if i.lotID == lot.id and i.status == "active"]
            if len(active_lot_awards) < config.min_bids_number:
                LOGGER.info(
                    "Switched lot {} of tender {} to {}".format(lot.id, tender.id, "unsuccessful"),
                    extra=context_unpack(request, {"MESSAGE_ID": "switched_lot_unsuccessful"}, {"LOT_ID": lot.id}),
                )
                lot.status = "unsuccessful"
                statuses.add(lot.status)
                continue
            statuses.add(lot.status)
    else:  # pragma: no cover
        active_awards = [i for i in tender.awards if i.status == "active"]
        if len(active_awards) <= config.min_bids_count:
            statuses.add("unsuccessful")
        else:
            statuses.add("active.awarded")

    if statuses == {"cancelled"}:  # pragma: no cover
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "cancelled"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_cancelled"}),
        )
        tender.status = "cancelled"
    elif not statuses.difference({"unsuccessful", "cancelled"}):  # pragma: no cover
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "unsuccessful"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
        )
        tender.status = "unsuccessful"
    else:
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "active.awarded"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active_awarded"}),
        )
        tender.status = "active.awarded"
        clarif_date = calculate_tender_business_date(now, config.clarifications_until_period, tender, False)
        tender.contractPeriod = {
            "startDate": now,
            "clarificationsUntil": clarif_date
        }
        lots = [l for l in tender.get("lots", []) if l.status == "active"]
        if lots:
            for lot in lots:
                agreement_data = generate_agreement_data(request, tender, lot)
                agreement = type(tender).agreements.model_class(agreement_data)
                agreement.__parent__ = tender
                tender.agreements.append(agreement)
        else:  # pragma: no cover
            agreement_data = generate_agreement_data(request, tender)
            agreement = type(tender).agreements.model_class(agreement_data)
            agreement.__parent__ = tender
            tender.agreements.append(agreement)

        # Update tender status (awarded, unsuccessful)


def check_tender_status_on_active_awarded(request):
    tender = request.validated["tender"]
    now = get_now()
    statuses = {agreement.status for agreement in tender.agreements}
    if statuses == {"cancelled"}:
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "cancelled"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_cancelled"}),
        )
        tender.status = "cancelled"
    elif not statuses.difference({"unsuccessful", "cancelled"}):
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "unsuccessful"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
        )
        tender.status = "unsuccessful"
    elif not statuses.difference({"active", "unsuccessful", "cancelled"}):
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "complete"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_complete"}),
        )
        tender.status = "complete"
        tender.contractPeriod.endDate = now


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()

    check_complaint_statuses_at_complaint_period_end(tender, now)
    check_cancellation_status(request, CancelTenderLot)

    active_lots = [
        lot.id
        for lot in tender.lots if lot.status == "active"
    ] if tender.lots else [None]

    if block_tender(request):
        return

    if (
        tender.status == "active.tendering"
        and tender.tenderPeriod.endDate <= now
        and not has_unanswered_complaints(tender)
        and not has_unanswered_questions(tender)
    ):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.pre-qualification"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.pre-qualification"}),
        )
        tender.status = "active.pre-qualification"
        tender.qualificationPeriod = type(tender).qualificationPeriod({"startDate": now})
        remove_draft_bids(request)
        check_initial_bids_count(request)
        prepare_qualifications(request)
        return

    elif (
        tender.status == "active.pre-qualification.stand-still"
        and tender.qualificationPeriod
        and tender.qualificationPeriod.endDate <= now
        and not any(
            [
                i.status in tender.block_complaint_status
                for q in tender.qualifications
                for i in q.complaints
                if q.lotID in active_lots
            ]
        )
    ):
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.auction"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.auction"}),
        )
        tender.status = "active.auction"
        check_initial_bids_count(request)
        return
    elif tender.status == "active.qualification.stand-still":
        check_tender_status_on_active_qualification_stand_still(request)


def add_next_awards(request, reverse=False, awarding_criteria_key="amount", regenerate_all_awards=False, lot_id=None):

    """Adding next award.
    :param request:
        The pyramid request object.
    :param reverse:
        Is used for sorting bids to generate award.
        By default (reverse = False) awards are generated from lower to higher by value.amount
        When reverse is set to True awards are generated from higher to lower by value.amount
    """
    tender = request.validated["tender"]
    max_awards = tender["maxAwardsCount"]
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
            lot_awards = [award for award in tender.awards if award.lotID == lot.id]
            lot_awards_statuses = {award["status"] for award in tender.awards if award.lotID == lot.id}
            if lot_awards_statuses and lot_awards_statuses.issubset({"pending", "active"}):
                statuses.union(lot_awards_statuses)
                continue

            all_bids = prepare_bids_for_awarding(tender, tender.bids, lot_id=lot.id)
            if not all_bids:
                lot.status = "unsuccessful"
                statuses.add("unsuccessful")
                continue

            selected_bids = exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=lot.id)

            if not regenerate_all_awards and lot.id == lot_id:
                # this block seems is supposed to cause the function append only one award
                # for a bid of the first (the only?) cancelled award
                cancelled_award_bid_ids = [
                    award.bid_id for award in lot_awards
                    if award.status == "cancelled" and request.context.id == award.id
                ]
                if cancelled_award_bid_ids:
                    selected_bids = [bid for bid in all_bids if bid["id"] == cancelled_award_bid_ids[0]]

            if max_awards:  # limit awards
                selected_bids = selected_bids[:max_awards]

            active_award_bid_ids = {a.bid_id for a in lot_awards if a.status in ("active", "pending")}
            selected_bids = list(filter(lambda b: b["id"] not in active_award_bid_ids, selected_bids))
            if selected_bids:
                for bid in selected_bids:
                    tender.append_award(bid, all_bids, lot_id=lot.id)
                statuses.add("pending")
            else:
                statuses.add("unsuccessful")
        if (
            statuses.difference({"unsuccessful", "active"})
            and any([i for i in tender.lots])
        ):
            # logic for auction to switch status
            tender.awardPeriod.endDate = None
            tender.status = "active.qualification"
    else:  # pragma: no cover
        if not tender.awards or request.context.status in ("cancelled", "unsuccessful"):
            codes = [i.code for i in tender.features or []]
            active_bids = [
                {
                    "id": bid.id,
                    "value": bid.value.serialize(),
                    "tenderers": bid.tenderers,
                    "parameters": [i for i in bid.parameters if i.code in codes],
                    "date": bid.date,
                }
                for bid in tender.bids
                if bid.status == "active"
            ]
            cancelled_awards = None
            if not regenerate_all_awards:
                cancelled_awards = [
                    award.bid_id
                    for award in tender.awards
                    if award.status == "cancelled" and request.context.id == award.id
                ]
            unsuccessful_awards = [i.bid_id for i in tender.awards if i.status == "unsuccessful"]
            bids = chef(active_bids, tender.features or [], unsuccessful_awards, reverse, awarding_criteria_key)
            bids = [bid for bid in bids if bid["id"] == cancelled_awards[0]] if cancelled_awards else bids
            bids = bids[:max_awards] if max_awards else bids
            active_awards = [a.bid_id for a in tender.awards if a.status in ("active", "pending")]
            bids = [bid for bid in bids if bid["id"] not in active_awards]
            if bids:
                for bid in bids:
                    award = tender.__class__.awards.model_class(
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
        if tender.awards[-1].status == "pending":  # logic for auction to switch status
            tender.awardPeriod.endDate = None
            tender.status = "active.qualification"


def all_awards_are_reviewed(request):
    """ checks if all tender awards are reviewed
    """
    return all([award.status != "pending" for award in request.validated["tender"].awards])


def generate_agreement_data(request, tender, lot=None):
    data = {
        "items": tender.items if not lot else [i for i in tender.items if i.relatedLot == lot.id],
        "agreementID": "{}-{}{}".format(tender.tenderID, request.registry.server_id, len(tender.agreements) + 1),
        "date": get_now().isoformat(),
        "contracts": [],
        "features": tender.features,
    }
    unit_prices = [
        {
            "relatedItem": item.id,
            "value": {"currency": tender.value.currency, "valueAddedTaxIncluded": tender.value.valueAddedTaxIncluded},
        }
        for item in data["items"]
    ]
    for award in tender.awards:
        if lot and lot.id != award.lotID:
            continue
        if award.status != "active":
            continue
        data["contracts"].append(
            {
                "suppliers": award.suppliers,
                "awardID": award.id,
                "bidID": award.bid_id,
                "date": get_now().isoformat(),
                "unitPrices": unit_prices,
                "parameters": [b for b in tender.bids if b.id == award.bid_id][0].parameters,
            }
        )
    return data
