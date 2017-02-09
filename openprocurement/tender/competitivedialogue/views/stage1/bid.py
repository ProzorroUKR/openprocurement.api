# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource, context_unpack, apply_patch, get_now, json_view
from openprocurement.tender.openeu.views.bid import TenderBidResource as BaseResourceEU
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.api.validation import validate_patch_bid_data


def patch_bid_first_stage(self):
    """Update of proposal

                Example request to change bid proposal:

                .. sourcecode:: http

                    PATCH /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
                    Host: example.com
                    Accept: application/json

                    {
                        "data": {
                            "value": {
                                "amount": 600
                            }
                        }
                    }

                And here is the response to be expected:

                .. sourcecode:: http

                    HTTP/1.0 200 OK
                    Content-Type: application/json

                    {
                        "data": {
                            "value": {
                                "amount": 600,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        }
                    }

                """
    if self.request.authenticated_role != 'Administrator' and self.request.validated['tender_status'] != 'active.tendering':
        self.request.errors.add('body', 'data', 'Can\'t update bid in current ({}) tender status'.format(self.request.validated['tender_status']))
        self.request.errors.status = 403
        return
    tender = self.request.validated['tender']
    if self.request.authenticated_role != 'Administrator' and (
                    tender.tenderPeriod.startDate and get_now() < tender.tenderPeriod.startDate or get_now() > tender.tenderPeriod.endDate):
        self.request.errors.add('body', 'data',
                                'Bid can be updated only during the tendering period: from ({}) to ({}).'.format(
                                    tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(),
                                    tender.tenderPeriod.endDate.isoformat()))
        self.request.errors.status = 403
        return
    if self.request.context.status == 'deleted':
            self.request.errors.add('body', 'bid', 'Can\'t update bid in ({}) status'.format(self.request.context.status))
            self.request.errors.status = 403
            return
    if self.request.authenticated_role != 'Administrator':
        bid_status_to = self.request.validated['data'].get("status", self.request.context.status)
        if bid_status_to not in ['pending', 'draft']:
            self.request.errors.add('body', 'bid', 'Can\'t update bid to ({}) status'.format(bid_status_to))
            self.request.errors.status = 403
            return
    self.request.validated['tender'].modified = False
    if apply_patch(self.request, src=self.request.context.serialize()):
        self.LOGGER.info('Updated tender bid {}'.format(self.request.context.id),
                         extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_bid_patch'}))
        return {'data': self.request.context.serialize("view")}


@opresource(name='Competitive Dialogue EU Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType=CD_EU_TYPE,
            description="Competitive Dialogue EU bids")
class CompetitiveDialogueEUBidResource(BaseResourceEU):
    """ Tender EU bids """

    patch = json_view(content_type="application/json",
                      permission='edit_bid',
                      validators=(validate_patch_bid_data,))(patch_bid_first_stage)


@opresource(name='Competitive Dialogue UA Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType=CD_UA_TYPE,
            description="Competitive Dialogue UA bids")
class CompetitiveDialogueUABidResource(BaseResourceEU):
    """ Tender UA bids """

    patch = json_view(content_type="application/json",
                      permission='edit_bid',
                      validators=(validate_patch_bid_data,))(patch_bid_first_stage)
