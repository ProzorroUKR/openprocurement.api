# -*- coding: utf-8 -*-
from pkg_resources import get_distribution
from datetime import timedelta
from logging import getLogger
from openprocurement.api.utils import get_now
from openprocurement.api.constants import TZ, SANDBOX_MODE
from openprocurement.tender.core.utils import (
    has_unanswered_questions,
    has_unanswered_complaints,
    remove_draft_bids
)
from openprocurement.tender.belowthreshold.utils import (
    check_tender_status,
    context_unpack,
)
from openprocurement.tender.openua.constants import (
    NORMALIZED_COMPLAINT_PERIOD_FROM
)
from barbecue import chef
PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def calculate_normalized_date(dt, tender, ceil=False):
    if (tender.revisions[0].date if tender.revisions else get_now()) > NORMALIZED_COMPLAINT_PERIOD_FROM and \
            not (SANDBOX_MODE and tender.procurementMethodDetails):
        if ceil:
            return dt.astimezone(TZ).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return dt.astimezone(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    return dt


def check_bids(request):
    tender = request.validated['tender']
    if tender.lots:
        [setattr(i.auctionPeriod, 'startDate', None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate]
        [setattr(i, 'status', 'unsuccessful') for i in tender.lots if i.numberOfBids < 2 and i.status == 'active']
        if not set([i.status for i in tender.lots]).difference(set(['unsuccessful', 'cancelled'])):
            tender.status = 'unsuccessful'
    else:
        if tender.numberOfBids < 2:
            if tender.auctionPeriod and tender.auctionPeriod.startDate:
                tender.auctionPeriod.startDate = None
            tender.status = 'unsuccessful'


def check_complaint_status(request, complaint):
    if complaint.status == 'answered':
        complaint.status = complaint.resolutionType


def check_status(request):
    tender = request.validated['tender']
    now = get_now()
    configurator = request.content_configurator
    for award in tender.awards:
        if award.status == 'active' and not any([i.awardID == award.id for i in tender.contracts]):
            tender.contracts.append(type(tender).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'value': award.value,
                'date': now,
                'items': [i for i in tender.items if i.relatedLot == award.lotID ],
                'contractID': '{}-{}{}'.format(tender.tenderID, request.registry.server_id, len(tender.contracts) + 1) }))
            add_next_award(request, reverse=configurator.reverse_awarding_criteria, awarding_criteria_key=configurator.awarding_criteria_key)
    if not tender.lots and tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and \
        not has_unanswered_complaints(tender) and not has_unanswered_questions(tender):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.auction'}))
        tender.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        if tender.numberOfBids < 2 and tender.auctionPeriod:
            tender.auctionPeriod.startDate = None
        return
    elif tender.lots and tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and \
        not has_unanswered_complaints(tender) and not has_unanswered_questions(tender):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.auction'}))
        tender.status = 'active.auction'
        remove_draft_bids(request)
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


def add_next_award(request, reverse=False, awarding_criteria_key='amount'):
    """Adding next award.
    :param request:
        The pyramid request object.
    :param reverse:
        Is used for sorting bids to generate award.
        By default (reverse = False) awards are generated from lower to higher by value.amount
        When reverse is set to True awards are generated from higher to lower by value.amount
    """
    tender = request.validated['tender']
    now = get_now()
    if not tender.awardPeriod:
        tender.awardPeriod = type(tender).awardPeriod({})
    if not tender.awardPeriod.startDate:
        tender.awardPeriod.startDate = now
    if tender.lots:
        statuses = set()
        for lot in tender.lots:
            if lot.status != 'active':
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            if lot_awards and lot_awards[-1].status in ['pending', 'active']:
                statuses.add(lot_awards[-1].status if lot_awards else 'unsuccessful')
                continue
            lot_items = [i.id for i in tender.items if i.relatedLot == lot.id]
            features = [
                i
                for i in (tender.features or [])
                if i.featureOf == 'tenderer' or i.featureOf == 'lot' and i.relatedItem == lot.id or i.featureOf == 'item' and i.relatedItem in lot_items
            ]
            codes = [i.code for i in features]
            bids = [
                {
                    'id': bid.id,
                    'value': [i for i in bid.lotValues if lot.id == i.relatedLot][0].value.serialize(),
                    'tenderers': bid.tenderers,
                    'parameters': [i for i in bid.parameters if i.code in codes],
                    'date': [i for i in bid.lotValues if lot.id == i.relatedLot][0].date
                }
                for bid in tender.bids
                if bid.status == "active" and lot.id in [i.relatedLot for i in bid.lotValues if getattr(i, 'status', "active") == "active"]
            ]
            if not bids:
                lot.status = 'unsuccessful'
                statuses.add('unsuccessful')
                continue
            unsuccessful_awards = [i.bid_id for i in lot_awards if i.status == 'unsuccessful']
            bids = chef(bids, features, unsuccessful_awards, reverse, awarding_criteria_key)
            if bids:
                bid = bids[0]
                award = tender.__class__.awards.model_class({
                    'bid_id': bid['id'],
                    'lotID': lot.id,
                    'status': 'pending',
                    'date': get_now(),
                    'value': bid['value'],
                    'suppliers': bid['tenderers'],
                    'complaintPeriod': {
                        'startDate': now.isoformat()
                    }
                })
                award.__parent__ = tender
                tender.awards.append(award)
                request.response.headers['Location'] = request.route_url('{}:Tender Awards'.format(tender.procurementMethodType), tender_id=tender.id, award_id=award['id'])
                statuses.add('pending')
            else:
                statuses.add('unsuccessful')
        if statuses.difference(set(['unsuccessful', 'active'])):
            tender.awardPeriod.endDate = None
            tender.status = 'active.qualification'
        else:
            tender.awardPeriod.endDate = now
            tender.status = 'active.awarded'
    else:
        if not tender.awards or tender.awards[-1].status not in ['pending', 'active']:
            unsuccessful_awards = [i.bid_id for i in tender.awards if i.status == 'unsuccessful']
            active_bids = [
                {
                    'id': bid.id,
                    'value': bid.value.serialize(),
                    'tenderers': bid.tenderers,
                    'parameters': [i for i in bid.parameters if i.code in codes],
                    'date': bid.date
                }
                for bid in tender.bids
                if bid.status == "active"
            ]
            bids = chef(active_bids, tender.features or [], unsuccessful_awards, reverse, awarding_criteria_key)
            if bids:
                bid = bids[0]
                award = tender.__class__.awards.model_class({
                    'bid_id': bid['id'],
                    'status': 'pending',
                    'date': get_now(),
                    'value': bid['value'],
                    'suppliers': bid['tenderers'],
                    'complaintPeriod': {
                        'startDate': get_now().isoformat()
                    }
                })
                award.__parent__ = tender
                tender.awards.append(award)
                request.response.headers['Location'] = request.route_url('{}:Tender Awards'.format(tender.procurementMethodType), tender_id=tender.id, award_id=award['id'])
        if tender.awards[-1].status == 'pending':
            tender.awardPeriod.endDate = None
            tender.status = 'active.qualification'
        else:
            tender.awardPeriod.endDate = now
            tender.status = 'active.awarded'

