# -*- coding: utf-8 -*-
from datetime import timedelta
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    apply_patch,
    save_tender,
    opresource,
    json_view,
    context_unpack,
    APIResource
)
from openprocurement.api.validation import (
    validate_patch_award_data,
    validate_award_data,
)
from openprocurement.tender.openua.utils import calculate_business_date
from openprocurement.tender.openua.models import calculate_normalized_date


@opresource(name='Tender Limited Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender awards",
            procurementMethodType='reporting',
            )
class TenderAwardResource(APIResource):

    @json_view(permission='view_tender')
    def collection_get(self):
        """Tender Awards List

        Get Awards List
        ---------------

        Example request to get awards list:

        .. sourcecode:: http

            GET /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": [
                    {
                        "status": "active",
                        "suppliers": [
                            {
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
                            }
                        ],
                        "value": {
                            "amount": 489,
                            "currency": "UAH",
                            "valueAddedTaxIncluded": true
                        }
                    }
                ]
            }

        """
        return {'data': [i.serialize("view") for i in self.request.validated['tender'].awards]}

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_award_data,))
    def collection_post(self):
        """Accept or reject bidder application

        Creating new Award
        ------------------

        Example request to create award:

        .. sourcecode:: http

            POST /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        tender = self.request.validated['tender']
        if tender.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t create award in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        if tender.awards and tender.awards[-1].status in ['pending', 'active']:
            self.request.errors.add('body', 'data', 'Can\'t create new award while any ({}) award exists'.format(tender.awards[-1].status))
            self.request.errors.status = 403
            return
        award = self.request.validated['award']
        tender.awards.append(award)
        if save_tender(self.request):
            self.LOGGER.info('Created tender award {}'.format(award.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_create'}, {'award_id': award.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('Tender Awards', tender_id=tender.id, award_id=award['id'])
            return {'data': award.serialize("view")}

    @json_view(permission='view_tender')
    def get(self):
        """Retrieving the award

        Example request for retrieving the award:

        .. sourcecode:: http

            GET /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        return {'data': self.request.validated['award'].serialize("view")}

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_patch_award_data,))
    def patch(self):
        """Update of award

        Example request to change the award:

        .. sourcecode:: http

            PATCH /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
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
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 600,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        tender = self.request.validated['tender']
        if tender.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t update award in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return

        award = self.request.context
        award_status = award.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if award_status == 'pending' and award.status == 'active':
            tender.contracts.append(type(tender).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'date': get_now(),
                'value': award.value,
                'items': tender.items,
                'contractID': '{}-{}{}'.format(tender.tenderID, self.server_id, len(tender.contracts) + 1)}))
            # add_next_award(self.request)
        elif award_status == 'active' and award.status == 'cancelled':
            for i in tender.contracts:
                if i.awardID == award.id:
                    i.status = 'cancelled'
            # add_next_award(self.request)
        elif award_status == 'pending' and award.status == 'unsuccessful':
            pass
            # add_next_award(self.request)
        elif award_status != award.status:
            self.request.errors.add('body', 'data', 'Can\'t update award in current ({}) status'.format(award_status))
            self.request.errors.status = 403
            return
        elif award_status != 'pending':
            self.request.errors.add('body', 'data', 'Can\'t update award in current ({}) status'.format(award_status))
            self.request.errors.status = 403
            return

        if save_tender(self.request):
            self.LOGGER.info('Updated tender award {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_patch'}, {'TENDER_REV': tender.rev}))
            return {'data': award.serialize("view")}


@opresource(name='Tender Negotiation Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender awards",
            procurementMethodType='negotiation')
class TenderNegotiationAwardResource(TenderAwardResource):
    """ Tender Negotiation Award Resource """
    stand_still_delta = timedelta(days=10)

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_award_data,))
    def collection_post(self):
        """Accept or reject bidder application

        Creating new Award
        ------------------

        Example request to create award:

        .. sourcecode:: http

            POST /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        tender = self.request.validated['tender']
        if tender.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t create award in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        if tender.awards and tender.awards[-1].status in ['pending', 'active']:
            self.request.errors.add('body', 'data', 'Can\'t create new award while any ({}) award exists'.format(tender.awards[-1].status))
            self.request.errors.status = 403
            return
        award = self.request.validated['award']
        if award.status == "active" and not award.qualified:
            self.request.errors.add('body', 'data', 'Can\'t create new award in active status and not qualified')
            self.request.errors.status = 403
            return
        award.complaintPeriod = {'startDate': get_now().isoformat()}
        tender.awards.append(award)
        if save_tender(self.request):
            self.LOGGER.info('Created tender award {}'.format(award.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_create'}, {'award_id': award.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('Tender Awards', tender_id=tender.id, award_id=award['id'])
            return {'data': award.serialize("view")}

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_patch_award_data,))
    def patch(self):
        """Update of award

        Example request to change the award:

        .. sourcecode:: http

            PATCH /tenders/4879d3f8ee2443169b5fbbc9f89fa607/awards/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
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
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 600,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        tender = self.request.validated['tender']
        if tender.status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t update award in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return

        award = self.request.context
        award_status = award.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if award.status == "active" and not award.qualified:
            self.request.errors.add('body', 'data', 'Can\'t update award to active status with not qualified')
            self.request.errors.status = 403
            return
        if award_status == 'pending' and award.status == 'active':
            normalized_end = calculate_normalized_date(get_now(), tender, True)
            award.complaintPeriod.endDate = calculate_business_date(normalized_end, self.stand_still_delta, tender)
            tender.contracts.append(type(tender).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'date': get_now(),
                'value': award.value,
                'items': tender.items,
                'contractID': '{}-{}{}'.format(tender.tenderID, self.server_id, len(tender.contracts) + 1)}))
            # add_next_award(self.request)
        elif award_status == 'active' and award.status == 'cancelled' and any([i.status == 'satisfied' for i in award.complaints]):
            now = get_now()
            for i in tender.awards:
                if i.complaintPeriod.endDate > now:
                    i.complaintPeriod.endDate = now
                i.status = 'cancelled'
            for i in tender.contracts:
                i.status = 'cancelled'
        elif award_status == 'active' and award.status == 'cancelled':
            now = get_now()
            if award.complaintPeriod.endDate > now:
                award.complaintPeriod.endDate = now
            for i in tender.contracts:
                if i.awardID == award.id:
                    i.status = 'cancelled'
            # add_next_award(self.request)
        elif award_status == 'pending' and award.status == 'unsuccessful':
            award.complaintPeriod.endDate = get_now()
            # add_next_award(self.request)
        elif award_status == 'unsuccessful' and award.status == 'cancelled' and any([i.status == 'satisfied' for i in award.complaints]):
            now = get_now()
            for i in tender.awards:
                if i.complaintPeriod.endDate > now:
                    i.complaintPeriod.endDate = now
                i.status = 'cancelled'
            for i in tender.contracts:
                i.status = 'cancelled'
        elif award_status != award.status:
            self.request.errors.add('body', 'data', 'Can\'t update award in current ({}) status'.format(award_status))
            self.request.errors.status = 403
            return
        elif self.request.authenticated_role != 'Administrator' and award_status != 'pending':
            self.request.errors.add('body', 'data', 'Can\'t update award in current ({}) status'.format(award_status))
            self.request.errors.status = 403
            return

        if save_tender(self.request):
            self.LOGGER.info('Updated tender award {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_patch'}, {'TENDER_REV': tender.rev}))
            return {'data': award.serialize("view")}


@opresource(name='Tender Negotiation Quick Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender awards",
            procurementMethodType='negotiation.quick')
class TenderNegotiationQuickAwardResource(TenderNegotiationAwardResource):
    """ Tender Negotiation Quick Award Resource """
    stand_still_delta = timedelta(days=5)
