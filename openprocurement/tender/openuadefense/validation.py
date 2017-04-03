# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, error_handler
from openprocurement.tender.core.utils import calculate_business_date


def validate_tender_period_extension_with_working_days(request):
    tender = request.context
    extra_period = request.content_configurator.tendering_period_extra
    if calculate_business_date(get_now(), extra_period, tender, True) > request.validated['tender'].tenderPeriod.endDate:
        request.errors.add('body', 'data', 'tenderPeriod should be extended by {0.days} working days'.format(extra_period))
        request.errors.status = 403
        raise error_handler(request.errors)

def validate_submit_claim_time(request):
    tender = request.context
    claim_submit_time = request.content_configurator.tender_claim_submit_time
    if get_now() > calculate_business_date(tender.tenderPeriod.endDate, -claim_submit_time, tender, True):
        request.errors.add('body', 'data', 'Can submit claim not later than {0.days} days before tenderPeriod end'.format(claim_submit_time))
        request.errors.status = 403
        raise error_handler(request.errors)
