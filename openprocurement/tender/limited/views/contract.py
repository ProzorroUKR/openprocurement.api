# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now, timedelta
from openprocurement.api.utils import (
    apply_patch,
    save_tender,
    opresource,
    json_view,
    context_unpack,
)
from openprocurement.api.validation import (
    validate_contract_data,
    validate_patch_contract_data,
)
from openprocurement.api.views.contract import TenderAwardContractResource as BaseTenderAwardContractResource


def check_tender_status(request):
    tender = request.validated['tender']
    if tender.contracts and tender.contracts[-1].status == 'active':
        tender.status = 'complete'


def check_tender_negotiation_status(request):
    tender = request.validated['tender']
    if tender.contracts and tender.contracts[-1].status == 'active':
        tender.status = 'complete'
    now = get_now()
    if tender.lots:
        for lot in tender.lots:
            if lot.status != 'active':
                continue
            lot_awards = [i for i in tender.awards if i.lotID == lot.id]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            pending_awards_complaints = any([
                i.status in ['claim', 'answered', 'pending']
                for a in lot_awards
                for i in a.complaints
            ])
            stand_still_end = max([
                a.complaintPeriod.endDate or now
                for a in lot_awards
            ])
            if pending_awards_complaints or not stand_still_end <= now:
                continue
            elif last_award.status == 'unsuccessful':
                lot.status = 'unsuccessful'
                continue
            elif last_award.status == 'active' and any([i.status == 'active' and i.awardID == last_award.id for i in tender.contracts]):
                lot.status = 'complete'
        statuses = set([lot.status for lot in tender.lots])
        if statuses == set(['cancelled']):
            tender.status = 'cancelled'
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            tender.status = 'unsuccessful'
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            tender.status = 'complete'
    else:
        if tender.contracts and tender.contracts[-1].status == 'active':
            tender.status = 'complete'


@opresource(name='Tender Limited Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            procurementMethodType='reporting',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            description="Tender contracts")
class TenderAwardContractResource(BaseTenderAwardContractResource):

    @json_view(content_type="application/json", permission='create_contract', validators=(validate_contract_data,))
    def collection_post(self):
        """Post a contract for award
        """
        tender = self.request.validated['tender']
        if tender.status not in ['active']:
            self.request.errors.add('body', 'data', 'Can\'t add contract in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        contract = self.request.validated['contract']
        tender.contracts.append(contract)
        if save_tender(self.request):
            self.LOGGER.info('Created tender contract {}'.format(contract.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_create'}, {'contract_id': contract.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('Tender Contracts', tender_id=tender.id, contract_id=contract['id'])
            return {'data': contract.serialize()}

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_patch_contract_data,))
    def patch(self):
        """Update of contract
        """
        if self.request.validated['tender_status'] not in ['active']:
            self.request.errors.add('body', 'data', 'Can\'t update contract in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if self.request.context.status == 'cancelled':
            self.request.errors.add('body', 'data', 'Can\'t update contract in current ({}) status'.format(self.request.context.status))
            self.request.errors.status = 403
            return

        data = self.request.validated['data']
        if data['value']:
            for ro_attr in ('valueAddedTaxIncluded', 'currency'):
                if data['value'][ro_attr] != getattr(self.context.value, ro_attr):
                    self.request.errors.add('body', 'data', 'Can\'t update {} for contract value'.format(ro_attr))
                    self.request.errors.status = 403
                    return

            award = [a for a in self.request.validated['tender'].awards if a.id == self.request.context.awardID][0]
            if data['value']['amount'] > award.value.amount:
                self.request.errors.add('body', 'data', 'Value amount should be less or equal to awarded amount ({})'.format(award.value.amount))
                self.request.errors.status = 403
                return

        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        self.request.context.date = get_now()
        if contract_status != self.request.context.status and contract_status != 'pending' and self.request.context.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t update contract status')
            self.request.errors.status = 403
            return

        if self.request.context.status == 'active' and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender contract {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_patch'}))
            return {'data': self.request.context.serialize()}


@opresource(name='Tender Negotiation Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            procurementMethodType='negotiation',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            description="Tender contracts")
class TenderNegotiationAwardContractResource(TenderAwardContractResource):
    """ Tender Negotiation Award Contract Resource """
    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_patch_contract_data,))
    def patch(self):
        """Update of contract
        """
        if self.request.validated['tender_status'] not in ['active']:
            self.request.errors.add('body', 'data', 'Can\'t update contract in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if self.request.context.status == 'cancelled':
            self.request.errors.add('body', 'data', 'Can\'t update contract in current ({}) status'.format(self.request.context.status))
            self.request.errors.status = 403
            return

        data = self.request.validated['data']
        if self.request.context.status != 'active' and 'status' in data and data['status'] == 'active':
            tender = self.request.validated['tender']
            award = [a for a in tender.awards if a.id == self.request.context.awardID][0]
            stand_still_end = award.complaintPeriod.endDate
            if stand_still_end > get_now():
                self.request.errors.add('body', 'data', 'Can\'t sign contract before stand-still period end ({})'.format(stand_still_end.isoformat()))
                self.request.errors.status = 403
                return
            if any([
                i.status in tender.block_complaint_status and a.lotID == award.lotID
                for a in tender.awards
                for i in a.complaints
            ]):
                self.request.errors.add('body', 'data', 'Can\'t sign contract before reviewing all complaints')
                self.request.errors.status = 403
                return

        if data['value']:
            for ro_attr in ('valueAddedTaxIncluded', 'currency'):
                if data['value'][ro_attr] != getattr(self.context.value, ro_attr):
                    self.request.errors.add('body', 'data', 'Can\'t update {} for contract value'.format(ro_attr))
                    self.request.errors.status = 403
                    return

            award = [a for a in self.request.validated['tender'].awards if a.id == self.request.context.awardID][0]
            if data['value']['amount'] > award.value.amount:
                self.request.errors.add('body', 'data', 'Value amount should be less or equal to awarded amount ({})'.format(award.value.amount))
                self.request.errors.status = 403
                return

        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        self.request.context.date = get_now()
        if contract_status != self.request.context.status and contract_status != 'pending' and self.request.context.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t update contract status')
            self.request.errors.status = 403
            return

        if self.request.context.status == 'active' and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_negotiation_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender contract {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_patch'}))
            return {'data': self.request.context.serialize()}

@opresource(name='Tender Negotiation Quick Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            procurementMethodType='negotiation.quick',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            description="Tender contracts")
class TenderNegotiationQuickAwardContractResource(TenderNegotiationAwardContractResource):
    """ Tender Negotiation Quick Award Contract Resource """
