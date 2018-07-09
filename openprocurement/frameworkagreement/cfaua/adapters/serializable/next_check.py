from zope.component import getAdapter
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.api.adapters import Serializable
from openprocurement.tender.core.utils import (
    calc_auction_end_time,
    has_unanswered_questions,
    has_unanswered_complaints,
)

from openprocurement.api.utils import get_now


class SerializableTenderNextCheck(Serializable):
    serialized_name = "next_check"
    serialize_when_none = False

    def __call__(self, obj):
        now = get_now()
        checks = []
        configurator = getAdapter(obj, IContentConfigurator)
        if obj.status == 'active.tendering' and obj.tenderPeriod.endDate and \
                not has_unanswered_complaints(obj) and not has_unanswered_questions(obj):
            checks.append(obj.tenderPeriod.endDate.astimezone(configurator.tz))
        elif obj.status == 'active.pre-qualification.stand-still' and obj.qualificationPeriod and obj.qualificationPeriod.endDate:
            active_lots = [lot.id for lot in obj.lots if lot.status == 'active'] if obj.lots else [None]
            if not any([
                        i.status in obj.block_complaint_status
                for q in obj.qualifications
                for i in q.complaints
                if q.lotID in active_lots
            ]):
                checks.append(obj.qualificationPeriod.endDate.astimezone(configurator.tz))
        elif not obj.lots and obj.status == 'active.auction' and obj.auctionPeriod and obj.auctionPeriod.startDate and not obj.auctionPeriod.endDate:
            if now < obj.auctionPeriod.startDate:
                checks.append(obj.auctionPeriod.startDate.astimezone(configurator.tz))
            elif now < calc_auction_end_time(obj.numberOfBids, obj.auctionPeriod.startDate).astimezone(configurator.tz):
                checks.append(calc_auction_end_time(obj.numberOfBids, obj.auctionPeriod.startDate).astimezone(configurator.tz))
        elif obj.lots and obj.status == 'active.auction':
            for lot in obj.lots:
                if lot.status != 'active' or not lot.auctionPeriod or not lot.auctionPeriod.startDate or lot.auctionPeriod.endDate:
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(configurator.tz))
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(configurator.tz):
                    checks.append(calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(configurator.tz))
        elif not obj.lots and obj.status == 'active.awarded' and not any([
                    i.status in obj.block_complaint_status
            for i in obj.complaints
        ]) and not any([
                    i.status in obj.block_complaint_status
            for a in obj.awards
            for i in a.complaints
        ]):
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(configurator.tz)
                for a in obj.awards
                if a.complaintPeriod.endDate
            ]
            last_award_status = obj.awards[-1].status if obj.awards else ''
            if standStillEnds and last_award_status == 'unsuccessful':
                checks.append(max(standStillEnds))
        elif obj.lots and obj.status in ['active.qualification', 'active.awarded'] and not any([
                            i.status in obj.block_complaint_status and i.relatedLot is None
            for i in obj.complaints
        ]):
            for lot in obj.lots:
                if lot['status'] != 'active':
                    continue
                lot_awards = [i for i in obj.awards if i.lotID == lot.id]
                pending_complaints = any([
                    i['status'] in obj.block_complaint_status and i.relatedLot == lot.id
                    for i in obj.complaints
                ])
                pending_awards_complaints = any([
                    i.status in obj.block_complaint_status
                    for a in lot_awards
                    for i in a.complaints
                ])
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(configurator.tz)
                    for a in lot_awards
                    if a.complaintPeriod.endDate
                ]
                last_award_status = lot_awards[-1].status if lot_awards else ''
                if not pending_complaints and not pending_awards_complaints and standStillEnds and last_award_status == 'unsuccessful':
                    checks.append(max(standStillEnds))
        if obj.status.startswith('active'):
            for award in obj.awards:
                if award.status == 'active' and not any([i.awardID == award.id for i in obj.contracts]):
                    checks.append(award.date)
        return min(checks).isoformat() if checks else None
