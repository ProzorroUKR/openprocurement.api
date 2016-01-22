# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import (
    check_complaint_status,
    check_tender_status,
    context_unpack,
)
from datetime import timedelta

LOGGER = getLogger(__name__)
COMPLAINT_STAND_STILL_TIME = timedelta(days=10)


def check_initial_bids_count(request):
    tender = request.validated['tender']
    if tender.lots:
        [setattr(i, 'status', 'unsuccessful') for i in tender.lots if i.numberOfBids < 2]
        if set([i.status for i in tender.lots]) == set(['unsuccessful']):
            tender.status = 'unsuccessful'
    else:
        if tender.numberOfBids < 2:
            tender.status = 'unsuccessful'


def all_bids_are_reviewed(request):
    """ checks if all tender bids are reviewed
    """
    return [1 for bid in request.validated['tender'].bids if bid.status == 'active']


def check_status(request):
    tender = request.validated['tender']
    now = get_now()
    for complaint in tender.complaints:
        check_complaint_status(request, complaint, now)
    for award in tender.awards:
        for complaint in award.complaints:
            check_complaint_status(request, complaint, now)
    if not tender.lots and tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now:
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.pre-qualification'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.pre-qualification'}))
        tender.status = 'active.pre-qualification'
        check_initial_bids_count(request)
        if tender.numberOfBids < 2 and tender.auctionPeriod:
            tender.auctionPeriod.startDate = None
        return
    elif tender.lots and tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now:
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.pre-qualification'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.pre-qualification'}))
        tender.status = 'active.pre-qualification'
        check_initial_bids_count(request)
        [setattr(i.auctionPeriod, 'startDate', None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod]
        return

    elif tender.status == 'active.pre-qualification' and all_bids_are_reviewed(request):
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.pre-qualification.stand-still'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.pre-qualification.stand-still'}))
        tender.status = 'active.pre-qualification.stand-still'
        tender.qualificationPeriod.endDate = now + COMPLAINT_STAND_STILL_TIME
        return

    elif tender.status == 'active.pre-qualification-stand-still' and tender.auctionPeriod.startDate <= now:
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.auction'}))
        tender.status = 'active.auction'
        return

    elif not tender.lots and tender.status == 'active.awarded':
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in tender.awards
            if a.complaintPeriod.endDate
        ]
        if not standStillEnds:
            return
        standStillEnd = max(standStillEnds)
        if standStillEnd <= now:
            pending_complaints = any([
                i['status'] in ['claim', 'answered', 'pending']
                for i in tender.complaints
            ])
            pending_awards_complaints = any([
                i['status'] in ['claim', 'answered', 'pending']
                for a in tender.awards
                for i in a.complaints
            ])
            awarded = any([
                i['status'] == 'active'
                for i in tender.awards
            ])
            if not pending_complaints and not pending_awards_complaints and not awarded:
                LOGGER.info('Switched tender {} to {}'.format(tender.id, 'unsuccessful'),
                            extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_unsuccessful'}))
                check_tender_status(request)
                return
    elif tender.lots and tender.status in ['active.qualification', 'active.awarded']:
        if any([i['status'] in ['claim', 'answered', 'pending'] for i in tender.complaints]):
            return
        lots_ends = []
        for lot in tender.lots:
            if lot['status'] != 'active':
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in lot_awards
                if a.complaintPeriod.endDate
            ]
            if not standStillEnds:
                continue
            standStillEnd = max(standStillEnds)
            if standStillEnd <= now:
                pending_awards_complaints = any([
                    i['status'] in ['claim', 'answered', 'pending']
                    for a in lot_awards
                    for i in a.complaints
                ])
                awarded = any([
                    i['status'] == 'active'
                    for i in lot_awards
                ])
                if not pending_awards_complaints and not awarded:
                    LOGGER.info('Switched lot {} of tender {} to {}'.format(lot['id'], tender.id, 'unsuccessful'),
                                extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_unsuccessful'}, {'LOT_ID': lot['id']}))
                    check_tender_status(request)
                    return
            elif standStillEnd > now:
                lots_ends.append(standStillEnd)
        if lots_ends:
            return
