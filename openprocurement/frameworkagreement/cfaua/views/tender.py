# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    get_now,
    raise_operation_error,
    generate_id,
    set_ownership,
)
from openprocurement.tender.core.utils import (
    optendersresource,
    apply_patch,
    save_tender,
    calculate_business_date,
    generate_tender_id,
)
from openprocurement.tender.core.validation import (
    validate_tender_period_extension,
    validate_tender_status_update_in_terminated_status,
    validate_tender_data,
)
from openprocurement.tender.core.views.tender import TendersResource
from openprocurement.tender.belowthreshold.views.tender import TenderResource
from openprocurement.frameworkagreement.cfaua.utils import (
    check_status,
    all_bids_are_reviewed,
    all_awards_are_reviewed
)
from openprocurement.tender.openua.utils import calculate_normalized_date
from openprocurement.tender.openua.validation import validate_patch_tender_ua_data
from openprocurement.frameworkagreement.cfaua.constants import (
    QUALIFICATION_COMPLAINT_STAND_STILL as COMPLAINT_STAND_STILL
)
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.frameworkagreement.cfaua.validation import (
    validate_tender_lots_count,
    validate_tender_status_update
)


@optendersresource(name='closeFrameworkAgreementUA:Tender',
                   path='/tenders/{tender_id}',
                   procurementMethodType='closeFrameworkAgreementUA',
                   description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderEUResource(TenderResource):
    """ Resource handler for TenderEU """

    @json_view(content_type="application/json",
               validators=(validate_tender_lots_count,
                           validate_patch_tender_ua_data,
                           validate_tender_status_update_in_terminated_status,
                           validate_tender_status_update,),
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
        data = self.request.validated['data']
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            if 'tenderPeriod' in data and 'endDate' in data['tenderPeriod']:
                self.request.validated['tender'].tenderPeriod.import_data(data['tenderPeriod'])
                validate_tender_period_extension(self.request)
                self.request.registry.notify(TenderInitializeEvent(self.request.validated['tender']))
                self.request.validated['data']["enquiryPeriod"] = self.request.validated['tender'].enquiryPeriod.serialize()

        apply_patch(self.request, save=False, src=self.request.validated['tender_src'])
        if self.request.authenticated_role == 'chronograph':
            check_status(self.request)
        elif self.request.authenticated_role == 'tender_owner' and tender.status == 'active.tendering':
            tender.invalidate_bids_data()
        elif self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.pre-qualification' and tender.status == "active.pre-qualification.stand-still":
            active_lots = [lot.id for lot in tender.lots if lot.status == 'active'] if tender.lots else [None]
            if any([i['status'] in self.request.validated['tender'].block_complaint_status for q in self.request.validated['tender']['qualifications'] for i in q['complaints'] if q['lotID'] in active_lots]):
                raise_operation_error(self.request, 'Can\'t switch to \'active.pre-qualification.stand-still\' before resolve all complaints')
            if all_bids_are_reviewed(self.request):
                normalized_date = calculate_normalized_date(get_now(), tender, True)
                tender.qualificationPeriod.endDate = calculate_business_date(normalized_date, COMPLAINT_STAND_STILL, self.request.validated['tender'])
                tender.check_auction_time()
            else:
                raise_operation_error(self.request, 'Can\'t switch to \'active.pre-qualification.stand-still\' while not all bids are qualified')
        elif self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.qualification' and tender.status == "active.qualification.stand-still":
            if all_awards_are_reviewed(self.request):
                normalized_date = calculate_normalized_date(get_now(), tender, True)
                tender.awardPeriod.endDate = calculate_business_date(normalized_date, COMPLAINT_STAND_STILL, self.request.validated['tender'])
            else:
                raise_operation_error(self.request, 'Can\'t switch to \'active.qualification.stand-still\' while not all awards are qualified')

        save_tender(self.request)
        self.LOGGER.info('Updated tender {}'.format(tender.id),
                         extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_patch'}))
        return {'data': tender.serialize(tender.status)}


@optendersresource(name='closeFrameworkAgreementUA:Tenders',
                   path='/tenders',
                   description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TendersEUResource(TendersResource):
    @json_view(content_type="application/json",
               permission='create_tender',
               validators=(validate_tender_lots_count, validate_tender_data,))
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
                             extra=context_unpack(self.request,
                                                  {'MESSAGE_ID': 'tender_create'},
                                                  {'tender_id': tender_id, 'tenderID': tender.tenderID}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = \
                self.request.route_url('{}:Tender'.format(tender.procurementMethodType), tender_id=tender_id)
            return {
                'data': tender.serialize(tender.status),
                'access': {
                    'token': tender.owner_token
                }
            }
