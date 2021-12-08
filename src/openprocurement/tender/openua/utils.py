# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import get_now
from openprocurement.api.constants import TZ
from openprocurement.tender.core.utils import (
    has_unanswered_questions,
    has_unanswered_complaints,
    remove_draft_bids,
    check_cancellation_status,
    cancellation_block_tender,
    CancelTenderLot as BaseCancelTenderLot,
    check_complaint_statuses_at_complaint_period_end,
)
from openprocurement.tender.belowthreshold.utils import (
    check_tender_status, context_unpack,
    add_next_award,
)

LOGGER = getLogger("openprocurement.tender.openua")


class CancelTenderLot(BaseCancelTenderLot):

    @staticmethod
    def add_next_award_method(request):
        add_next_award(request)


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
