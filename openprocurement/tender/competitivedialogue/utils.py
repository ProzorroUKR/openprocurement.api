# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.tender.openua.utils import calculate_business_date
from openprocurement.tender.openua.models import TENDERING_EXTRA_PERIOD
from openprocurement.api.models import get_now
from openprocurement.api.utils import save_tender, apply_patch, opresource, json_view, context_unpack, generate_id
from openprocurement.tender.openeu.utils import check_status, all_bids_are_reviewed
from openprocurement.tender.openeu.models import PREQUALIFICATION_COMPLAINT_STAND_STILL as COMPLAINT_STAND_STILL
from openprocurement.tender.openua.utils import BLOCK_COMPLAINT_STATUS, check_complaint_status, add_next_award
from openprocurement.tender.openeu.utils import check_initial_bids_count, prepare_qualifications


LOGGER = getLogger(__name__)


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
            data['status'] not in ['active.pre-qualification.stand-still', 'active.stage2.waiting', tender.status]:
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
        LOGGER.info('Switched tender {} to {}'.format(tender['id'], 'active.stage2.pending'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_tender_active_stage2_pending'}))
        tender.status = 'active.stage2.pending'
        return

def set_ownership(item):
    item.owner_token = generate_id()