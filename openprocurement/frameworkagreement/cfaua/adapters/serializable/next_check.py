from openprocurement.api.interfaces import IContentConfigurator
from zope.component import getAdapter
from openprocurement.tender.core.utils import (
    calc_auction_end_time,
    has_unanswered_questions,
    has_unanswered_complaints,
)

from openprocurement.api.utils import get_now
from openprocurement.api.constants import TZ

class SerializableTenderNextCheck(object):
    def __init__(self, tender):
        self.context = tender
        self.configurator = getAdapter(tender, IContentConfigurator)

    def __call__(self, *args, **kwargs):
        now = get_now()
        checks = []
        if self.context.status == 'active.tendering' and self.context.tenderPeriod.endDate and \
                not has_unanswered_complaints(self.context) and not has_unanswered_questions(self.context):
            checks.append(self.context.tenderPeriod.endDate.astimezone(TZ))
        elif self.context.status == 'active.pre-qualification.stand-still' and self.context.qualificationPeriod and self.context.qualificationPeriod.endDate:
            active_lots = [lot.id for lot in self.context.lots if lot.status == 'active'] if self.context.lots else [None]
            if not any([
                        i.status in self.context.block_complaint_status
                for q in self.context.qualifications
                for i in q.complaints
                if q.lotID in active_lots
            ]):
                checks.append(self.context.qualificationPeriod.endDate.astimezone(TZ))
        elif not self.context.lots and self.context.status == 'active.auction' and self.context.auctionPeriod and self.context.auctionPeriod.startDate and not self.context.auctionPeriod.endDate:
            if now < self.context.auctionPeriod.startDate:
                checks.append(self.context.auctionPeriod.startDate.astimezone(TZ))
            elif now < calc_auction_end_time(self.context.numberOfBids, self.context.auctionPeriod.startDate).astimezone(TZ):
                checks.append(calc_auction_end_time(self.context.numberOfBids, self.context.auctionPeriod.startDate).astimezone(TZ))
        elif self.context.lots and self.context.status == 'active.auction':
            for lot in self.context.lots:
                if lot.status != 'active' or not lot.auctionPeriod or not lot.auctionPeriod.startDate or lot.auctionPeriod.endDate:
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(TZ))
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ):
                    checks.append(calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ))
        elif not self.context.lots and self.context.status == 'active.awarded' and not any([
                    i.status in self.context.block_complaint_status
            for i in self.context.complaints
        ]) and not any([
                    i.status in self.context.block_complaint_status
            for a in self.context.awards
            for i in a.complaints
        ]):
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.context.awards
                if a.complaintPeriod.endDate
            ]
            last_award_status = self.context.awards[-1].status if self.context.awards else ''
            if standStillEnds and last_award_status == 'unsuccessful':
                checks.append(max(standStillEnds))
        elif self.context.lots and self.context.status in ['active.qualification', 'active.awarded'] and not any([
                            i.status in self.context.block_complaint_status and i.relatedLot is None
            for i in self.context.complaints
        ]):
            for lot in self.context.lots:
                if lot['status'] != 'active':
                    continue
                lot_awards = [i for i in self.context.awards if i.lotID == lot.id]
                pending_complaints = any([
                    i['status'] in self.context.block_complaint_status and i.relatedLot == lot.id
                    for i in self.context.complaints
                ])
                pending_awards_complaints = any([
                    i.status in self.context.block_complaint_status
                    for a in lot_awards
                    for i in a.complaints
                ])
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(TZ)
                    for a in lot_awards
                    if a.complaintPeriod.endDate
                ]
                last_award_status = lot_awards[-1].status if lot_awards else ''
                if not pending_complaints and not pending_awards_complaints and standStillEnds and last_award_status == 'unsuccessful':
                    checks.append(max(standStillEnds))
        if self.context.status.startswith('active'):
            for award in self.context.awards:
                if award.status == 'active' and not any([i.awardID == award.id for i in self.context.contracts]):
                    checks.append(award.date)

        return min(checks).isoformat() if checks else None
