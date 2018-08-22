# -*- coding: utf-8 -*-
from datetime import timedelta
from openprocurement.api.utils import context_unpack, json_view, APIResource, get_now

from openprocurement.tender.core.utils import (
    save_tender, optendersresource, apply_patch
)
from openprocurement.tender.cfaselectionua.constants import ENQUIRY_PERIOD
from openprocurement.tender.cfaselectionua.validation import (
    validate_patch_tender_in_draft_pending,
    validate_tender_status_update_in_terminated_status,
)
from openprocurement.tender.cfaselectionua.utils import (
    check_status, check_period_and_items
)

from openprocurement.tender.core.validation import (
    validate_patch_tender_data
)
from openprocurement.tender.core.views.tender import TendersResource as APIResources

from openprocurement.tender.cfaselectionua.utils import check_status
from openprocurement.tender.cfaselectionua.validation import validate_patch_tender_data


@optendersresource(name='closeFrameworkAgreementSelectionUA:Tender',
                   path='/tenders/{tender_id}',
                   procurementMethodType='closeFrameworkAgreementSelectionUA',
                   description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderResource(APIResource):

    @json_view(permission='view_tender')
    def get(self):
        """Tender Read

        Get Tender
        ----------

        Example request to get tender:

        .. sourcecode:: http

            GET /tenders/64e93250be76435397e8c992ed4214d1 HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "64e93250be76435397e8c992ed4214d1",
                    "tenderID": "UA-64e93250be76435397e8c992ed4214d1",
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "procuringEntity": {
                        "id": {
                            "name": "Державне управління справами",
                            "scheme": "https://ns.openprocurement.org/ua/edrpou",
                            "uid": "00037256",
                            "uri": "http://www.dus.gov.ua/"
                        },
                        "address": {
                            "countryName": "Україна",
                            "postalCode": "01220",
                            "region": "м. Київ",
                            "locality": "м. Київ",
                            "streetAddress": "вул. Банкова, 11, корпус 1"
                        }
                    },
                    "value": {
                        "amount": 500,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    },
                    "itemsToBeProcured": [
                        {
                            "description": "футляри до державних нагород",
                            "primaryClassification": {
                                "scheme": "CPV",
                                "id": "44617100-9",
                                "description": "Cartons"
                            },
                            "additionalClassification": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "17.21.1",
                                    "description": "папір і картон гофровані, паперова й картонна тара"
                                }
                            ],
                            "unitOfMeasure": "item",
                            "quantity": 5
                        }
                    ],
                    "enquiryPeriod": {
                        "endDate": "2014-10-31T00:00:00"
                    },
                    "tenderPeriod": {
                        "startDate": "2014-11-03T00:00:00",
                        "endDate": "2014-11-06T10:00:00"
                    },
                    "awardPeriod": {
                        "endDate": "2014-11-13T00:00:00"
                    },
                    "deliveryDate": {
                        "endDate": "2014-11-20T00:00:00"
                    },
                    "minimalStep": {
                        "amount": 35,
                        "currency": "UAH"
                    }
                }
            }

        """
        if self.request.authenticated_role == 'chronograph':
            tender_data = self.context.serialize('chronograph_view')
        else:
            tender_data = self.context.serialize(self.context.status)
        return {'data': tender_data}

    @json_view(content_type="application/json",
               validators=(validate_patch_tender_data,
                           validate_tender_status_update_in_terminated_status,
                           validate_patch_tender_in_draft_pending),
               permission='edit_tender')
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
        if self.request.authenticated_role == 'chronograph':
            apply_patch(self.request, save=False, src=self.request.validated['tender_src'])
            check_status(self.request)
            save_tender(self.request)
        elif self.request.authenticated_role == 'agreement_selection':
            check_period_and_items(self.request, tender)
            tender.enquiryPeriod.startDate = get_now()
            tender.enquiryPeriod.endDate = tender.enquiryPeriod.startDate + ENQUIRY_PERIOD
            tender.tenderPeriod.startDate = tender.enquiryPeriod.endDate
            apply_patch(self.request, src=self.request.validated['tender_src'])
        else:
            apply_patch(self.request, src=self.request.validated['tender_src'])
        self.LOGGER.info('Updated tender {}'.format(tender.id),
                    extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_patch'}))
        return {'data': tender.serialize(tender.status)}
