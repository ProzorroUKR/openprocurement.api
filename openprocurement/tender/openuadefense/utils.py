from logging import getLogger
from pkg_resources import get_distribution

from openprocurement.api.constants import read_json, TZ
from openprocurement.tender.core.utils import (
    context_unpack, get_now, has_unanswered_questions, has_unanswered_complaints
)
from openprocurement.tender.openua.utils import (
    check_complaint_status, add_next_award
)
from openprocurement.tender.belowthreshold.utils import check_tender_status
PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)
WORKING_DAYS = read_json('working_days.json')


def check_bids(request):
    tender = request.validated['tender']
    if tender.lots:
        [setattr(i.auctionPeriod, 'startDate', None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate]
        [setattr(i, 'status', 'unsuccessful') for i in tender.lots if i.numberOfBids == 0 and i.status == 'active']
        numberOfBids_in_active_lots = [i.numberOfBids for i in tender.lots if i.status == 'active']
        if numberOfBids_in_active_lots and max(numberOfBids_in_active_lots) < 2:
            add_next_award(request)
        if not set([i.status for i in tender.lots]).difference(set(['unsuccessful', 'cancelled'])):
            tender.status = 'unsuccessful'
    else:
        if tender.numberOfBids < 2 and tender.auctionPeriod and tender.auctionPeriod.startDate:
            tender.auctionPeriod.startDate = None
        if tender.numberOfBids == 0:
            tender.status = 'unsuccessful'
        if tender.numberOfBids == 1:
            add_next_award(request)


def check_status(request):
    tender = request.validated['tender']
    now = get_now()
    for award in tender.awards:
        if award.status == 'active' and not any([i.awardID == award.id for i in tender.contracts]):
            tender.contracts.append(type(tender).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'value': award.value,
                'date': now,
                'items': [i for i in tender.items if i.relatedLot == award.lotID ],
                'contractID': '{}-{}{}'.format(tender.tenderID, request.registry.server_id, len(tender.contracts) + 1) }))
            add_next_award(request)
    if not tender.lots and tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and \
        not has_unanswered_complaints(tender) and not has_unanswered_questions(tender):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.auction'}))
        tender.status = 'active.auction'
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
                i['status'] in tender.block_complaint_status
                for i in tender.complaints
            ])
            pending_awards_complaints = any([
                i['status'] in tender.block_complaint_status
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
                pending_complaints = any([
                    i['status'] in tender.block_complaint_status and i.relatedLot == lot.id
                    for i in tender.complaints
                ])
                pending_awards_complaints = any([
                    i['status'] in tender.block_complaint_status
                    for a in lot_awards
                    for i in a.complaints
                ])
                awarded = any([
                    i['status'] == 'active'
                    for i in lot_awards
                ])
                if not pending_complaints and not pending_awards_complaints and not awarded:
                    LOGGER.info('Switched lot {} of tender {} to {}'.format(lot['id'], tender.id, 'unsuccessful'),
                                extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_unsuccessful'}, {'LOT_ID': lot['id']}))
                    check_tender_status(request)
