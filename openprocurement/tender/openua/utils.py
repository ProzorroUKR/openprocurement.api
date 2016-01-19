# -*- coding: utf-8 -*-
from pkg_resources import get_distribution
from logging import getLogger
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import (
    check_bids,
    check_tender_status,
    context_unpack,
)

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def get_invalidated_bids_data(request):
    data = request.validated['data']
    tender = request.validated['tender']
    data['bids'] = []
    for bid in tender.bids:
        if bid.status != "deleted":
            bid.status = "invalidBid"
        data['bids'].append(bid.serialize())
    return data


def calculate_buisness_date(date_obj, timedelta_obj):
    return date_obj + timedelta_obj


def check_status(request):
    tender = request.validated['tender']
    now = get_now()
    if not tender.lots and tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and not any([i.status == 'accepted' for i in tender.complaints]):
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.auction'}))
        tender.status = 'active.auction'
        check_bids(request)
        if tender.numberOfBids < 2 and tender.auctionPeriod:
            tender.auctionPeriod.startDate = None
        return
    elif tender.lots and tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and not any([i.status == 'accepted' for i in tender.complaints]):
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.auction'}))
        tender.status = 'active.auction'
        check_bids(request)
        [setattr(i.auctionPeriod, 'startDate', None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod]
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
