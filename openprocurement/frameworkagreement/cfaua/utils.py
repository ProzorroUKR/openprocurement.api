# -*- coding: utf-8 -*-
from logging import getLogger
from functools import partial
from cornice.resource import resource
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import (
    error_handler,
    context_unpack,
)
from barbecue import chef
from openprocurement.tender.core.utils import (
    remove_draft_bids,
    has_unanswered_questions,
    has_unanswered_complaints
)
from openprocurement.tender.belowthreshold.utils import (
    check_tender_status
)
from openprocurement.tender.openua.utils import (
    add_next_award,
    check_complaint_status
)
from openprocurement.frameworkagreement.cfaua.constants import MaxAwards, MIN_BIDS_NUMBER
from openprocurement.frameworkagreement.cfaua.models.submodels.qualification import Qualification
from openprocurement.frameworkagreement.cfaua.traversal import (
    qualifications_factory, bid_financial_documents_factory,
    bid_eligibility_documents_factory, bid_qualification_documents_factory)
from zope.component import getAdapter

LOGGER = getLogger(__name__)

qualifications_resource = partial(resource, error_handler=error_handler, factory=qualifications_factory)
bid_financial_documents_resource = partial(resource, error_handler=error_handler, factory=bid_financial_documents_factory)
bid_eligibility_documents_resource = partial(resource, error_handler=error_handler, factory=bid_eligibility_documents_factory)
bid_qualification_documents_resource = partial(resource, error_handler=error_handler, factory=bid_qualification_documents_factory)


def check_initial_bids_count(request):
    tender = request.validated['tender']
    if tender.lots:
        [setattr(i.auctionPeriod, 'startDate', None) for i in tender.lots if i.numberOfBids < getAdapter(tender, IContentConfigurator).min_bids_number and i.auctionPeriod and i.auctionPeriod.startDate]

        for i in tender.lots:
            if i.numberOfBids < getAdapter(tender, IContentConfigurator).min_bids_number and i.status == 'active':
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
    elif tender.numberOfBids < getAdapter(tender, IContentConfigurator).min_bids_number:
        LOGGER.info('Switched tender {} to {}'.format(tender.id, 'unsuccessful'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_unsuccessful'}))
        if tender.auctionPeriod and tender.auctionPeriod.startDate:
            tender.auctionPeriod.startDate = None
        tender.status = 'unsuccessful'


def check_initial_awards_count(request):
    tender = request.validated['tender']
    if tender.lots:
        [setattr(i.awardPeriod, 'startDate', None) for i in tender.lots if i.numberOfBids < getAdapter(tender, IContentConfigurator).min_bids_number and i.awardPeriod and i.awardPeriod.startDate]

        for i in tender.lots:
            if i.numberOfBids < getAdapter(tender, IContentConfigurator).min_bids_number and i.status == 'active':
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
    elif tender.numberOfAwards < getAdapter(tender, IContentConfigurator).min_bids_number:
        LOGGER.info('Switched tender {} to {}'.format(tender.id, 'unsuccessful'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_unsuccessful'}))
        if tender.awardPeriod and tender.awardPeriod.startDate:
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
    active_lots = [lot.id for lot in tender.lots if lot.status == 'active'] if tender.lots else [None]

    if tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and \
            not has_unanswered_complaints(tender) and not has_unanswered_questions(tender):
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
        if q.lotID in active_lots
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
    elif tender.status == 'active.qualification.stand-still' and tender.awardPeriod and tender.awardPeriod.endDate <= now and not any([
        i.status in tender.block_complaint_status
        for q in tender.qualifications
        for i in q.complaints
        if q.lotID in active_lots
    ]):
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.awarded'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.awarded'}))
        tender.status = 'active.awarded'
        check_initial_awards_count(request)
        if tender.status == 'active.awarded':
            tender.contracts.append(type(tender).contracts.model_class({
                'awardID': tender.awards[0].id,
                'suppliers': tender.awards[0].suppliers,
                'value': tender.awards[0].value,
                'items': [i for i in tender.items if i.relatedLot == tender.awards[0].lotID],
                'contractID': '{}-{}{}'.format(tender.tenderID, request.registry.server_id, len(tender.contracts) + 1)}))
        return


def add_next_awards(request, reverse=False, awarding_criteria_key='amount'):
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
                for bid in bids:
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
        if not tender.awards or len(tender.numberOfAwards) < MIN_BIDS_NUMBER:
            unsuccessful_awards = [i.bid_id for i in tender.awards if i.status == 'unsuccessful']
            codes = [i.code for i in tender.features or []]
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
            bids = bids[:MaxAwards] if MaxAwards else bids
            if bids:
                for bid in bids:
                    award = tender.__class__.awards.model_class({
                        'bid_id': bid['id'],
                        'status': 'pending',
                        'date': get_now(),
                        'value': bid['value'],
                        'suppliers': bid['tenderers'],
                    })
                    award.__parent__ = tender
                    tender.awards.append(award)
        if tender.awards[-1].status == 'pending':
            tender.awardPeriod.endDate = None
            tender.status = 'active.qualification'
        else:
            tender.awardPeriod.endDate = now
            tender.status = 'active.awarded'


def all_awards_are_reviewed(request):
    """ checks if all tender awards are reviewed
    """
    return all([award.status != 'pending' for award in request.validated['tender'].awards])