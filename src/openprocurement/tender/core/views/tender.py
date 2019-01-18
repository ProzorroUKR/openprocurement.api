# -*- coding: utf-8 -*-
from functools import partial
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.design import (
    FIELDS,
    tenders_by_dateModified_view, tenders_real_by_dateModified_view,
    tenders_test_by_dateModified_view, tenders_by_local_seq_view,
    tenders_real_by_local_seq_view, tenders_test_by_local_seq_view,
)

from openprocurement.api.utils import (
    get_now, decrypt, encrypt, generate_id, json_view, set_ownership,
    context_unpack, APIResourceListing
)

from openprocurement.tender.core.utils import (
    save_tender, tender_serialize, optendersresource, generate_tender_id
)

from openprocurement.tender.core.validation import (
    validate_patch_tender_data, validate_tender_data,
)


VIEW_MAP = {
    u'': tenders_real_by_dateModified_view,
    u'test': tenders_test_by_dateModified_view,
    u'_all_': tenders_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    u'': tenders_real_by_local_seq_view,
    u'test': tenders_test_by_local_seq_view,
    u'_all_': tenders_by_local_seq_view,
}
FEED = {
    u'dateModified': VIEW_MAP,
    u'changes': CHANGES_VIEW_MAP,
}


@optendersresource(name='Tenders',
                   path='/tenders',
                   description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TendersResource(APIResourceListing):

    def __init__(self, request, context):
        super(TendersResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = tender_serialize
        self.object_name_for_listing = 'Tenders'
        self.log_message_id = 'tender_list_custom'

    @json_view(content_type="application/json", permission='create_tender', validators=(validate_tender_data,))
    def post(self):
        """This API request is targeted to creating new Tenders by procuring organizations.

        Creating new Tender
        -------------------

        Example request to create tender:

        .. sourcecode:: http

            POST /tenders HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
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

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Location: http://localhost/api/0.1/tenders/64e93250be76435397e8c992ed4214d1
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
        tender_id = generate_id()
        tender = self.request.validated['tender']
        tender.id = tender_id
        if not tender.get('tenderID'):
            tender.tenderID = generate_tender_id(get_now(), self.db, self.server_id)
        self.request.registry.notify(TenderInitializeEvent(tender))
        if self.request.json_body['data'].get('status') == 'draft':
            tender.status = 'draft'
        set_ownership(tender, self.request)  # rewrite as subscriber?
        self.request.validated['tender'] = tender
        self.request.validated['tender_src'] = {}
        if save_tender(self.request):
            self.LOGGER.info('Created tender {} ({})'.format(tender_id, tender.tenderID),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_create'}, {'tender_id': tender_id, 'tenderID': tender.tenderID}))
            self.request.response.status = 201
            self.request.response.headers[
                'Location'] = self.request.route_url('{}:Tender'.format(tender.procurementMethodType), tender_id=tender_id)
            return {
                'data': tender.serialize(tender.status),
                'access': {
                    'token': tender.owner_token
                }
            }


