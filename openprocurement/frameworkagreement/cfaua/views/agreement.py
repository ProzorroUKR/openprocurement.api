# -*- coding: utf-8 -*-
from openprocurement.api.utils import context_unpack, json_view, get_now, raise_operation_error
from openprocurement.tender.core.utils import apply_patch, save_tender
from openprocurement.tender.openua.views.contract import (
    TenderUaAwardContractResource as BaseResource
)

from openprocurement.frameworkagreement.cfaua.validation import (
    validate_agreement_data,
    validate_agreement_operation_not_in_allowed_status,
    validate_agreement_signing,
    validate_agreement_update_with_accepted_complaint,
    validate_patch_agreement_data,
    validate_update_agreement_only_for_active_lots,
    validate_update_agreement_value,
)
from openprocurement.frameworkagreement.cfaua.utils import agreement_resource, check_tender_status


@agreement_resource(name='closeFrameworkAgreementUA:Tender Agreements',
                    collection_path='/tenders/{tender_id}/agreements',
                    path='/tenders/{tender_id}/agreements/{agreement_id}',
                    procurementMethodType='closeFrameworkAgreementUA',
                    description="Tender EU agreements")
class TenderAwardContractResource(BaseResource):
    """ """

    @json_view(content_type="application/json",
               permission='create_agreement',
               validators=(validate_agreement_data, validate_agreement_operation_not_in_allowed_status))
    def collection_post(self):
        """ Post a agreement for award """

        tender = self.request.validated['tender']
        agreement = self.request.validated['agreement']
        tender.agreements.append(agreement)
        if save_tender(self.request):
            self.LOGGER.info(
                'Created tender agreement {}'.format(agreement.id),
                extra=context_unpack(self.request,
                                     {'MESSAGE_ID': 'tender_agreement_create'}, {'agreement_id': agreement.id})
            )
            self.request.response.status = 201
            self.request.response.headers['Location'] = \
                self.request.route_url('{}:Tender Agreements'.format(tender.procurementMethodType),
                                       tender_id=tender.id,
                                       agreement_id=agreement['id'])
            return {'data': agreement.serialize()}

    @json_view(permission='view_tender')
    def collection_get(self):
        """ List contracts for award """

        return {'data': [i.serialize() for i in self.request.context.agreements]}

    @json_view(permission='view_tender')
    def get(self):
        """ Retrieving the contract for award """

        return {'data': self.request.validated['agreement'].serialize()}

    @json_view(content_type="application/json",
               permission='edit_tender',
               validators=(validate_patch_agreement_data,
                           validate_agreement_operation_not_in_allowed_status,
                           validate_update_agreement_only_for_active_lots,
                           validate_agreement_update_with_accepted_complaint,
                           validate_update_agreement_value,
                           validate_agreement_signing))
    def patch(self):
        """ Update of agreement """
        agreement_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if agreement_status != self.request.context.status and \
                (agreement_status != 'pending' or self.request.context.status != 'active'):
            raise_operation_error(self.request, 'Can\'t update agreement status')
        if self.request.context.status == 'active' and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender agreement {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_agreement_patch'}))
            return {'data': self.request.context.serialize()}
