# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    apply_patch,
    save_tender,
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.tender.openeu.validation import validate_patch_qualification_data
from openprocurement.tender.openeu.utils import qualifications_resource, prepare_qualifications


@qualifications_resource(
    name='TenderEU Qualification',
    collection_path='/tenders/{tender_id}/qualifications',
    path='/tenders/{tender_id}/qualifications/{qualification_id}',
    procurementMethodType='aboveThresholdEU',
    description="TenderEU Qualification")
class TenderQualificationResource(APIResource):

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
        def set_bid_status(tender, bid_id, status, lotId=None):
            if lotId:
                for bid in tender.bids:
                    if bid.id == bid_id:
                        for lotValue in bid.lotValues:
                            if lotValue.relatedLot == lotId:
                                lotValue.status = status
                                return bid
            for bid in tender.bids:
                if bid.id == bid_id:
                    bid.status = status
                    return bid
        tender = self.request.validated['tender']
        if tender.status not in ['active.pre-qualification']:
            self.request.errors.add('body', 'data', 'Can\'t update qualification in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        if self.request.context.status == 'cancelled':
            self.request.errors.add('body', 'data', 'Can\'t update qualification in current cancelled qualification status')
            self.request.errors.status = 403
            return

        prev_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if prev_status != 'pending' and self.request.context.status != 'cancelled':
            self.request.errors.add('body', 'data', 'Can\'t update qualification status'.format(tender.status))
            self.request.errors.status = 403
            return
        if self.request.context.status == 'active':
            # approve related bid
            set_bid_status(tender, self.request.context.bidID, 'active', self.request.context.lotID)
        elif self.request.context.status == 'unsuccessful':
            # cancel related bid
            set_bid_status(tender, self.request.context.bidID, 'unsuccessful', self.request.context.lotID)
        elif self.request.context.status == 'cancelled':
            # return bid to initial status
            bid = set_bid_status(tender, self.request.context.bidID, 'pending', self.request.context.lotID)
            # generate new qualification for related bid
            ids = prepare_qualifications(self.request, bids=[bid], lotId=self.request.context.lotID)
            self.request.response.headers['Location'] = self.request.route_url('TenderEU Qualification',
                                                                               tender_id=tender.id,
                                                                               qualification_id=ids[0])
        if save_tender(self.request):
            self.LOGGER.info('Updated tender qualification {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_qualification_patch'}))
            return {'data': self.request.context.serialize("view")}
