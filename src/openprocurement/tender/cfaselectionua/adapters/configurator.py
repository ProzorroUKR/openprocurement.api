# -*- coding: utf-8 -*-
from openprocurement.api.constants import TZ
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.cfaselectionua.constants import (
    STATUS4ROLE,
    MIN_PERIOD_UNTIL_AGREEMENT_END,
    MIN_ACTIVE_CONTRACTS,
    ENQUIRY_PERIOD,
    TENDERING_DURATION,
    MINIMAL_STEP_PERCENTAGE,
)


class TenderCfaSelectionUAConfigurator(TenderConfigurator):
    """ CFASelectionUA Tender configuration adapter """

    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            self.context, self.request = args
        else:
            self.context = args[0]

    name = "CFASelectionUA configurator"
    tz = TZ

    # Dictionary with allowed complaint statuses for operations for each role
    allowed_statuses_for_complaint_operations_for_roles = STATUS4ROLE

    # days before agreement period ends. Not allow create procedure if less than 7 days to end agreement
    agreement_expired_until = MIN_PERIOD_UNTIL_AGREEMENT_END
    # if bot patches tender with agreement with less than 3 active contracts, tender -> draft.unsuccessful
    min_active_contracts = MIN_ACTIVE_CONTRACTS
    enquiry_period = ENQUIRY_PERIOD  # patch tender by agreement bot, into active.enquiries
    tender_period = TENDERING_DURATION  # patch tender by agreement bot, into active.enquiries
    minimal_step_percentage = MINIMAL_STEP_PERCENTAGE
