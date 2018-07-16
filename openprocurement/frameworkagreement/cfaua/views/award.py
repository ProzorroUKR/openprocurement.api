# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    get_now,
    raise_operation_error
)
from openprocurement.tender.core.validation import (
    validate_patch_award_data,
    validate_update_award_only_for_active_lots,
    validate_update_award_in_not_allowed_status,
    validate_update_award_with_accepted_complaint
)
from openprocurement.tender.core.utils import (
    apply_patch,
    optendersresource,
    save_tender,
    calculate_business_date
)
from openprocurement.tender.openua.views.award import TenderUaAwardResource as BaseResource


@optendersresource(name='closeFrameworkAgreementUA:Tender Awards',
                   collection_path='/tenders/{tender_id}/awards',
                   path='/tenders/{tender_id}/awards/{award_id}',
                   description="Tender EU awards",
                   procurementMethodType='closeFrameworkAgreementUA')
class TenderAwardResource(BaseResource):
    """ EU award resource """

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_patch_award_data, validate_update_award_in_not_allowed_status,
               validate_update_award_only_for_active_lots, validate_update_award_with_accepted_complaint))
    def patch(self):
        """Update of award

        Example request to change the award:

        .. sourcecode:: http

        """
        tender = self.request.validated['tender']
        award = self.request.context
        award_status = award.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())

        if award_status == 'pending' and award.status in ['active', 'unsuccessful']:
            pass
        elif award_status == 'active' and award.status == 'cancelled':
            pass
        elif award_status == 'pending' and award.status == 'cancelled': # and award.status  'active':
            print 'need to cancel here'
        elif self.request.authenticated_role != 'Administrator' and not(award_status == 'pending' and award.status == 'pending'):
            raise_operation_error(self.request, 'Can\'t update award in current ({}) status'.format(award_status))
        if save_tender(self.request):
            self.LOGGER.info('Updated tender award {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_patch'}))
            return {'data': award.serialize("view")}
