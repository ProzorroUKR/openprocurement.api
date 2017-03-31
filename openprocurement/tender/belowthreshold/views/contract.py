# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    opresource,
    json_view,
    context_unpack,
    APIResource,
    error_handler
)
from openprocurement.tender.core.utils import (
    save_tender, optendersresource, apply_patch,
)
from openprocurement.tender.core.validation import (
    validate_update_contract_value,
    validate_update_contract_only_for_active_lots,
    validate_contract_operation_not_in_allowed_status
)
from openprocurement.tender.belowthreshold.validation import (
    validate_contract_data,
    validate_patch_contract_data
)
from openprocurement.tender.belowthreshold.utils import (
    check_tender_status,
)

@optendersresource(name='belowThreshold:Tender Contracts',
                   collection_path='/tenders/{tender_id}/contracts',
                   path='/tenders/{tender_id}/contracts/{contract_id}',
                   procurementMethodType='belowThreshold',
                   description="Tender contracts")
class TenderAwardContractResource(APIResource):

    @json_view(content_type="application/json", permission='create_contract', validators=(validate_contract_data, validate_contract_operation_not_in_allowed_status))
    def collection_post(self):
        """Post a contract for award
        """
        tender = self.request.validated['tender']
        contract = self.request.validated['contract']
        tender.contracts.append(contract)
        if save_tender(self.request):
            self.LOGGER.info('Created tender contract {}'.format(contract.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_create'}, {'contract_id': contract.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('{}:Tender Contracts'.format(tender.procurementMethodType), tender_id=tender.id, contract_id=contract['id'])
            return {'data': contract.serialize()}

    @json_view(permission='view_tender')
    def collection_get(self):
        """List contracts for award
        """
        return {'data': [i.serialize() for i in self.request.context.contracts]}

    @json_view(permission='view_tender')
    def get(self):
        """Retrieving the contract for award
        """
        return {'data': self.request.validated['contract'].serialize()}

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_patch_contract_data, validate_contract_operation_not_in_allowed_status,
               validate_update_contract_only_for_active_lots, validate_update_contract_value))
    def patch(self):
        """Update of contract
        """
        tender = self.request.validated['tender']
        data = self.request.validated['data']

        if self.request.context.status != 'active' and 'status' in data and data['status'] == 'active':
            award = [a for a in tender.awards if a.id == self.request.context.awardID][0]
            stand_still_end = award.complaintPeriod.endDate
            if stand_still_end > get_now():
                self.request.errors.add('body', 'data', 'Can\'t sign contract before stand-still period end ({})'.format(stand_still_end.isoformat()))
                self.request.errors.status = 403
                raise error_handler(self.request.errors)
            pending_complaints = [
                i
                for i in tender.complaints
                if i.status in ['claim', 'answered', 'pending'] and i.relatedLot in [None, award.lotID]
            ]
            pending_awards_complaints = [
                i
                for a in tender.awards
                for i in a.complaints
                if i.status in ['claim', 'answered', 'pending'] and a.lotID == award.lotID
            ]
            if pending_complaints or pending_awards_complaints:
                self.request.errors.add('body', 'data', 'Can\'t sign contract before reviewing all complaints')
                self.request.errors.status = 403
                raise error_handler(self.request.errors)
        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if contract_status != self.request.context.status and (contract_status != 'pending' or self.request.context.status != 'active'):
            self.request.errors.add('body', 'data', 'Can\'t update contract status')
            self.request.errors.status = 403
            raise error_handler(self.request.errors)
        if self.request.context.status == 'active' and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender contract {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_patch'}))
            return {'data': self.request.context.serialize()}
