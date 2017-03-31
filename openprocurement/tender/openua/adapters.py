# -*- coding: utf-8 -*-
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.openua.models import Tender
from openprocurement.tender.openua.constants import (
    TENDER_PERIOD, TENDERING_EXTRA_PERIOD, STATUS4ROLE
)


class TenderAboveThresholdUAConfigurator(TenderConfigurator):
    """ AboveThresholdUA Tender configuration adapter """

    name = "AboveThresholdUA Tender configurator"
    model = Tender

    # duration of tendering period. timedelta object.
    tendering_period_duration = TENDER_PERIOD

    # duration of tender period extension. timedelta object
    tendering_period_extra = TENDERING_EXTRA_PERIOD

    block_tender_complaint_status = model.block_tender_complaint_status
    block_complaint_status = model.block_complaint_status

    # Dictionary with allowed complaint statuses for operations for each role
    allowed_statuses_for_complaint_operations_for_roles = STATUS4ROLE
