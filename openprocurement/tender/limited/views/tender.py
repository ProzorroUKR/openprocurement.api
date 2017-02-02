# -*- coding: utf-8 -*-
from openprocurement.api.views.tender import TenderResource as BaseTenderResource
from openprocurement.api.validation import validate_patch_tender_data
from openprocurement.api.utils import (
    apply_patch,
    opresource,
    json_view,
    context_unpack,
)


@opresource(name='TenderLimited',
            path='/tenders/{tender_id}',
            procurementMethodType='reporting',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderResource(BaseTenderResource):
    """ Resource handler for TenderLimited """

    @json_view(content_type="application/json", validators=(validate_patch_tender_data, ), permission='edit_tender')
    def patch(self):
        """Tender Edit (partial)

        For example here is how procuring entity can change number of items to be procured and total Value of a tender:

        .. sourcecode:: http

            PATCH /tenders/4879d3f8ee2443169b5fbbc9f89fa607 HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "value": {
                        "amount": 600
                    },
                    "itemsToBeProcured": [
                        {
                            "quantity": 6
                        }
                    ]
                }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "tenderID": "UA-64e93250be76435397e8c992ed4214d1",
                    "dateModified": "2014-10-27T08:12:34.956Z",
                    "value": {
                        "amount": 600
                    },
                    "itemsToBeProcured": [
                        {
                            "quantity": 6
                        }
                    ]
                }
            }

        """
        tender = self.request.validated['tender']
        if self.request.authenticated_role != 'Administrator' and tender.status in ['complete', 'unsuccessful', 'cancelled']:
            self.request.errors.add('body', 'data', 'Can\'t update tender in current ({}) status'.format(tender.status))
            self.request.errors.status = 403
            return
        data = self.request.validated['data']
        if self.request.authenticated_role == 'chronograph':
            self.request.errors.add('body', 'data', 'Chronograph has no power over me!')
            self.request.errors.status = 403
            return
        else:
            data = self.request.validated['data']
            if tender.awards:
                self.request.errors.add('body', 'data', 'Can\'t update tender when there is at least one award.')
                self.request.errors.status = 403
                return
            apply_patch(self.request, data=data, src=self.request.validated['tender_src'])
        self.LOGGER.info('Updated tender {}'.format(tender.id),
                         extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_patch'}))
        return {'data': tender.serialize(tender.status)}


@opresource(name='TenderLimitedNegotiation',
            path='/tenders/{tender_id}',
            procurementMethodType='negotiation',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderNegotioationResource(TenderResource):
    """ Resource handler for Negotiation Tender """


@opresource(name='TenderLimitedNegotiationQuick',
            path='/tenders/{tender_id}',
            procurementMethodType='negotiation.quick',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderNegotioationQuickResource(TenderNegotioationResource):
    """ Resource handler for Negotiation Quick Tender """
