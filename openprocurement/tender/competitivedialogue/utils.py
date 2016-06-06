# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.tender.openua.utils import calculate_business_date
from openprocurement.tender.openua.models import TENDERING_EXTRA_PERIOD
from openprocurement.api.models import get_now
from openprocurement.api.utils import save_tender, apply_patch, opresource, json_view, context_unpack
from openprocurement.tender.openeu.utils import check_status, all_bids_are_reviewed
from openprocurement.tender.openeu.models import PREQUALIFICATION_COMPLAINT_STAND_STILL as COMPLAINT_STAND_STILL
from openprocurement.tender.openua.utils import BLOCK_COMPLAINT_STATUS, check_complaint_status, add_next_award
from openprocurement.tender.openeu.utils import check_initial_bids_count, prepare_qualifications


LOGGER = getLogger(__name__)


# TODO: move to openprocurement.api (utils.py) and use in openua plugin
def patch_ua(self):
    """Tender Edit for UA procedure (partial)

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
    if self.request.authenticated_role != 'Administrator' and tender.status in ['complete', 'unsuccessful',
                                                                                'cancelled']:
        self.request.errors.add('body', 'data', 'Can\'t update tender in current ({}) status'.format(tender.status))
        self.request.errors.status = 403
        return
    data = self.request.validated['data']

    if self.request.authenticated_role == 'tender_owner' \
            and self.request.validated['tender_status'] == 'active.tendering':
        if 'tenderPeriod' in data and 'endDate' in data['tenderPeriod']:
            self.request.validated['tender'].tenderPeriod.import_data(data['tenderPeriod'])
            if calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, context=tender) > self.request.validated['tender'].tenderPeriod.endDate:
                self.request.errors.add('body', 'data', 'tenderPeriod should be extended by {0.days} days'.format(
                    TENDERING_EXTRA_PERIOD))
                self.request.errors.status = 403
                return
            self.request.validated['tender'].initialize()
            self.request.validated['data']["enquiryPeriod"] = self.request.validated[
                'tender'].enquiryPeriod.serialize()

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


# TODO: move to openprocurement.api (utils.py) and use in openeu plugin
def patch_eu(self):
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
    if self.request.authenticated_role != 'Administrator' and tender.status in ['complete', 'unsuccessful',
                                                                                'cancelled']:
        self.request.errors.add('body', 'data', 'Can\'t update tender in current ({}) status'.format(tender.status))
        self.request.errors.status = 403
        return
    data = self.request.validated['data']
    if self.request.authenticated_role == 'tender_owner' and 'status' in data and \
            data['status'] not in ['active.pre-qualification.stand-still', tender.status]:
        self.request.errors.add('body', 'data', 'Can\'t update tender status')
        self.request.errors.status = 403
        return

    if self.request.authenticated_role == 'tender_owner' \
            and self.request.validated['tender_status'] == 'active.tendering':
        if 'tenderPeriod' in data and 'endDate' in data['tenderPeriod']:
            self.request.validated['tender'].tenderPeriod.import_data(data['tenderPeriod'])
            if calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, self.request.validated['tender']) > \
                    self.request.validated['tender'].tenderPeriod.endDate:
                self.request.errors.add('body', 'data', 'tenderPeriod should be extended by {0.days} days'.format(
                    TENDERING_EXTRA_PERIOD))
                self.request.errors.status = 403
                return
            self.request.validated['tender'].initialize()
            self.request.validated['data']["enquiryPeriod"] = self.request.validated[
                'tender'].enquiryPeriod.serialize()

    apply_patch(self.request, save=False, src=self.request.validated['tender_src'])
    if self.request.authenticated_role == 'chronograph':
        check_status(self.request)
    elif self.request.authenticated_role == 'tender_owner' and tender.status == 'active.tendering':
        tender.invalidate_bids_data()
    elif self.request.authenticated_role == 'tender_owner' and \
            self.request.validated['tender_status'] == 'active.pre-qualification' and \
            tender.status == "active.pre-qualification.stand-still":
        if all_bids_are_reviewed(self.request):
            tender.qualificationPeriod.endDate = calculate_business_date(get_now(), COMPLAINT_STAND_STILL,
                                                                         self.request.validated['tender'])
            tender.check_auction_time()
        else:
            self.request.errors.add('body', 'data', 'Can\'t switch to \'active.pre-qualification.stand-still\' while not all bids are qualified')
            self.request.errors.status = 403
            return

    save_tender(self.request)
    self.LOGGER.info('Updated tender {}'.format(tender.id),
                     extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_patch'}))
    return {'data': tender.serialize(tender.status)}


# TODO: move to openprocurement.tender.openua (utils.py) and use in openua plugin
def cancellation_ua_cancel_lot(self, cancellation=None):
    if not cancellation:
        cancellation = self.context
    tender = self.request.validated['tender']
    [setattr(i, 'status', 'cancelled') for i in tender.lots if i.id == cancellation.relatedLot]
    statuses = set([lot.status for lot in tender.lots])
    if statuses == set(['cancelled']):
        self.cancel_tender()
    elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
        tender.status = 'unsuccessful'
    elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
        tender.status = 'complete'
    if tender.status == 'active.auction' and all([i.auctionPeriod and i.auctionPeriod.endDate
                                                  for i in self.request.validated['tender'].lot
                                                  if i.status == 'active']):
        add_next_award(self.request)


# TODO: move to openprocurement.tender.openeu (utils.py) and use in openeu plugin
def cancellation_eu_cancel_lot(self, cancellation=None):
    if not cancellation:
        cancellation = self.context
    tender = self.request.validated['tender']
    [setattr(i, 'status', 'cancelled') for i in tender.lots if i.id == cancellation.relatedLot]
    cancelled_lots = [i.id for i in tender.lots if i.status == 'cancelled']
    cancelled_items = [i.id for i in tender.items if i.relatedLot in cancelled_lots]
    cancelled_features = [
        i.code
        for i in (tender.features or [])
        if i.featureOf == 'lot' and i.relatedItem in cancelled_lots or i.featureOf == 'item' and i.relatedItem in cancelled_items
    ]
    if tender.status in ['active.tendering', 'active.pre-qualification',
                         'active.pre-qualification.stand-still', 'active.auction']:
        for bid in tender.bids:
            if tender.status == "active.tendering":
                bid.documents = [i for i in bid.documents
                                 if i.documentOf != 'lot' or i.relatedItem not in cancelled_lots]
            bid.financialDocuments = [i for i in bid.financialDocuments
                                      if i.documentOf != 'lot' or i.relatedItem not in cancelled_lots]
            bid.eligibilityDocuments = [i for i in bid.eligibilityDocuments
                                        if i.documentOf != 'lot' or i.relatedItem not in cancelled_lots]
            bid.qualificationDocuments = [i for i in bid.qualificationDocuments
                                          if i.documentOf != 'lot' or i.relatedItem not in cancelled_lots]
            bid.parameters = [i for i in bid.parameters if i.code not in cancelled_features]
            bid.lotValues = [i for i in bid.lotValues if i.relatedLot not in cancelled_lots]
            if not bid.lotValues:
                bid.status = 'invalid'
    for qualification in tender.qualifications:
        if qualification.lotID in cancelled_lots:
            qualification.status = 'cancelled'
    statuses = set([lot.status for lot in tender.lots])
    if statuses == set(['cancelled']):
        self.cancel_tender()
    elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
        tender.status = 'unsuccessful'
    elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
        tender.status = 'complete'
    if tender.status == 'active.auction' and all([i.auctionPeriod and i.auctionPeriod.endDate
                                                  for i in self.request.validated['tender'].lots
                                                  if i.status == 'active']):
        add_next_award(self.request)


# TODO: move to openprocurement.tender.openeu (utils.py) and use in openeu plugin
def cancellation_eu_cancel_tender(self):
    tender = self.request.validated['tender']
    if tender.status in ['active.tendering']:
        tender.bids = []
    if tender.status in ['active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction']:
        [setattr(i, 'status', 'invalid') for i in tender.bids]
    tender.status = 'cancelled'


# TODO: move to openprocurement.tender.openeu (utils.py) and use in openeu plugin
def bid_collection_get_eu(self):
    """Bids Listing

    Get Bids List
    -------------

    Example request to get bids list:

    .. sourcecode:: http

        GET /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids HTTP/1.1
        Host: example.com
        Accept: application/json

    This is what one should expect in response:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "data": [
                {
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            ]
        }

    """
    tender = self.request.validated['tender']
    if self.request.validated['tender_status'] == 'active.tendering':
        self.request.errors.add('body', 'data', 'Can\'t view bids in current ({}) tender status'.format(
            self.request.validated['tender_status']))
        self.request.errors.status = 403
        return
    return {'data': [i.serialize(self.request.validated['tender_status']) for i in tender.bids]}


# TODO: move to openprocurement.tender.openeu (utils.py) and use in openeu plugin
def bid_get_eu(self):
    """Retrieving the proposal

    Example request for retrieving the proposal:

    .. sourcecode:: http

        GET /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
        Host: example.com
        Accept: application/json

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
    if self.request.authenticated_role == 'bid_owner':
        return {'data': self.request.context.serialize('view')}
    if self.request.validated['tender_status'] == 'active.tendering':
        self.request.errors.add('body', 'data', 'Can\'t view bid in current ({}) tender status'.format(
            self.request.validated['tender_status']))
        self.request.errors.status = 403
        return
    return {'data': self.request.context.serialize(self.request.validated['tender_status'])}


# TODO: move to openprocurement.tender.openeu (utils.py) and use in openeu plugin
def bid_patch_eu(self):
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
    if self.request.authenticated_role != 'Administrator' \
            and self.request.validated['tender_status'] != 'active.tendering':
        self.request.errors.add('body', 'data', 'Can\'t update bid in current ({}) tender status'.format(
            self.request.validated['tender_status']))
        self.request.errors.status = 403
        return
    tender = self.request.validated['tender']
    if self.request.authenticated_role != 'Administrator' and (tender.tenderPeriod.startDate
                                                               and get_now() < tender.tenderPeriod.startDate
                                                               or get_now() > tender.tenderPeriod.endDate):
        self.request.errors.add('body', 'data', 'Bid can be updated only during the tendering period: from ({}) to ({}).'.format(
            tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(),
            tender.tenderPeriod.endDate.isoformat()))
        self.request.errors.status = 403
        return
    if self.request.authenticated_role != 'Administrator':
        bid_status_to = self.request.validated['data'].get("status", self.request.context.status)
        if bid_status_to != 'pending':
            self.request.errors.add('body', 'bid', 'Can\'t update bid to ({}) status'.format(bid_status_to))
            self.request.errors.status = 403
            return
    value = self.request.validated['data'].get("value") and self.request.validated['data']["value"].get("amount")
    if value and value != self.request.context.get("value", {}).get("amount"):
        self.request.validated['data']['date'] = get_now().isoformat()
    if self.request.context.lotValues:
        lotValues = dict([(i.relatedLot, i.value.amount) for i in self.request.context.lotValues])
        for lotvalue in self.request.validated['data'].get("lotValues", []):
            if lotvalue['relatedLot'] in lotValues \
                    and lotvalue.get("value", {}).get("amount") != lotValues[lotvalue['relatedLot']]:
                lotvalue['date'] = get_now().isoformat()
    self.request.validated['tender'].modified = False
    if apply_patch(self.request, src=self.request.context.serialize()):
        self.LOGGER.info('Updated tender bid {}'.format(self.request.context.id),
                         extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_bid_patch'}))
        return {'data': self.request.context.serialize("view")}


# TODO: move to openprocurement.tender.openeu (utils.py) and use in openeu plugin
def bid_delete_eu(self):
    """Cancelling the proposal

            Example request for cancelling the proposal:

            .. sourcecode:: http

                DELETE /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
                Host: example.com
                Accept: application/json

            """
    bid = self.request.context
    if self.request.validated['tender_status'] != 'active.tendering':
        self.request.errors.add('body', 'data', 'Can\'t delete bid in current ({}) tender status'.format(
            self.request.validated['tender_status']))
        self.request.errors.status = 403
        return
    tender = self.request.validated['tender']
    if tender.tenderPeriod.startDate and get_now() < tender.tenderPeriod.startDate or get_now() > tender.tenderPeriod.endDate:
        self.request.errors.add('body', 'data',
                                'Bid can be deleted only during the tendering period: from ({}) to ({}).'.format(
                                    tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(),
                                    tender.tenderPeriod.endDate.isoformat()))
        self.request.errors.status = 403
        return
    bid.status = 'deleted'
    if tender.lots:
        bid.lotValues = []
    self.request.validated['tender'].modified = False
    if save_tender(self.request):
        res = bid.serialize("view")
        self.LOGGER.info('Deleted tender bid {}'.format(self.request.context.id),
                         extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_bid_delete'}))
        return {'data': res}


def check_status(request):
    tender = request.validated['tender']
    now = get_now()

    if tender.status == 'active.tendering' and tender.tenderPeriod.endDate <= now and \
            not any([i.status in BLOCK_COMPLAINT_STATUS for i in tender.complaints]) and \
            not any([i.id for i in tender.questions if not i.answer]):
        for complaint in tender.complaints:
            check_complaint_status(request, complaint)
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.pre-qualification'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.pre-qualification'}))
        tender.status = 'active.pre-qualification'
        tender.qualificationPeriod = type(tender).qualificationPeriod({'startDate': now})
        check_initial_bids_count(request)
        prepare_qualifications(request)
        return

    elif tender.status == 'active.pre-qualification.stand-still' and tender.qualificationPeriod and tender.qualificationPeriod.endDate <= now and not any([
        i.status in BLOCK_COMPLAINT_STATUS
        for q in tender.qualifications
        for i in q.complaints
    ]):
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active.auction'}))
        tender.status = 'active.auction'
        check_initial_bids_count(request)
        return
