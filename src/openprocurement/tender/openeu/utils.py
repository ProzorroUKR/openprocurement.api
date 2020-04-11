# -*- coding: utf-8 -*-
from logging import getLogger
from functools import partial
from cornice.resource import resource
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import error_handler, context_unpack
from openprocurement.tender.belowthreshold.utils import check_tender_status, add_contract
from openprocurement.tender.openua.utils import add_next_award, check_complaint_status
from openprocurement.tender.core.utils import (
    remove_draft_bids,
    has_unanswered_questions,
    has_unanswered_complaints,
    check_cancellation_status,
    block_tender,
    CancelTenderLot as BaseTenderLot,
    check_complaint_statuses_at_complaint_period_end,
)
from openprocurement.tender.openeu.models import Qualification
from openprocurement.tender.openeu.traversal import (
    qualifications_factory,
    bid_financial_documents_factory,
    bid_eligibility_documents_factory,
    bid_qualification_documents_factory,
)

LOGGER = getLogger(__name__)

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


class CancelTenderLot(BaseTenderLot):
    def cancel_tender(self, request):
        tender = request.validated["tender"]
        if tender.status == "active.tendering":
            tender.bids = []

        elif tender.status in ("active.pre-qualification", "active.pre-qualification.stand-still", "active.auction"):
            for bid in tender.bids:
                if bid.status in ("pending", "active"):
                    bid.status = "invalid.pre-qualification"

        tender.status = "cancelled"

    def cancel_lot(self, request, cancellation):
        tender = request.validated["tender"]
        self._cancel_lots(tender, cancellation)
        cancelled_lots, cancelled_items, cancelled_features = self._get_cancelled_lot_objects(tender)

        self._invalidate_lot_bids(tender, cancelled_lots=cancelled_lots, cancelled_features=cancelled_features)
        self._cancel_lot_qualifications(tender, cancelled_lots=cancelled_lots)
        self._lot_update_check_tender_status(request, tender)
        self._lot_update_check_next_award(request, tender)

    @staticmethod
    def _get_cancelled_lot_objects(tender):
        cancelled_lots = {i.id for i in tender.lots if i.status == "cancelled"}
        cancelled_items = {i.id for i in tender.items if i.relatedLot in cancelled_lots}
        cancelled_features = {
            i.code
            for i in (tender.features or [])
            if i.featureOf == "lot" and i.relatedItem in cancelled_lots
            or i.featureOf == "item" and i.relatedItem in cancelled_items
        }
        return cancelled_lots, cancelled_items, cancelled_features

    def _lot_update_check_next_award(self, request, tender):
        if tender.status == "active.auction" and all(
            i.auctionPeriod and i.auctionPeriod.endDate
            for i in tender.lots
            if i.status == "active"
        ):
            self.add_next_award_method(request)

    @staticmethod
    def _invalidate_lot_bids(tender, cancelled_lots, cancelled_features):
        check_statuses = (
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
        )
        if tender.status in check_statuses:
            def filter_docs(items):
                result = [i for i in items
                          if i.documentOf != "lot"
                          or i.relatedItem not in cancelled_lots]
                return result

            for bid in tender.bids:
                if tender.status == "active.tendering":
                    bid.documents = filter_docs(bid.documents)
                bid.financialDocuments = filter_docs(bid.financialDocuments)
                bid.eligibilityDocuments = filter_docs(bid.eligibilityDocuments)
                bid.qualificationDocuments = filter_docs(bid.qualificationDocuments)
                bid.parameters = [i for i in bid.parameters if i.code not in cancelled_features]
                bid.lotValues = [i for i in bid.lotValues if i.relatedLot not in cancelled_lots]
                if not bid.lotValues and bid.status in ["pending", "active"]:
                    bid.status = "invalid" if tender.status == "active.tendering" else "invalid.pre-qualification"

    @staticmethod
    def _cancel_lot_qualifications(tender, cancelled_lots):
        for qualification in tender.qualifications:
            if qualification.lotID in cancelled_lots:
                qualification.status = "cancelled"


def check_initial_bids_count(request):
    tender = request.validated["tender"]

    if tender.lots:
        [
            setattr(i.auctionPeriod, "startDate", None)
            for i in tender.lots
            if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate
        ]

        for i in tender.lots:
            if i.numberOfBids < 2 and i.status == "active":
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
    elif tender.numberOfBids < 2:
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
    else:
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
    else:
        return all([bid.status != "pending" for bid in request.validated["tender"].bids])


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()
    configurator = request.content_configurator

    check_complaint_statuses_at_complaint_period_end(tender, now)
    check_cancellation_status(request, CancelTenderLot)

    active_lots = [
        lot.id for lot in tender.lots
        if lot.status == "active"
    ] if tender.lots else [None]
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

    elif not tender.lots and tender.status == "active.awarded":
        standStillEnds = [a.complaintPeriod.endDate.astimezone(TZ) for a in tender.awards if a.complaintPeriod.endDate]
        if standStillEnds:
            standStillEnd = max(standStillEnds)
            if standStillEnd <= now:
                check_tender_status(request)
    elif tender.lots and tender.status in ["active.qualification", "active.awarded"]:
        for lot in tender.lots:
            if lot["status"] != "active":
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            standStillEnds = [a.complaintPeriod.endDate.astimezone(TZ) for a in lot_awards if a.complaintPeriod.endDate]
            if not standStillEnds:
                continue
            standStillEnd = max(standStillEnds)
            if standStillEnd <= now:
                check_tender_status(request)
                break
