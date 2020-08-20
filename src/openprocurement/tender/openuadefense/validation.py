# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.tender.openua.validation import (
    validate_tender_period_duration as validate_tender_period_duration_base,
)
from openprocurement.tender.openua.validation import (
    validate_complaint_post_review_date as validate_complaint_post_review_date_base
)
from openprocurement.tender.openuadefense.utils import calculate_tender_business_date, WORKING_DAYS


def validate_tender_period_extension_with_working_days(request):
    tender = request.validated["tender"]
    extra_period = request.content_configurator.tendering_period_extra
    extra_end_date = calculate_tender_business_date(get_now(), extra_period, tender, True)
    if tender.tenderPeriod.endDate < extra_end_date:
        raise_operation_error(request, "tenderPeriod should be extended by {0.days} working days".format(extra_period))


def validate_submit_claim_time(request):
    tender = request.validated["tender"]
    claim_submit_time = request.content_configurator.tender_claim_submit_time
    claim_end_date = calculate_tender_business_date(tender.tenderPeriod.endDate, -claim_submit_time, tender, True)
    if get_now() > claim_end_date:
        raise_operation_error(
            request,
            "Can submit claim not later than {duration.days} "
            "full business days before tenderPeriod ends".format(
                duration=claim_submit_time
            )
        )


def validate_update_tender(request):
    status = request.validated["tender_status"]
    if status == "active.tendering":
        validate_tender_period_extension_with_working_days(request)


def validate_complaint_post_review_date(request, calendar=WORKING_DAYS):
    validate_complaint_post_review_date_base(request, calendar=calendar)


def validate_tender_period_duration(data, period, duration, working_days=False, calendar=WORKING_DAYS):
    validate_tender_period_duration_base(
        data=data,
        period=period,
        duration=duration,
        working_days=working_days,
        calendar=calendar
    )
