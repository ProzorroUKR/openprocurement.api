# -*- coding: utf-8 -*-
from logging import getLogger
from datetime import timedelta
from functools import partial
from cornice.resource import resource
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import (
    check_tender_status,
    error_handler,
    context_unpack,
)
from openprocurement.tender.openua.utils import BLOCK_COMPLAINT_STATUS, check_complaint_status, calculate_business_date
from openprocurement.tender.openeu.models import Qualification
from openprocurement.tender.openeu.traversal import qualifications_factory

LOGGER = getLogger(__name__)
COMPLAINT_STAND_STILL_TIME = timedelta(days=10)

qualifications_resource = partial(resource, error_handler=error_handler, factory=qualifications_factory)


def check_initial_bids_count(request):
    tender = request.validated['tender']
    if tender.lots:
        [setattr(i.auctionPeriod, 'startDate', None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate]
        [setattr(i, 'status', 'unsuccessful') for i in tender.lots if i.numberOfBids < 2]
        if set([i.status for i in tender.lots]) == set(['unsuccessful']):
            LOGGER.info('Switched tender {} to {}'.format(tender.id, 'unsuccessful'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_unsuccessful'}))
            tender.status = 'unsuccessful'
    else:
        if tender.numberOfBids < 2:
            LOGGER.info('Switched tender {} to {}'.format(tender.id, 'unsuccessful'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_unsuccessful'}))
            if tender.auctionPeriod and tender.auctionPeriod.startDate:
                tender.auctionPeriod.startDate = None
            tender.status = 'unsuccessful'


def prepare_qualifications(request, bids=[]):
    """ creates Qualification for each Bid
    """
    new_qualifications = []
    tender = request.validated['tender']
    if not bids:
        bids = tender.bids
    for bid in bids:
        if bid.status == 'pending':
            qualification = Qualification({'bidID': bid.id, 'status': 'pending'})
            tender.qualifications.append(qualification)
            new_qualifications.append(qualification.id)
    return new_qualifications


def all_bids_are_reviewed(request):
    """ checks if all tender bids are reviewed
    """
    return all([bid.status != 'pending' for bid in request.validated['tender'].bids])


def check_status(request):
    tender = request.validated['tender']
    now = get_now()
    if not tender.lots and tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and not any([i.status in BLOCK_COMPLAINT_STATUS for i in tender.complaints]):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.pre-qualification'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.pre-qualification'}))
        tender.status = 'active.pre-qualification'
        tender.qualificationPeriod = type(tender).qualificationPeriod({'startDate': now})
        check_initial_bids_count(request)
        prepare_qualifications(request)
        if tender.numberOfBids < 2 and tender.auctionPeriod:
            tender.auctionPeriod.startDate = None
        return
    elif tender.lots and tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and not any([i.status in BLOCK_COMPLAINT_STATUS for i in tender.complaints]):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.pre-qualification'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.pre-qualification'}))
        tender.status = 'active.pre-qualification'
        tender.qualificationPeriod = type(tender).qualificationPeriod({'startDate': now})
        check_initial_bids_count(request)
        prepare_qualifications(request)
        [setattr(i.auctionPeriod, 'startDate', None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod]
        return

    elif tender.status == 'active.pre-qualification' and all_bids_are_reviewed(request):
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.pre-qualification.stand-still'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.pre-qualification.stand-still'}))
        tender.status = 'active.pre-qualification.stand-still'
        tender.qualificationPeriod.endDate = calculate_business_date(now, COMPLAINT_STAND_STILL_TIME)
        return

    elif tender.status == 'active.pre-qualification.stand-still' and tender.qualificationPeriod and tender.qualificationPeriod.endDate <= now:
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
