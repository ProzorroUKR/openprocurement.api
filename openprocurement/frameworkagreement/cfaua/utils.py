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
from openprocurement.tender.belowthreshold.utils import check_ignored_claim
from openprocurement.tender.core.utils import (
    remove_draft_bids,
    has_unanswered_questions,
    has_unanswered_complaints
)
from openprocurement.tender.openua.utils import (
    add_next_award,
    check_complaint_status
)

from openprocurement.frameworkagreement.cfaua.models.submodels.qualification import Qualification
from openprocurement.frameworkagreement.cfaua.traversal import (
    agreement_factory, qualifications_factory, bid_financial_documents_factory,
    bid_eligibility_documents_factory, bid_qualification_documents_factory)
from zope.component import getAdapter


LOGGER = getLogger(__name__)


agreement_resource = partial(resource, error_handler=error_handler, factory=agreement_factory)
qualifications_resource = partial(resource, error_handler=error_handler, factory=qualifications_factory)
bid_financial_documents_resource = partial(resource,
                                           error_handler=error_handler,
                                           factory=bid_financial_documents_factory)
bid_eligibility_documents_resource = partial(resource,
                                             error_handler=error_handler,
                                             factory=bid_eligibility_documents_factory)
bid_qualification_documents_resource = partial(resource,
                                               error_handler=error_handler,
                                               factory=bid_qualification_documents_factory)


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
    configurator = request.content_configurator
    for award in tender.awards:
        if award.status == 'active' and not any([i.awardID == award.id for i in tender.agreements]):
            tender.agreements.append(type(tender).agreements.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'value': award.value,
                'date': now,
                'items': [i for i in tender.items if i.relatedLot == award.lotID],
                'agreementID': '{}-{}{}'.format(tender.tenderID, request.registry.server_id,
                                                len(tender.agreements) + 1)}))
            add_next_award(request,
                           reverse=configurator.reverse_awarding_criteria,
                           awarding_criteria_key=configurator.awarding_criteria_key)

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

    elif tender.status == 'active.pre-qualification.stand-still' and tender.qualificationPeriod and \
            tender.qualificationPeriod.endDate <= now and not any([
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


def check_tender_status(request):
    tender = request.validated['tender']
    now = get_now()
    if tender.lots:
        if any([i.status in tender.block_complaint_status and i.relatedLot is None for i in tender.complaints]):
            return
        for lot in tender.lots:
            if lot.status != 'active':
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            pending_complaints = any([
                i['status'] in tender.block_complaint_status and i.relatedLot == lot.id
                for i in tender.complaints
            ])
            pending_awards_complaints = any([
                i.status in tender.block_complaint_status
                for a in lot_awards
                for i in a.complaints
            ])
            stand_still_end = max([
                a.complaintPeriod.endDate or now
                for a in lot_awards
            ])
            if pending_complaints or pending_awards_complaints or not stand_still_end <= now:
                continue
            elif last_award.status == 'unsuccessful':
                LOGGER.info(
                    'Switched lot {} of tender {} to {}'.format(lot.id, tender.id, 'unsuccessful'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_unsuccessful'}, {'LOT_ID': lot.id})
                )
                lot.status = 'unsuccessful'
                continue
            elif last_award.status == 'active' and \
                    any([i.status == 'active' and i.awardID == last_award.id for i in tender.agreements]):
                LOGGER.info('Switched lot {} of tender {} to {}'.format(lot.id, tender.id, 'complete'),
                            extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_complete'}, {'LOT_ID': lot.id}))
                lot.status = 'complete'
        statuses = set([lot.status for lot in tender.lots])
        if statuses == set(['cancelled']):
            LOGGER.info('Switched tender {} to {}'.format(tender.id, 'cancelled'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_cancelled'}))
            tender.status = 'cancelled'
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            LOGGER.info('Switched tender {} to {}'.format(tender.id, 'unsuccessful'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_unsuccessful'}))
            tender.status = 'unsuccessful'
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            LOGGER.info('Switched tender {} to {}'.format(tender.id, 'complete'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_complete'}))
            tender.status = 'complete'
    else:
        pending_complaints = any([
            i.status in tender.block_complaint_status
            for i in tender.complaints
        ])
        pending_awards_complaints = any([
            i.status in tender.block_complaint_status
            for a in tender.awards
            for i in a.complaints
        ])
        stand_still_ends = [
            a.complaintPeriod.endDate
            for a in tender.awards
            if a.complaintPeriod.endDate
        ]
        stand_still_end = max(stand_still_ends) if stand_still_ends else now
        stand_still_time_expired = stand_still_end < now
        last_award_status = tender.awards[-1].status if tender.awards else ''
        if not pending_complaints and not pending_awards_complaints and \
                stand_still_time_expired and last_award_status == 'unsuccessful':
            LOGGER.info('Switched tender {} to {}'.format(tender.id, 'unsuccessful'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_unsuccessful'}))
            tender.status = 'unsuccessful'
        if tender.agreements and tender.agreements[-1].status == 'active':
            tender.status = 'complete'
    if tender.procurementMethodType == "belowThreshold":
        check_ignored_claim(tender)
