# -*- coding: utf-8 -*-
from logging import getLogger
from functools import partial
from cornice.resource import resource
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import (
    check_tender_status,
    error_handler,
    context_unpack,
    remove_draft_bids
)
from openprocurement.tender.openua.utils import check_complaint_status
from openprocurement.tender.openeu.models import Qualification
from openprocurement.tender.openeu.traversal import (
    qualifications_factory, bid_financial_documents_factory,
    bid_eligibility_documents_factory, bid_qualification_documents_factory)
from barbecue import chef

LOGGER = getLogger(__name__)

qualifications_resource = partial(resource, error_handler=error_handler, factory=qualifications_factory)
bid_financial_documents_resource = partial(resource, error_handler=error_handler, factory=bid_financial_documents_factory)
bid_eligibility_documents_resource = partial(resource, error_handler=error_handler, factory=bid_eligibility_documents_factory)
bid_qualification_documents_resource = partial(resource, error_handler=error_handler, factory=bid_qualification_documents_factory)


def check_initial_bids_count(request):
    tender = request.validated['tender']
    if tender.lots:
        [setattr(i.auctionPeriod, 'startDate', None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate]

        for i in tender.lots:
            if i.numberOfBids < 2 and i.status == 'active':
                setattr(i, 'status', 'unsuccessful')
                for bid_index, bid in enumerate(tender.bids):
                    for lot_index, lot_value in enumerate(bid.lotValues):
                        if lot_value.relatedLot == i.id:
                            setattr(tender.bids[bid_index].lotValues[lot_index], 'status', 'unsuccessful')

        # [setattr(i, 'status', 'unsuccessful') for i in tender.lots if i.numberOfBids < 2 and i.status == 'active']

        if not set([i.status for i in tender.lots]).difference(set(['unsuccessful', 'cancelled'])):
            LOGGER.info('Switched tender {} to {}'.format(tender.id, 'unsuccessful'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_unsuccessful'}))
            tender.status = 'unsuccessful'
    elif tender.numberOfBids < 2:
        LOGGER.info('Switched tender {} to {}'.format(tender.id, 'unsuccessful'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_unsuccessful'}))
        if tender.auctionPeriod and tender.auctionPeriod.startDate:
            tender.auctionPeriod.startDate = None
        tender.status = 'unsuccessful'


def prepare_qualifications(request, bids=[], lotId=None):
    """ creates Qualification for each Bid
    """
    new_qualifications = []
    tender = request.validated['tender']
    if not bids:
        bids = tender.bids
    if tender.lots:
        active_lots = [lot.id for lot in tender.lots if lot.status == 'active']
        for bid in bids:
            if bid.status not in ['invalid', 'deleted']:
                for lotValue in bid.lotValues:
                    if lotValue.status == 'pending' and lotValue.relatedLot in active_lots:
                        if lotId:
                            if lotValue.relatedLot == lotId:
                                qualification = Qualification({'bidID': bid.id, 'status': 'pending', 'lotID': lotId})
                                qualification.date = get_now()
                                tender.qualifications.append(qualification)
                                new_qualifications.append(qualification.id)
                        else:
                            qualification = Qualification({'bidID': bid.id, 'status': 'pending', 'lotID': lotValue.relatedLot})
                            qualification.date = get_now()
                            tender.qualifications.append(qualification)
                            new_qualifications.append(qualification.id)
    else:
        for bid in bids:
            if bid.status == 'pending':
                qualification = Qualification({'bidID': bid.id, 'status': 'pending'})
                qualification.date = get_now()
                tender.qualifications.append(qualification)
                new_qualifications.append(qualification.id)
    return new_qualifications


def all_bids_are_reviewed(request):
    """ checks if all tender bids are reviewed
    """
    if request.validated['tender'].lots:
        active_lots = [lot.id for lot in request.validated['tender'].lots if lot.status == 'active']
        return all([
            lotValue.status != 'pending'
            for bid in request.validated['tender'].bids
            if bid.status not in ['invalid', 'deleted']
            for lotValue in bid.lotValues
            if lotValue.relatedLot in active_lots
        ])
    else:
        return all([bid.status != 'pending' for bid in request.validated['tender'].bids])


def check_status(request):
    tender = request.validated['tender']
    now = get_now()

    if tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and \
            not any([i.status in tender.block_tender_complaint_status for i in tender.complaints]) and \
            not any([i.id for i in tender.questions if not i.answer]):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.pre-qualification'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.pre-qualification'}))
        tender.status = 'active.pre-qualification'
        tender.qualificationPeriod = type(tender).qualificationPeriod({'startDate': now})
        remove_draft_bids(request)
        check_initial_bids_count(request)
        prepare_qualifications(request)
        return

    elif tender.status == 'active.pre-qualification.stand-still' and tender.qualificationPeriod and tender.qualificationPeriod.endDate <= now and not any([
        i.status in tender.block_complaint_status
        for q in tender.qualifications
        for i in q.complaints
    ]):
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.auction'}))
        tender.status = 'active.auction'
        check_initial_bids_count(request)
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
            check_tender_status(request)
    elif tender.lots and tender.status in ['active.qualification', 'active.awarded']:
        if any([i['status'] in tender.block_complaint_status and i.relatedLot is None for i in tender.complaints]):
            return
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
                check_tender_status(request)
                return
