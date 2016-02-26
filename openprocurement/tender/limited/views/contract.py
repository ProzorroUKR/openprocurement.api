# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.models import get_now
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


LOGGER = getLogger(__name__)


def check_tender_status(request):
    tender = request.validated['tender']
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
            LOGGER.info('Created tender contract {}'.format(contract.id),
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

        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if contract_status != self.request.context.status and contract_status != 'pending' and self.request.context.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t update contract status')
            self.request.errors.status = 403
            return

        check_tender_status(self.request)
        if save_tender(self.request):
            LOGGER.info('Updated tender contract {}'.format(self.request.context.id),
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
        data = self.request.validated['data']
        if self.request.context.status == 'cancelled':
            self.request.errors.add('body', 'data', 'Can\'t update contract in current ({}) status'.format(self.request.context.status))
            self.request.errors.status = 403
            return
        if self.request.context.status != 'active' and 'status' in data and data['status'] == 'active':
            tender = self.request.validated['tender']
            award = [a for a in tender.awards if a.id == self.request.context.awardID][0]
            stand_still_end = award.complaintPeriod.endDate
            if stand_still_end > get_now():
                self.request.errors.add('body', 'data', 'Can\'t sign contract before stand-still period end ({})'.format(stand_still_end.isoformat()))
                self.request.errors.status = 403
                return

        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if contract_status != self.request.context.status and contract_status != 'pending' and self.request.context.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t update contract status')
            self.request.errors.status = 403
            return

        check_tender_status(self.request)
        if save_tender(self.request):
            LOGGER.info('Updated tender contract {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_patch'}))
            return {'data': self.request.context.serialize()}


@opresource(name='Tender Negotiation Quick Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            procurementMethodType='negotiation.quick',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            description="Tender contracts")
class TenderNegotiationQuickAwardContractResource(TenderNegotiationAwardContractResource):
    """ Tender Negotiation Quick Award Contract Resource """
