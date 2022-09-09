# -*- coding: utf-8 -*-
from logging import getLogger
from functools import partial
from cornice.resource import resource
from openprocurement.api.utils import error_handler, context_unpack, get_now, TZ
from openprocurement.tender.belowthreshold.utils import check_tender_status
from openprocurement.tender.openua.utils import add_next_award, check_complaint_status
from openprocurement.tender.core.utils import (
    remove_draft_bids,
    has_unanswered_questions,
    has_unanswered_complaints,
    check_cancellation_status,
    cancellation_block_tender,
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
    @staticmethod
    def add_next_award_method(request):
        raise NotImplementedError

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
            for bid in tender.bids:
                bid.parameters = [i for i in bid.parameters if i.code not in cancelled_features]
                bid.lotValues = [i for i in bid.lotValues if i.relatedLot not in cancelled_lots]
                if not bid.lotValues and bid.status in ["pending", "active"]:
                    bid.status = "invalid" if tender.status == "active.tendering" else "invalid.pre-qualification"


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


def is_procedure_restricted(tender):
    return tender.get("preQualificationFeaturesRatingBidLimit") and tender.get("preQualificationMinBidsNumber")
