# -*- coding: utf-8 -*-
from openprocurement.api.views.tender import TenderResource
from openprocurement.tender.openua.validation import validate_patch_tender_ua_data
from openprocurement.tender.openuadefense.utils import calculate_business_date, check_status
from openprocurement.api.utils import (
    save_tender,
    apply_patch,
    opresource,
    json_view,
    context_unpack,
)
from openprocurement.api.models import get_now
from openprocurement.tender.openuadefense.models import TENDERING_EXTRA_PERIOD


@opresource(name='Tender UA.defense',
            path='/tenders/{tender_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderUAResource(TenderResource):
    """ Resource handler for TenderUA """

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

        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            if 'tenderPeriod' in data and 'endDate' in data['tenderPeriod']:
                self.request.validated['tender'].tenderPeriod.import_data(data['tenderPeriod'])
                if calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, tender, True) > self.request.validated['tender'].tenderPeriod.endDate:
                    self.request.errors.add('body', 'data', 'tenderPeriod should be extended by {0.days} working days'.format(TENDERING_EXTRA_PERIOD))
                    self.request.errors.status = 403
                    return
                self.request.validated['tender'].initialize()
                self.request.validated['data']["enquiryPeriod"] = self.request.validated['tender'].enquiryPeriod.serialize()

        apply_patch(self.request, save=False, src=self.request.validated['tender_src'])
        if self.request.authenticated_role == 'chronograph':
            check_status(self.request)
        elif self.request.authenticated_role == 'tender_owner' and tender.status == 'active.tendering':
            # invalidate bids on tender change
            tender.invalidate_bids_data()
        save_tender(self.request)
        self.LOGGER.info('Updated tender {}'.format(tender.id),
                    extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_patch'}))
        return {'data': tender.serialize(tender.status)}
