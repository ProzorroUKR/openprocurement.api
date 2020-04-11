from zope.component import getAdapter
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.api.adapters import Serializable
from openprocurement.tender.core.utils import (
    calc_auction_end_time,
    has_unanswered_questions, has_unanswered_complaints,
    extend_next_check_by_complaint_period_ends,
)

from openprocurement.api.utils import get_now


class SerializableTenderNextCheck(Serializable):
    serialized_name = "next_check"
    serialize_when_none = False

    def __call__(self, obj):
        now = get_now()
        checks = []
        configurator = getAdapter(obj, IContentConfigurator)
        if (
            obj.status == "active.tendering"
            and obj.tenderPeriod.endDate
            and not has_unanswered_complaints(obj)
            and not has_unanswered_questions(obj)
        ):
            checks.append(obj.tenderPeriod.endDate.astimezone(configurator.tz))
        elif (
            obj.status == "active.pre-qualification.stand-still"
            and obj.qualificationPeriod
            and obj.qualificationPeriod.endDate
        ):
            active_lots = [lot.id for lot in obj.lots if lot.status == "active"] if obj.lots else [None]
            if not any(
                [
                    i.status in obj.block_complaint_status
                    for q in obj.qualifications
                    for i in q.complaints
                    if q.lotID in active_lots
                ]
            ):
                checks.append(obj.qualificationPeriod.endDate.astimezone(configurator.tz))
        elif (
            not obj.lots
            and obj.status == "active.auction"
            and obj.auctionPeriod
            and obj.auctionPeriod.startDate
            and not obj.auctionPeriod.endDate
        ):
            if now < obj.auctionPeriod.startDate:
                checks.append(obj.auctionPeriod.startDate.astimezone(configurator.tz))
            elif now < calc_auction_end_time(obj.numberOfBids, obj.auctionPeriod.startDate).astimezone(configurator.tz):
                checks.append(
                    calc_auction_end_time(obj.numberOfBids, obj.auctionPeriod.startDate).astimezone(configurator.tz)
                )
        elif obj.lots and obj.status == "active.auction":
            for lot in obj.lots:
                if (
                    lot.status != "active"
                    or not lot.auctionPeriod
                    or not lot.auctionPeriod.startDate
                    or lot.auctionPeriod.endDate
                ):
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(configurator.tz))
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(
                    configurator.tz
                ):
                    checks.append(
                        calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(configurator.tz)
                    )
        elif obj.status == "active.qualification.stand-still" and obj.awardPeriod and obj.awardPeriod.endDate:
            active_lots = [lot.id for lot in obj.lots if lot.status == "active"] if obj.lots else [None]
            if not any(
                [
                    i.status in obj.block_complaint_status
                    for q in obj.qualifications
                    for i in q.complaints
                    if q.lotID in active_lots
                ]
            ):
                checks.append(obj.awardPeriod.endDate.astimezone(configurator.tz))

        extend_next_check_by_complaint_period_ends(obj, checks)

        return min(checks).isoformat() if checks else None
