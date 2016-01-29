# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.views.tender import TenderResource
from openprocurement.tender.openeu.utils import check_status, all_bids_are_reviewed
from openprocurement.api.utils import (
    save_tender,
    apply_patch,
    opresource,
    json_view,
    context_unpack,
)

LOGGER = getLogger(__name__)



from openprocurement.tender.openua.validation import validate_patch_tender_ua_data

@opresource(name='Tender EU',
            path='/tenders/{tender_id}',
            procurementMethodType='aboveThresholdEU',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderEUResource(TenderResource):
    """ Resource handler for TenderEU """

    @json_view(content_type="application/json", validators=(validate_patch_tender_ua_data, ), permission='edit_tender')
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
        tender = self.context
        if self.request.authenticated_role != 'Administrator' and tender.status in ['complete', 'unsuccessful', 'cancelled']:
            self.request.errors.add('body', 'data', 'Can\'t update tender in current ({}) status'.format(tender.status))
            self.request.errors.status = 403
            return
        data = self.request.validated['data']
        if self.request.authenticated_role == 'tender_owner' and 'status' in data and data['status'] not in ['active.pre-qualification.stand-still', tender.status]:
            self.request.errors.add('body', 'data', 'Can\'t update tender status')
            self.request.errors.status = 403
            return

        apply_patch(self.request, save=False, src=self.request.validated['tender_src'])
        if self.request.authenticated_role == 'chronograph':
            check_status(self.request)
        elif self.request.authenticated_role == 'tender_owner' and tender.status == 'active.tendering':
            tender.invalidate_bids_data()
        elif tender.status == "active.pre-qualification.stand-still":
            if all_bids_are_reviewed(self.request):
                if sum([1 for bid in tender.bids if bid.status == 'active']) < 2:
                    tender.status = 'unsuccessful'

        save_tender(self.request)
        LOGGER.info('Updated tender {}'.format(tender.id),
                    extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_patch'}))
        return {'data': tender.serialize(tender.status)}