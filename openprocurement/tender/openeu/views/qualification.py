# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import (
    apply_patch,
    save_tender,
    check_tender_status,
    opresource,
    json_view,
    context_unpack,
)
from openprocurement.tender.openeu.validation import validate_patch_qualification_data


LOGGER = getLogger(__name__)


@opresource(name='TenderEU Qualification',
            collection_path='/tenders/{tender_id}/qualifications',
            path='/tenders/{tender_id}/qualifications/{qualification_id}',
            procurementMethodType='aboveThresholdEU',
            description="TenderEU Qualification")
class TenderQualificationResource(object):

    def __init__(self, request, context):
        self.request = request
        self.db = request.registry.db

    @json_view(permission='view_tender')
    def collection_get(self):
        """List qualifications
        """
        return {'data': [i.serialize("view") for i in self.request.validated['tender'].qualifications]}

    @json_view(permission='view_tender')
    def get(self):
        """Retrieving the qualification
        """
        return {'data': self.request.validated['qualification'].serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_qualification_data,), permission='edit_tender')
    def patch(self):
        """Post a qualification resolution
        """
        def set_bid_status(tender, bid_id, status):
            for bid in tender.bids:
                if bid.id == bid_id:
                    bid.status = status
                    return

        tender = self.request.validated['tender']
        if tender.status not in ['active.pre-qualification']:
            self.request.errors.add('body', 'data', 'Can\'t update qualification in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return

        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if self.request.context.status == 'active':
            # approve related bid
            set_bid_status(tender, self.request.context.bidID, 'active')
        elif self.request.context.status == 'cancelled':
            # cancel related bid
            set_bid_status(tender, self.request.context.bidID, 'invalid')
        # switch to 'stand-still' when all bids are approved
        if all([bid.status != 'pending' for bid in tender.bids]):
            if sum([1 for bid in tender.bids if bid.status == 'active']) < 2:
                tender.status = 'unsuccessful'
            else:
                tender.status = 'active.pre-qualification.stand-still'
        if save_tender(self.request):
            LOGGER.info('Updated tender qualification {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_qualification_patch'}))
            return {'data': self.request.context.serialize("view")}
