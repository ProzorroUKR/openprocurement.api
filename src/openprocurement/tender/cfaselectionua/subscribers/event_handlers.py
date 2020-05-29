# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.tender.core.models import PeriodEndRequired
from openprocurement.tender.cfaselectionua.adapters.configurator import TenderCfaSelectionUAConfigurator
from openprocurement.tender.core.utils import calculate_tender_business_date


@subscriber(TenderInitializeEvent, procurementMethodType="closeFrameworkAgreementSelectionUA")
def tender_init_handler(event):
    """ initialization handler for closeFrameworkAgreementSelectionUA tenders """
    tender = event.tender
    default_status = type(tender).fields["status"].default
    if tender.status != default_status:
        raise Exception("Allow create tender only in ({default_status}) status".format(default_status=default_status))
    if not tender.enquiryPeriod:
        tender.enquiryPeriod = PeriodEndRequired()
        tender.enquiryPeriod["__parent__"] = tender
    if not tender.enquiryPeriod.startDate:
        tender.enquiryPeriod.startDate = get_now()
    if not tender.enquiryPeriod.endDate:
        tender.enquiryPeriod.endDate = calculate_tender_business_date(
            tender.enquiryPeriod.startDate,
            TenderCfaSelectionUAConfigurator.enquiry_period,
            tender
        )
    if not tender.tenderPeriod:
        tender.tenderPeriod = PeriodEndRequired()
        tender.tenderPeriod["__parent__"] = tender
    if not tender.tenderPeriod.startDate:
        tender.tenderPeriod.startDate = tender.enquiryPeriod.endDate
    if not tender.tenderPeriod.endDate:
        tender.tenderPeriod.endDate = calculate_tender_business_date(
            tender.tenderPeriod.startDate,
            TenderCfaSelectionUAConfigurator.tender_period,
            tender
        )
    now = get_now()
    tender.date = now
    if tender.lots:
        for lot in tender.lots:
            lot.date = now
