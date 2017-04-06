# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.views.contract import TenderAwardContractResource
from openprocurement.api.utils import (
    context_unpack,
    json_view,
    get_now,
    raise_operation_error
)
from openprocurement.tender.openua.utils import check_tender_status
from openprocurement.tender.core.validation import (
    validate_patch_contract_data,
    validate_update_contract_value,
    validate_update_contract_only_for_active_lots,
    validate_contract_operation_not_in_allowed_status
)
from openprocurement.tender.core.utils import (
    save_tender,
    apply_patch,
    optendersresource
)
from openprocurement.tender.openua.validation import validate_contract_update_with_accepted_complaint


@optendersresource(name='aboveThresholdUA:Tender Contracts',
                   collection_path='/tenders/{tender_id}/contracts',
                   path='/tenders/{tender_id}/contracts/{contract_id}',
                   procurementMethodType='aboveThresholdUA',
                   description="Tender contracts")
class TenderUaAwardContractResource(TenderAwardContractResource):

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_patch_contract_data, validate_contract_operation_not_in_allowed_status,
               validate_update_contract_only_for_active_lots, validate_contract_update_with_accepted_complaint, validate_update_contract_value))
    def patch(self):
        """Update of contract
        """
        tender = self.request.validated['tender']
        data = self.request.validated['data']

        if self.request.context.status != 'active' and 'status' in data and data['status'] == 'active':
            award = [a for a in tender.awards if a.id == self.request.context.awardID][0]
            stand_still_end = award.complaintPeriod.endDate
            if stand_still_end > get_now():
                raise_operation_error(self.request, 'Can\'t sign contract before stand-still period end ({})'.format(stand_still_end.isoformat()))
            pending_complaints = [
                i
                for i in tender.complaints
                if i.status in tender.block_complaint_status and i.relatedLot in [None, award.lotID]
            ]
            pending_awards_complaints = [
                i
                for a in tender.awards
                for i in a.complaints
                if i.status in tender.block_complaint_status and a.lotID == award.lotID
            ]
            if pending_complaints or pending_awards_complaints:
                raise_operation_error(self.request, 'Can\'t sign contract before reviewing all complaints')
        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if contract_status != self.request.context.status and (contract_status != 'pending' or self.request.context.status != 'active'):
            raise_operation_error(self.request, 'Can\'t update contract status')
        if self.request.context.status == 'active' and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender contract {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_patch'}))
            return {'data': self.request.context.serialize()}
